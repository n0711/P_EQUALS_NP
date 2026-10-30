"""SAT research baseline: polynomial 2-SAT, general DPLL (worst-case exponential).

CNF is a list of clauses, each a list of signed nonzero integer literals.
Variable indices are 1..n. No external dependencies.
"""
from __future__ import annotations

def _validate(n, clauses):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be nonnegative integer")
    out = []
    for clause in clauses:
        row = tuple(clause)
        if any(not isinstance(lit, int) or isinstance(lit, bool)
               or lit == 0 or abs(lit) > n for lit in row):
            raise ValueError("literals must be signed variable indices 1..n")
        out.append(row)
    return out

def verify(n, clauses, assignment):
    """Check a purported model against the original formula."""
    return (len(assignment) == n and
            all(any(assignment[abs(lit)-1] == (lit > 0) for lit in clause)
                for clause in clauses))

def two_sat(n, clauses):
    """2-CNF decision and witness via implication graph SCC, O(n+m).
    
    Returns a list of n bools, or None when unsatisfiable.
    """
    clauses = _validate(n, clauses)
    if any(len(c) > 2 for c in clauses):
        raise ValueError("two_sat requires clauses with at most 2 literals")
    size = 2*n
    edges = [[] for _ in range(size)]
    reverse = [[] for _ in range(size)]
    def node(lit):
        return 2*(abs(lit)-1) + (0 if lit > 0 else 1)
    def add(a, b):
        edges[a].append(b)
        reverse[b].append(a)
    for clause in clauses:
        if not clause:
            return None
        a, b = (clause[0], clause[0]) if len(clause) == 1 else clause
        add(node(-a), node(b))
        add(node(-b), node(a))
    visited = [False]*size
    order = []
    for root in range(size):
        if visited[root]:
            continue
        visited[root] = True
        stack = [(root, 0)]
        while stack:
            v, idx = stack[-1]
            if idx == len(edges[v]):
                order.append(v)
                stack.pop()
            else:
                stack[-1] = (v, idx+1)
                w = edges[v][idx]
                if not visited[w]:
                    visited[w] = True
                    stack.append((w, 0))
    components = [-1]*size
    count = 0
    for root in reversed(order):
        if components[root] != -1:
            continue
        components[root] = count
        stack = [root]
        while stack:
            v = stack.pop()
            for w in reverse[v]:
                if components[w] == -1:
                    components[w] = count
                    stack.append(w)
        count += 1
    answer = []
    for v in range(n):
        pos, neg = components[2*v], components[2*v+1]
        if pos == neg:
            return None
        answer.append(pos > neg)
    assert verify(n, clauses, answer)
    return answer

def dpll(n, clauses):
    """Correct general CNF SAT baseline. Exponential worst-case; not P=NP."""
    clauses = _validate(n, clauses)
    def reduce_formula(formula, lit):
        result = []
        for clause in formula:
            if lit in clause:
                continue
            new = tuple(x for x in clause if x != -lit)
            if not new:
                return None
            result.append(new)
        return result
    def solve(formula, partial):
        while True:
            if not formula:
                return partial
            if any(len(c) == 0 for c in formula):
                return None
            unit = next((c[0] for c in formula if len(c) == 1), None)
            if unit is None:
                break
            var = abs(unit)
            value = unit > 0
            if var in partial and partial[var] != value:
                return None
            partial = {**partial, var: value}
            formula = reduce_formula(formula, unit)
            if formula is None:
                return None
        pivot = min(formula, key=len)[0]
        for lit in (pivot, -pivot):
            next_formula = reduce_formula(formula, lit)
            if next_formula is None:
                continue
            result = solve(next_formula, {**partial, abs(lit): lit > 0})
            if result is not None:
                return result
        return None
    result = solve(clauses, {})
    if result is None:
        return None
    witness = [result.get(i, False) for i in range(1, n+1)]
    assert verify(n, clauses, witness)
    return witness
