"""M15: Bellman-Ford certificates for a conservative Boolean difference-CNF class.

Recognized clauses after duplicate/tautology cleanup:
  ()                    => contradiction 0 <= -1 (negative self-loop);
  (x_i) or (not x_i)   => fix x_i to 1 or 0;
  (not x_i or x_j)     => x_i <= x_j (directed edge j -> i, weight 0).

Represent each Boolean x_i as an integer potential d_i-d_0 constrained
between zero and one. Every recognized satisfying assignment is feasible
as such a potential vector, and integer Bellman-Ford distances recover
a Boolean satisfying assignment whenever no negative cycle exists.

The method is polynomial on this RESTRICTED class, which is a subset of
2-SAT. It does not solve general SAT, count models, or compute the M11
arithmetic zeta exponent. Unsupported CNF returns 'unrecognized'.
"""
from __future__ import annotations

from sat import _validate, verify


def _negative_cycle(start, predecessors, node_count):
    """Recover a concrete forward-oriented negative cycle as (u,v,w) edges."""
    node = start
    for _ in range(node_count):
        predecessor = predecessors[node]
        if predecessor is None:
            raise AssertionError("Bellman-Ford cycle predecessor missing")
        node = predecessor[0]
    root = node
    edges = []
    while True:
        edge = predecessors[node]
        if edge is None:
            raise AssertionError("Bellman-Ford cycle chain interrupted")
        edges.append(edge)
        node = edge[0]
        if node == root:
            break
        if len(edges) > node_count:
            raise AssertionError("invalid predecessor cycle length")
    edges.reverse()
    assert edges and all(a[1] == b[0] for a, b in
                         zip(edges, edges[1:] + edges[:1]))
    assert sum(weight for _, _, weight in edges) < 0
    return tuple(edges)


def bellman_ford_boolean_sat(n, clauses):
    """Decide *only* implication-and-unit CNF through difference constraints.

    Return a dict with status: 'sat', 'unsat', or 'unrecognized'.
    A SAT status includes verified model of n Boolean values.
    UNSAT includes a negative-weight cycle certificate as directed edges.
    An unrecognized input gets no SAT/UNSAT claim and no model.

    Number of nodes is n+1 (node 0 is reference x0).
    At most 2n+m constraint edges; Bellman-Ford takes O((n+1)*(n+m)).
    Variables must be explicitly accounted for by their count n.
    """
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    original = _validate(n, clauses)
    # Edges implement x_v - x_u <= c.
    edges = []
    for i in range(1, n + 1):
        edges.append((0, i, 1))   # x_i - x_0 <= 1
        edges.append((i, 0, 0))   # x_0 - x_i <= 0

    supported = set()
    for clause in original:
        literal_set = set(clause)
        if any(-lit in literal_set for lit in literal_set):
            continue  # tautology, including repeated occurrences
        literals = tuple(sorted(literal_set, key=lambda lit: (abs(lit), lit)))
        if literals in supported:
            continue
        supported.add(literals)
        if not literals:
            edges.append((0, 0, -1))  # 0 <= -1, explicit certificate
        elif len(literals) == 1:
            lit = literals[0]
            var = abs(lit)
            if lit > 0:
                edges.append((var, 0, -1))   # x_var >= 1
            else:
                edges.append((0, var, 0))    # x_var <= 0
        elif len(literals) == 2 and literals[0] * literals[1] < 0:
            neg = next(-lit for lit in literals if lit < 0)
            pos = next(lit for lit in literals if lit > 0)
            edges.append((pos, neg, 0))  # (not x_neg or x_pos)
        else:
            return {
                "status": "unrecognized",
                "model": None,
                "negative_cycle": None,
                "reason": "clause outside unit/implication difference constraints",
                "metrics": {"variables": n, "input_clauses": len(original),
                            "constraints_examined": len(supported)},
            }

    node_count = n + 1
    # Implicit super-source with zero edges to every node: dist=0 initially.
    distances = [0] * node_count
    predecessor = [None] * node_count
    passes = 0
    last_relaxed = None
    for _ in range(node_count):
        passes += 1
        last_relaxed = None
        for u, v, weight in edges:
            candidate = distances[u] + weight
            if candidate < distances[v]:
                distances[v] = candidate
                predecessor[v] = (u, v, weight)
                last_relaxed = v
        if last_relaxed is None:
            break

    metrics = {
        "variables": n, "input_clauses": len(original),
        "constraints_examined": len(supported),
        "nodes": node_count, "edges": len(edges), "passes": passes,
    }
    if last_relaxed is not None:
        return {
            "status": "unsat",
            "model": None,
            "negative_cycle": _negative_cycle(last_relaxed, predecessor,
                                              node_count),
            "reason": "negative-weight difference-constraint cycle",
            "metrics": metrics,
        }

    assignment = []
    for i in range(1, n + 1):
        value = distances[i] - distances[0]
        if value not in (0, 1):
            raise AssertionError("Boolean bounds violated by integer distances")
        assignment.append(bool(value))
    if not verify(n, original, assignment):
        raise AssertionError("Bellman-Ford witness fails original CNF")
    return {
        "status": "sat",
        "model": assignment,
        "negative_cycle": None,
        "reason": None,
        "metrics": metrics,
    }
