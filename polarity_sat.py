"""Exact SAT preprocessing by clause-support signatures and literal polarity.

Recognizes standard sufficient UNSAT patterns and performs classical
unit/pure-literal reductions. Complete graph connectivity alone is not hardness.
Full general SAT still needs the exact fallback (exponential worst case).
"""
from __future__ import annotations

from collections import defaultdict
from time import perf_counter

from sat import _validate, verify


def _normalize(clauses):
    result = set()
    for clause in clauses:
        literals = set(clause)
        if any(-lit in literals for lit in literals):
            continue
        result.add(tuple(sorted(literals, key=lambda lit: abs(lit))))
    return tuple(sorted(result, key=lambda c: (len(c), c)))


def _restrict(formula, assignments):
    result = []
    for clause in formula:
        if any((lit > 0) == assignments[abs(lit)]
               for lit in clause if abs(lit) in assignments):
            continue
        rest = tuple(lit for lit in clause if abs(lit) not in assignments)
        if not rest:
            return ((),)
        result.append(rest)
    return tuple(sorted(set(result), key=lambda c: (len(c), c)))


def _complete_support(formula, max_width):
    """Return support proving UNSAT, or None.

    A width-k clause over one fixed support excludes precisely one
    assignment to its k variables. All 2**k patterns exclude every model.
    """
    signatures = defaultdict(set)
    for clause in formula:
        if 1 <= len(clause) <= max_width:
            support = tuple(abs(lit) for lit in clause)
            signature = tuple(lit < 0 for lit in clause)
            signatures[support].add(signature)
    for support in sorted(signatures):
        if len(signatures[support]) == (1 << len(support)):
            return support
    return None


def preprocess_polarity(n, clauses, *, max_signature_width=3):
    """Return (state, residual_formula, implied_assignment, statistics).

    State is SAT, UNSAT or RESIDUAL. In RESIDUAL only the partial model
    is established, and the remaining formula must still be decided.
    """
    original = _validate(n, clauses)
    if not isinstance(max_signature_width, int) or isinstance(max_signature_width, bool) or max_signature_width < 0:
        raise ValueError("max_signature_width must be a nonnegative integer")
    started = perf_counter()
    formula = _normalize(original)
    assigned = {}
    stats = {
        "state": "RESIDUAL", "unit_assignments": 0,
        "pure_assignments": 0, "complete_support_contradictions": 0,
        "complete_support_witness": None, "passes": 0,
        "original_clauses": len(original), "normalized_clauses": len(formula),
        "remaining_clauses": 0, "remaining_active_variables": 0,
        "elapsed_seconds": 0.0,
    }

    def finish(state):
        stats["state"] = state
        stats["remaining_clauses"] = len(formula)
        stats["remaining_active_variables"] = len({
            abs(lit) for clause in formula for lit in clause
        })
        stats["elapsed_seconds"] = perf_counter() - started
        return state, formula, dict(assigned), stats

    while True:
        stats["passes"] += 1
        if () in formula:
            return finish("UNSAT")
        if not formula:
            return finish("SAT")
        support = _complete_support(formula, max_signature_width)
        if support is not None:
            stats["complete_support_contradictions"] += 1
            stats["complete_support_witness"] = list(support)
            return finish("UNSAT")

        unit = next((clause[0] for clause in formula if len(clause) == 1), None)
        if unit is not None:
            variable = abs(unit)
            value = unit > 0
            if variable in assigned and assigned[variable] != value:
                return finish("UNSAT")
            assigned[variable] = value
            stats["unit_assignments"] += 1
            formula = _restrict(formula, {variable: value})
            continue

        polarities = {}
        for clause in formula:
            for lit in clause:
                variable = abs(lit)
                polarities[variable] = polarities.get(variable, 0) | (
                    1 if lit > 0 else 2
                )
        pure = {v: (mask == 1) for v, mask in sorted(polarities.items())
                if mask in (1, 2)}
        if pure:
            for v, value in pure.items():
                assigned[v] = value
            stats["pure_assignments"] += len(pure)
            formula = _restrict(formula, pure)
            continue

        return finish("RESIDUAL")


def polarity_hybrid_sat(n, clauses, *, max_signature_width=3,
                        max_calls=None, max_separator_size=2,
                        pair_scan_limit=36):
    """Portfolio with status=completed or limit_calls.

    All complete SAT/UNSAT outcomes are exact. An explicit call limit
    returns no model and status=limit_calls, never an UNSAT decision.
    """
    original = _validate(n, clauses)
    state, residual, partial, preprocessing = preprocess_polarity(
        n, original, max_signature_width=max_signature_width)
    if state == "UNSAT":
        return None, {"status": "completed",
                      "method": "support_contradiction_or_unit",
                      "preprocessing": preprocessing}
    if state == "SAT":
        model = [partial.get(v, False) for v in range(1, n + 1)]
        assert verify(n, original, model)
        return model, {"status": "completed", "method": "polarity_preprocess",
                       "preprocessing": preprocessing}

    from structural_hybrid_sat import structural_hybrid_sat
    remainder_model, downstream = structural_hybrid_sat(
        n, residual, max_calls=max_calls,
        max_separator_size=max_separator_size,
        pair_scan_limit=pair_scan_limit)
    if downstream["status"] != "completed":
        return None, {"status": downstream["status"],
                      "method": "polarity_then_" + downstream["method"],
                      "preprocessing": preprocessing, "downstream": downstream}
    if remainder_model is None:
        return None, {"status": "completed",
                      "method": "polarity_then_" + downstream["method"],
                      "preprocessing": preprocessing, "downstream": downstream}
    model = list(remainder_model)
    for v, value in partial.items():
        model[v - 1] = value
    assert verify(n, original, model)
    return model, {"status": "completed",
                   "method": "polarity_then_" + downstream["method"],
                   "preprocessing": preprocessing, "downstream": downstream}
