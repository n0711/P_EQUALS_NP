"""Exact SAT by decomposing disconnected variable-clause incidence components.

Standard structural preprocessing, not an unrestricted polynomial-time SAT algorithm.
Input: n variables 1..n and an iterable of signed-literal clauses.
Return: (verified model or None, statistics). None means UNSAT.
"""
from __future__ import annotations

from sat import _validate, dpll, verify


def component_sat(n, clauses):
    """Factor an arbitrary CNF into disjoint variable components before DPLL.

    Independent components have disjoint variable sets. The empty clause is UNSAT.
    Tautological and duplicate clauses are removed without changing semantics.
    """
    original = _validate(n, clauses)
    normalized = set()
    for clause in original:
        literals = frozenset(clause)
        if any(-lit in literals for lit in literals):
            continue
        normalized.add(tuple(sorted(literals, key=lambda x: (abs(x), x))))
    formula = sorted(normalized, key=lambda c: (len(c), c))
    stats = {"status": "completed", "variables": n, "clauses_original": len(original),
             "clauses_normalized": len(formula), "components": 0,
             "max_component_variables": 0, "max_component_clauses": 0,
             "dpll_calls": 0}

    if () in normalized:
        return None, stats
    if not formula:
        model = [False] * n
        assert verify(n, original, model)
        return model, stats

    parent = list(range(n + 1))
    rank = [0] * (n + 1)

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    used = set()
    for clause in formula:
        variables = [abs(lit) for lit in clause]
        used.update(variables)
        anchor = variables[0]
        for v in variables[1:]:
            union(anchor, v)

    grouped_variables = {}
    for v in sorted(used):
        grouped_variables.setdefault(find(v), []).append(v)
    grouped_clauses = {r: [] for r in grouped_variables}
    for clause in formula:
        grouped_clauses[find(abs(clause[0]))].append(clause)

    stats["components"] = len(grouped_variables)
    model = [False] * n
    for root in sorted(grouped_variables, key=lambda r: grouped_variables[r][0]):
        variables = grouped_variables[root]
        group_clauses = grouped_clauses[root]
        stats["max_component_variables"] = max(stats["max_component_variables"], len(variables))
        stats["max_component_clauses"] = max(stats["max_component_clauses"], len(group_clauses))
        local = {v: i + 1 for i, v in enumerate(variables)}
        compact = [tuple((1 if lit > 0 else -1) * local[abs(lit)] for lit in clause)
                   for clause in group_clauses]
        stats["dpll_calls"] += 1
        component_model = dpll(len(variables), compact)
        if component_model is None:
            return None, stats
        for v, value in zip(variables, component_model):
            model[v - 1] = value

    assert verify(n, original, model)
    return model, stats
