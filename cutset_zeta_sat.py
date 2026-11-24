"""M13: Exact #SAT through supplied logarithmic separators and tractable components.

This is a restricted-class counting algorithm, NOT a general polynomial-time
SAT/#SAT algorithm. It combines established cutset conditioning, connected
component factorization, affine rank counting, and small-component enumeration.

For explicitly represented CNF size proxy N=n+m+L, accept only:
- a caller-supplied separator of size <= floor(log2(max(2,N))),
- every non-affine residual connected component of size <= that bound.
Recognized affine components may be arbitrarily large.
Every rejected case returns status='unrecognized', NEVER a guessed count.
Only the caller-supplied separator is used; finding it is not implemented.
"""
from __future__ import annotations

from itertools import product

from affine_zeta_sat import affine_zeta_profile
from rh_grh_bridge import _normalized
from zeta_sat import count_sat_bounded, local_zeta_coefficients


def _components(clauses):
    """Return disjoint (variable IDs, clause lists) of a nonempty-clause CNF."""
    parent = {}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for clause in clauses:
        variables = sorted({abs(lit) for lit in clause})
        for v in variables:
            parent.setdefault(v, v)
        for v in variables[1:]:
            union(variables[0], v)

    grouped = {}
    for variable in sorted(parent):
        root = find(variable)
        grouped.setdefault(root, {"variables": [], "clauses": []})
        grouped[root]["variables"].append(variable)
    for clause in clauses:
        root = find(abs(clause[0]))
        grouped[root]["clauses"].append(clause)
    return [grouped[r] for r in sorted(grouped)]


def _restrict(clauses, fixed):
    residual = []
    for clause in clauses:
        literals = set(clause)
        if any(-lit in literals for lit in literals):
            continue
        reduced = []
        satisfied = False
        for literal in literals:
            value = fixed.get(abs(literal))
            if value is None:
                reduced.append(literal)
            elif value == (literal > 0):
                satisfied = True
                break
        if satisfied:
            continue
        if not reduced:
            return None
        residual.append(tuple(sorted(reduced, key=lambda x: (abs(x), x))))
    return residual


def _unrecognized(reason, metrics):
    return {
        "status": "unrecognized",
        "reason": reason,
        "model_count": None,
        "local_coefficients": None,
        "metrics": metrics,
    }


def cutset_zeta_profile(n, clauses, separator, *, local_degree=3):
    """Exact #SAT on formulas satisfying a verified logarithmic-cutset contract.

    The input n is an *explicit* variable count, and clauses are explicitly
    listed. Bound = floor(log2(max(2,n + clauses + literal occurrences))).
    This proxy differs from bit length but is <= O(input bit length) under
    the explicit variable convention, so the polynomial guarantee follows.

    Output is counted with exact count or unrecognized with null count.
    Component arithmetic is exact and includes isolated variables and
    all original variables in the #SAT count. Local coefficient degree d
    is explicit output size, and computational cost is polynomial in N+d
    for accepted inputs (not necessarily N+log(d)).
    """
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if type(local_degree) is not int or local_degree < 0:
        raise ValueError("local_degree must be a nonnegative integer")
    formula = _normalized(n, clauses)
    try:
        cutset = tuple(separator)
    except TypeError as error:
        raise ValueError("separator must be an iterable") from error
    if any(type(v) is not int or not (1 <= v <= n) for v in cutset):
        raise ValueError("separator must contain variable indices in 1..n")
    if len(set(cutset)) != len(cutset):
        raise ValueError("separator must contain distinct indices")
    # The original variable count is explicit input (not a compressed int).
    proxy = max(2, n + len(formula) + sum(len(c) for c in formula))
    bound = proxy.bit_length() - 1
    metrics = {
        "input_size_proxy": proxy,
        "log_bound": bound,
        "separator_variables": len(cutset),
        "branches_examined": 0,
        "affine_components": 0,
        "enumerated_components": 0,
        "max_component_variables": 0,
        "contradictory_branches": 0,
    }
    if len(cutset) > bound:
        return _unrecognized("separator exceeds logarithmic size bound", metrics)

    count = 0
    for bits in product((False, True), repeat=len(cutset)):
        metrics["branches_examined"] += 1
        fixed = dict(zip(cutset, bits))
        residual = _restrict(formula, fixed)
        if residual is None:
            metrics["contradictory_branches"] += 1
            continue
        components = _components(residual)
        used_variables = sum(len(c["variables"]) for c in components)
        free = n - len(cutset) - used_variables
        assert free >= 0
        branch_count = 1 << free
        for component in components:
            variables = component["variables"]
            metrics["max_component_variables"] = max(
                metrics["max_component_variables"], len(variables)
            )
            mapping = {v: i+1 for i, v in enumerate(variables)}
            compact = [
                tuple((1 if lit > 0 else -1) * mapping[abs(lit)]
                      for lit in clause)
                for clause in component["clauses"]
            ]
            affine = affine_zeta_profile(len(variables), compact, local_degree=0)
            if affine["status"] == "counted":
                metrics["affine_components"] += 1
                component_count = affine["model_count"]
            elif len(variables) <= bound:
                metrics["enumerated_components"] += 1
                component_count = count_sat_bounded(
                    len(variables), compact, max_variables=bound
                )
            else:
                return _unrecognized(
                    "non-affine residual component exceeds logarithmic bound",
                    metrics,
                )
            branch_count *= component_count
            if branch_count == 0:
                break
        count += branch_count

    return {
        "status": "counted",
        "reason": None,
        "model_count": count,
        "local_coefficients": local_zeta_coefficients(count, local_degree),
        "metrics": metrics,
    }
