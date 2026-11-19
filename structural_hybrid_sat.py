"""Exact SAT portfolio using affine recognition, five-literal cores and separator search."""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from time import perf_counter

from sat import _validate, verify


def try_affine_sat(n, clauses):
    """Return (recognized, model_or_none, metrics).

    If recognized=False, model is None and no SAT decision was made.
    If recognized=True, None means UNSAT and otherwise model is verified.
    """
    return _affine_on_validated(n, _validate(n, clauses))


def _affine_on_validated(n, original):
    started = perf_counter()
    cleaned = set()
    for clause in original:
        lits = set(clause)
        if any(-lit in lits for lit in lits):
            continue  # tautological CNF clause
        cleaned.add(tuple(sorted(lits, key=lambda lit: abs(lit))))
    stats = {"recognized": False, "equations": 0, "rank": 0,
             "elapsed_seconds": 0.0}

    def finish(recognized, model):
        stats["recognized"] = recognized
        stats["elapsed_seconds"] = perf_counter() - started
        if recognized and model is not None:
            assert verify(n, original, model)
        return recognized, model, stats

    if () in cleaned:
        return finish(True, None)
    grouped = defaultdict(set)
    for clause in cleaned:
        variables = tuple(abs(lit) for lit in clause)
        if len(variables) > 3:
            return finish(False, None)
        forbidden = tuple(int(lit < 0) for lit in clause)
        grouped[variables].add(forbidden)

    equations = []
    for variables, forbidden_patterns in sorted(grouped.items()):
        width = len(variables)
        if len(forbidden_patterns) != (1 << (width - 1)):
            return finish(False, None)
        bad_parities = {sum(bits) % 2 for bits in forbidden_patterns}
        if len(bad_parities) != 1:
            return finish(False, None)
        rhs = 1 ^ next(iter(bad_parities))
        row = sum(1 << (v - 1) for v in variables)
        equations.append((row, rhs))

    stats["equations"] = len(equations)
    basis = {}  # pivot (highest indexed variable) -> (row, rhs)
    for row, rhs in equations:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (row, rhs)
                break
            other_row, other_rhs = basis[pivot]
            row ^= other_row
            rhs ^= other_rhs
        if not row and rhs:
            stats["rank"] = len(basis)
            return finish(True, None)

    stats["rank"] = len(basis)
    assignment_bits = 0
    # Every basis row has only lower-variable terms besides its pivot.
    for pivot in sorted(basis):
        row, rhs = basis[pivot]
        value = rhs ^ ((row & assignment_bits).bit_count() & 1)
        if value:
            assignment_bits |= 1 << pivot
    model = [bool((assignment_bits >> v) & 1) for v in range(n)]
    return finish(True, model)


def _five_literal_core(clauses):
    """Return five signed literals whose triples all occur in both polarities."""
    triples = set()
    for clause in clauses:
        literals = set(clause)
        if len(literals) == 3 and len({abs(v) for v in literals}) == 3:
            triples.add(tuple(sorted(literals, key=abs)))

    paired = {t for t in triples if tuple(-v for v in t) in triples}
    tails = defaultdict(list)
    for a, b, c in sorted(paired):
        if a > 0:  # A global sign flip gives an equivalent witness.
            tails[a, b].append(c)

    for (a, b), candidates in tails.items():
        for rest in combinations(sorted(candidates, key=abs), 3):
            core = (a, b, *rest)
            if len({abs(v) for v in core}) == 5 and all(
                triple in paired for triple in combinations(core, 3)
            ):
                return core
    return None


def structural_hybrid_sat(n, clauses, *, max_calls=None,
                          max_separator_size=2, pair_scan_limit=36):
    """Decide by affine elimination, a five-literal witness, or separator search."""
    clauses = _validate(n, clauses)
    recognized, model, affine_metrics = _affine_on_validated(n, clauses)
    if recognized:
        return model, {"status": "completed", "method": "affine_gf2",
                       "affine": affine_metrics}
    core = _five_literal_core(clauses)
    if core is not None:
        return None, {"status": "completed", "method": "five_literal_core",
                      "core": core, "affine": affine_metrics}
    from graph_separator_sat import graph_separator_sat
    model, graph_metrics = graph_separator_sat(
        n, clauses, max_calls=max_calls,
        max_separator_size=max_separator_size,
        pair_scan_limit=pair_scan_limit,
    )
    return model, {"status": graph_metrics["status"], "method": "graph_separator",
                   "affine": affine_metrics, "graph": graph_metrics}
