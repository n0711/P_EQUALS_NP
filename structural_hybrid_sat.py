"""Exact affine-CNF recognition and deterministic GF(2) elimination.

Recognizes only conjunctions of complete 1-, 2-, or 3-XOR clause blocks.
Other CNFs are left to a complete solver. This is a standard tractable
Boolean class, not a polynomial-time algorithm for arbitrary SAT.
"""
from __future__ import annotations

from collections import defaultdict
from time import perf_counter

from sat import _validate, verify


def try_affine_sat(n, clauses):
    """Return (recognized, model_or_none, metrics).

    If recognized=False, model is None and no SAT decision was made.
    If recognized=True, None means UNSAT and otherwise model is verified.
    """
    started = perf_counter()
    original = _validate(n, clauses)
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


def structural_hybrid_sat(n, clauses, *, max_calls=None,
                          max_separator_size=2, pair_scan_limit=36):
    """An exact portfolio: GF(2) for recognized affine CNF, else separator SAT."""
    recognized, model, affine_metrics = try_affine_sat(n, clauses)
    if recognized:
        return model, {"status": "completed", "method": "affine_gf2",
                       "affine": affine_metrics}
    from graph_separator_sat import graph_separator_sat
    model, graph_metrics = graph_separator_sat(
        n, clauses, max_calls=max_calls,
        max_separator_size=max_separator_size,
        pair_scan_limit=pair_scan_limit,
    )
    return model, {"status": graph_metrics["status"], "method": "graph_separator",
                   "affine": affine_metrics, "graph": graph_metrics}
