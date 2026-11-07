"""Exact SAT using primal-graph separators, conditioning and component caching.

A research implementation of established cutset/AND-OR search ideas, not P=NP.
No resource limit is imposed unless max_calls is explicitly supplied.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, product
from time import perf_counter

from sat import _validate, verify


class _CallLimit(Exception):
    pass


def _canonical(formula):
    return tuple(sorted(set(formula), key=lambda c: (len(c), c)))


def _restrict(formula, assignments):
    """Substitute assignments; clauses are canonicalized for exact memo keys."""
    result = []
    for clause in formula:
        if any((lit > 0) == assignments[abs(lit)]
               for lit in clause if abs(lit) in assignments):
            continue
        rest = tuple(lit for lit in clause if abs(lit) not in assignments)
        if not rest:
            return ((),)
        result.append(rest)
    return _canonical(result)


def _propagate(formula):
    forced = {}
    while True:
        if () in formula:
            return None, forced
        unit = next((clause[0] for clause in formula if len(clause) == 1), None)
        if unit is None:
            return formula, forced
        v, val = abs(unit), unit > 0
        if v in forced and forced[v] != val:
            return None, forced
        forced[v] = val
        formula = _restrict(formula, {v: val})


def _graph(formula):
    graph = {}
    for clause in formula:
        variables = sorted({abs(lit) for lit in clause})
        for v in variables:
            graph.setdefault(v, set())
        for i, v in enumerate(variables):
            for w in variables[i + 1:]:
                graph[v].add(w)
                graph[w].add(v)
    return graph


def _connected(graph, removed=()):
    remaining = set(graph).difference(removed)
    groups = []
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        group = {first}
        stack = [first]
        while stack:
            v = stack.pop()
            for w in graph[v] & remaining:
                remaining.remove(w)
                group.add(w)
                stack.append(w)
        groups.append(group)
    return groups


def _component_formulas(formula, graph):
    groups = _connected(graph)
    if len(groups) <= 1:
        return (formula,)
    owner = {v: i for i, group in enumerate(groups) for v in group}
    result = [[] for _ in groups]
    for clause in formula:
        result[owner[abs(clause[0])]].append(clause)
    return tuple(_canonical(group) for group in result)


def _separator(graph, max_size, pair_scan_limit):
    """Deterministic minimum-max-component separator; singles before pairs."""
    vertices = sorted(graph)
    for size in range(1, max_size + 1):
        if size == 2 and len(vertices) > pair_scan_limit:
            break  # heuristic work limit, not an incomplete SAT decision
        best = None
        for removal in combinations(vertices, size):
            pieces = _connected(graph, removal)
            if len(pieces) <= 1:
                continue
            score = (max(map(len, pieces)), -len(pieces), removal)
            if best is None or score < best[0]:
                best = score, removal
        if best is not None:
            return best[1]
    return ()


def graph_separator_sat(n, clauses, *, max_separator_size=2,
                        pair_scan_limit=36, max_calls=None):
    """Return (verified satisfying assignment or None, metrics).

    status=completed makes None a correct UNSAT answer; on limit_calls,
    None means UNDECIDED, never UNSAT. All decisions are deterministic.
    """
    original = _validate(n, clauses)
    if max_separator_size not in (0, 1, 2):
        raise ValueError("max_separator_size must be 0, 1 or 2")
    if not isinstance(pair_scan_limit, int) or pair_scan_limit < 2:
        raise ValueError("pair_scan_limit must be >= 2")
    if max_calls is not None and (not isinstance(max_calls, int) or max_calls < 1):
        raise ValueError("max_calls must be a positive integer or None")
    cleaned = []
    for clause in original:
        literals = set(clause)
        if any(-lit in literals for lit in literals):
            continue
        cleaned.append(tuple(sorted(literals, key=lambda lit: (abs(lit), lit))))
    formula = _canonical(cleaned)
    stats = {"status": "completed", "calls": 0, "cache_hits": 0,
             "unit_assignments": 0, "component_splits": 0,
             "separator_1_splits": 0, "separator_2_splits": 0,
             "fallback_branches": 0, "branch_trials": 0,
             "peak_graph_variables": 0, "memo_entries": 0,
             "elapsed_seconds": 0.0}
    memo = {}
    start = perf_counter()

    def solve(current):
        stats["calls"] += 1
        if max_calls is not None and stats["calls"] > max_calls:
            raise _CallLimit
        if current in memo:
            stats["cache_hits"] += 1
            return memo[current]
        reduced, forced = _propagate(current)
        stats["unit_assignments"] += len(forced)
        if reduced is None:
            memo[current] = None
            return None
        if not reduced:
            memo[current] = forced
            return forced
        graph = _graph(reduced)
        stats["peak_graph_variables"] = max(stats["peak_graph_variables"], len(graph))
        parts = _component_formulas(reduced, graph)
        if len(parts) > 1:
            stats["component_splits"] += 1
            merged = dict(forced)
            for part in parts:
                partial = solve(part)
                if partial is None:
                    memo[current] = None
                    return None
                merged.update(partial)
            memo[current] = merged
            return merged
        sep = _separator(graph, max_separator_size, pair_scan_limit)
        if sep:
            stats[f"separator_{len(sep)}_splits"] += 1
            trials = (dict(zip(sep, values)) for values in product((False, True), repeat=len(sep)))
        else:
            stats["fallback_branches"] += 1
            frequencies = Counter(abs(lit) for clause in reduced for lit in clause)
            pivot = min(frequencies, key=lambda v: (-frequencies[v], v))
            trials = ({pivot: val} for val in (False, True))
        for choice in trials:
            stats["branch_trials"] += 1
            child = solve(_restrict(reduced, choice))
            if child is not None:
                result = dict(forced)
                result.update(choice)
                result.update(child)
                memo[current] = result
                return result
        memo[current] = None
        return None

    try:
        solution = solve(formula)
    except _CallLimit:
        stats["status"] = "limit_calls"
        solution = None
    stats["memo_entries"] = len(memo)
    stats["elapsed_seconds"] = perf_counter() - start
    if solution is None:
        return None, stats
    model = [solution.get(v, False) for v in range(1, n + 1)]
    assert verify(n, original, model)
    return model, stats
