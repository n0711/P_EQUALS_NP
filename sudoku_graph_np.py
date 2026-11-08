"""Generalized Sudoku as precolored graph coloring with an NP witness.

An abstract nondeterministic machine guesses one digit for each cell and
verifies the coloring in polynomial time. The runnable solver is an
ordinary deterministic backtracking algorithm with exponential worst case.

For box width b, the board has side n=b*b and n*n cells.
Empty clues are zero; digits are 1..n. No third-party dependencies.
"""
from __future__ import annotations

from itertools import combinations
from time import perf_counter


def _validate(box, grid):
    if not isinstance(box, int) or isinstance(box, bool) or box < 1:
        raise ValueError("box width must be a positive integer")
    side = box * box
    if len(grid) != side:
        raise ValueError("grid must have box**2 rows")
    flat = []
    for row in grid:
        if len(row) != side:
            raise ValueError("each row must have box**2 entries")
        for value in row:
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= side:
                raise ValueError("entries must be integers from zero to box**2")
            flat.append(value)
    return side, tuple(flat)


def sudoku_units(box):
    """Rows, columns and blocks, each a clique of length side."""
    if not isinstance(box, int) or isinstance(box, bool) or box < 1:
        raise ValueError("box must be positive")
    n = box * box
    rows = [tuple(r * n + c for c in range(n)) for r in range(n)]
    columns = [tuple(r * n + c for r in range(n)) for c in range(n)]
    blocks = [
        tuple((br * box + dr) * n + bc * box + dc
              for dr in range(box) for dc in range(box))
        for br in range(box) for bc in range(box)
    ]
    return tuple(rows + columns + blocks)


def sudoku_graph(box):
    """Return deterministic undirected edges and per-cell sorted peers."""
    units = sudoku_units(box)
    n = box * box
    edges = set()
    peers = [set() for _ in range(n * n)]
    for unit in units:
        for u, v in combinations(unit, 2):
            a, b = min(u, v), max(u, v)
            edges.add((a, b))
            peers[u].add(v)
            peers[v].add(u)
    return tuple(sorted(edges)), tuple(tuple(sorted(p)) for p in peers)


def verify_sudoku_certificate(box, givens, candidate):
    """Polynomial-time deterministic checker for an NP Sudoku witness.

    Input validation rejects malformed instances. A wrong or incomplete
    witness returns False. The verifier never searches for a witness.
    """
    side, original = _validate(box, givens)
    try:
        _, proposed = _validate(box, candidate)
    except (ValueError, TypeError):
        return False
    if any(not 1 <= d <= side for d in proposed):
        return False
    if any(g and g != w for g, w in zip(original, proposed)):
        return False
    edges, _ = sudoku_graph(box)
    return all(proposed[u] != proposed[v] for u, v in edges)


class _NodeLimit(Exception):
    pass


def solve_sudoku_graph(box, givens, *, max_nodes=None):
    """Exact deterministic propagation/backtracking coloring solver.

    Return (solution or None, statistics). A None result is UNSAT only
    when status == 'completed'; limit_nodes is UNDECIDED.
    """
    side, original = _validate(box, givens)
    if max_nodes is not None and (not isinstance(max_nodes, int)
                                   or isinstance(max_nodes, bool) or max_nodes < 1):
        raise ValueError("max_nodes must be positive or None")
    units = sudoku_units(box)
    _, peers = sudoku_graph(box)
    total = side * side
    full = (1 << side) - 1
    domains = tuple((1 << (g - 1)) if g else full for g in original)
    stats = {"status": "completed", "nodes": 0, "branches": 0,
             "dead_ends": 0, "unit_forcings": 0, "hidden_single_forcings": 0,
             "max_depth": 0, "elapsed_seconds": 0.0}
    started = perf_counter()

    def propagate(domains_in):
        d = list(domains_in)
        while True:
            modified = False
            # Arc filtering from assigned singletons.
            for u in range(total):
                mask = d[u]
                if mask == 0:
                    return None
                if mask.bit_count() != 1:
                    continue
                for v in peers[u]:
                    if d[v] & mask:
                        reduced = d[v] & ~mask
                        if not reduced:
                            return None
                        if reduced != d[v]:
                            d[v] = reduced
                            modified = True
                            stats["unit_forcings"] += 1
            # Each unit has exactly 'side' different cells/digits.
            # For every digit exactly one cell in the unit must support it.
            for unit in units:
                for value in range(side):
                    bit = 1 << value
                    choices = [u for u in unit if d[u] & bit]
                    if not choices:
                        return None
                    if len(choices) == 1:
                        u = choices[0]
                        if d[u] != bit:
                            d[u] = bit
                            modified = True
                            stats["hidden_single_forcings"] += 1
            if not modified:
                return tuple(d)

    def search(domains_in, depth):
        stats["nodes"] += 1
        if max_nodes is not None and stats["nodes"] > max_nodes:
            raise _NodeLimit
        stats["max_depth"] = max(stats["max_depth"], depth)
        d = propagate(domains_in)
        if d is None:
            stats["dead_ends"] += 1
            return None
        remaining = [i for i, mask in enumerate(d) if mask.bit_count() > 1]
        if not remaining:
            return tuple(mask.bit_length() for mask in d)
        # Minimum remaining values, then most unassigned peers, then index.
        pivot = min(
            remaining,
            key=lambda i: (d[i].bit_count(),
                           -sum(d[v].bit_count() > 1 for v in peers[i]), i),
        )
        for value in range(side):
            bit = 1 << value
            if not (d[pivot] & bit):
                continue
            stats["branches"] += 1
            child = list(d)
            child[pivot] = bit
            candidate = search(tuple(child), depth + 1)
            if candidate is not None:
                return candidate
        return None

    try:
        witness = search(domains, 0)
    except _NodeLimit:
        stats["status"] = "limit_nodes"
        witness = None
    stats["elapsed_seconds"] = perf_counter() - started
    if witness is None:
        return None, stats
    answer = [list(witness[r * side:(r + 1) * side]) for r in range(side)]
    assert verify_sudoku_certificate(box, givens, answer)
    return answer, stats


def patterned_solution(box):
    """Deterministic valid complete grid, for synthetic tests."""
    if not isinstance(box, int) or isinstance(box, bool) or box < 1:
        raise ValueError("box must be positive")
    n = box * box
    grid = [[(r * box + r // box + c) % n + 1
             for c in range(n)] for r in range(n)]
    assert verify_sudoku_certificate(box, [[0] * n for _ in range(n)], grid)
    return grid
