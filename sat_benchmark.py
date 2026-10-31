"""Deterministic DPLL benchmarking variants. Worst-case exponential."""
from collections import Counter
from sat import _validate, verify

def solve_counted(n, clauses, heuristic="first"):
    """Return (witness or None, metrics). Metrics count recursive calls and branches."""
    if heuristic not in ("first", "occurrence"):
        raise ValueError("unknown heuristic")
    original = _validate(n, clauses)
    metrics = {"calls": 0, "branches": 0, "unit_steps": 0}

    def reduce_formula(formula, lit):
        reduced = []
        for clause in formula:
            if lit in clause:
                continue
            new_clause = tuple(v for v in clause if v != -lit)
            if not new_clause:
                return None
            reduced.append(new_clause)
        return reduced

    def solve(formula, assignment):
        metrics["calls"] += 1
        while True:
            if not formula:
                return assignment
            if any(not c for c in formula):
                return None
            unit = next((c[0] for c in formula if len(c) == 1), None)
            if unit is None:
                break
            metrics["unit_steps"] += 1
            var, value = abs(unit), unit > 0
            if var in assignment and assignment[var] != value:
                return None
            assignment = {**assignment, var: value}
            formula = reduce_formula(formula, unit)
            if formula is None:
                return None

        if heuristic == "first":
            pivot = min(formula, key=len)[0]
        else:
            counts = Counter(lit for clause in formula for lit in clause)
            variables = {abs(lit) for lit in counts}
            variable = min(variables, key=lambda v: (
                -(counts[v] + counts[-v]), v))
            pivot = variable if counts[variable] >= counts[-variable] else -variable

        for lit in (pivot, -pivot):
            metrics["branches"] += 1
            reduced = reduce_formula(formula, lit)
            if reduced is None:
                continue
            answer = solve(reduced, {**assignment, abs(lit): lit > 0})
            if answer is not None:
                return answer
        return None

    assignment = solve(original, {})
    if assignment is None:
        return None, metrics
    witness = [assignment.get(v, False) for v in range(1, n + 1)]
    assert verify(n, original, witness)
    return witness, metrics
