"""Deterministic primal-graph profiles and explicit SAT benchmark generators.

Reported min-fill width is an upper bound on treewidth, NOT exact treewidth.
Degeneracy is a lower bound on treewidth. These are graph metrics, not
complexity lower bounds for every SAT algorithm.
"""
from __future__ import annotations

import itertools
import random


def primal_graph(n, clauses):
    if n < 0:
        raise ValueError("n must be nonnegative")
    graph = {}
    for clause in clauses:
        group = sorted({abs(lit) for lit in clause})
        if any(v < 1 or v > n for v in group):
            raise ValueError("literal index out of range")
        for v in group:
            graph.setdefault(v, set())
        for index, v in enumerate(group):
            for w in group[index + 1:]:
                graph[v].add(w)
                graph[w].add(v)
    return graph


def _components(graph, excluded=()):
    todo = set(graph).difference(excluded)
    groups = []
    while todo:
        root = min(todo)
        todo.remove(root)
        reachable = {root}
        stack = [root]
        while stack:
            v = stack.pop()
            for w in graph[v] & todo:
                todo.remove(w)
                reachable.add(w)
                stack.append(w)
        groups.append(reachable)
    return groups


def graph_profile(n, clauses):
    graph = primal_graph(n, clauses)
    work = {v: set(neighbors) for v, neighbors in graph.items()}
    components = len(_components(graph))
    lower = 0
    peel = {v: set(ns) for v, ns in graph.items()}
    while peel:
        v = min(peel, key=lambda k: (len(peel[k]), k))
        lower = max(lower, len(peel[v]))
        for u in peel[v]:
            peel[u].remove(v)
        del peel[v]
    width = 0
    fills = 0
    ordering = []
    while work:
        def score(v):
            near = sorted(work[v])
            missing = sum(b not in work[a]
                          for i, a in enumerate(near) for b in near[i + 1:])
            return (missing, len(near), v)
        v = min(work, key=score)
        neighbors = sorted(work[v])
        width = max(width, len(neighbors))
        ordering.append(v)
        for index, a in enumerate(neighbors):
            for b in neighbors[index + 1:]:
                if b not in work[a]:
                    work[a].add(b)
                    work[b].add(a)
                    fills += 1
        for a in neighbors:
            work[a].remove(v)
        del work[v]
    articulation = sum(len(_components(graph, (v,))) > components
                       for v in graph)
    return {"active_variables": len(graph),
            "edges": sum(map(len, graph.values())) // 2,
            "components": components,
            "articulation_vertices": articulation,
            "degeneracy_lower_bound": lower,
            "min_fill_width_upper_bound": width,
            "min_fill_added_edges": fills,
            "min_fill_elimination_order": ordering}


def _cycle_matching(vertices, seed):
    """Connected cubic graph: Hamiltonian cycle + seeded disjoint noncycle matching."""
    if vertices < 6 or vertices % 2:
        raise ValueError("vertices must be even and >= 6")
    rng = random.Random(seed)
    ring = {tuple(sorted((i, (i+1) % vertices))) for i in range(vertices)}
    for _ in range(10000):
        items = list(range(vertices))
        rng.shuffle(items)
        pairs = {tuple(sorted((items[i], items[i + 1])))
                 for i in range(0, vertices, 2)}
        if not pairs.intersection(ring):
            return sorted(ring | pairs)
    raise RuntimeError("cannot construct noncycle matching")


def cubic_tseitin_3cnf(vertices, seed=0, charge="odd"):
    """3-XOR Tseitin constraints on a seeded connected 3-regular graph.

    Every graph edge is a Boolean variable. Odd total parity is UNSAT.
    Even total parity is SAT because the graph is connected.
    """
    if charge not in ("even", "odd"):
        raise ValueError("charge must be even or odd")
    edges = _cycle_matching(vertices, seed)
    incident = [[] for _ in range(vertices)]
    for variable, (u, v) in enumerate(edges, 1):
        incident[u].append(variable)
        incident[v].append(variable)
    if not all(len(edge_vars) == 3 for edge_vars in incident):
        raise AssertionError("expected cubic graph")
    charges = [0] * vertices
    charges[0] = 1
    if charge == "even":
        charges[-1] = 1
    clauses = []
    for vertex, edge_vars in enumerate(incident):
        for values in itertools.product((0, 1), repeat=3):
            if sum(values) % 2 != charges[vertex]:
                clauses.append(tuple(-v if b else v
                                     for v, b in zip(sorted(edge_vars), values)))
    return len(edges), clauses


def pigeonhole_3cnf(pigeons):
    """Equisatisfiable 3-CNF for PHP(pigeons, pigeons-1), UNSAT when pigeons>=2.

    Introduced chain variables preserve existence of assignments, not #SAT.
    """
    if pigeons < 2:
        raise ValueError("need at least 2 pigeons")
    holes = pigeons - 1
    n = pigeons * holes
    clauses = []
    def var(p, h):
        return 1 + p * holes + h

    def add_or_chain(literals):
        nonlocal n
        if len(literals) <= 3:
            clauses.append(tuple(literals))
            return
        n += 1
        aux = n
        clauses.append((literals[0], literals[1], aux))
        for pos in range(2, len(literals) - 2):
            last = aux
            n += 1
            aux = n
            clauses.append((-last, literals[pos], aux))
        clauses.append((-aux, literals[-2], literals[-1]))

    for p in range(pigeons):
        add_or_chain([var(p, h) for h in range(holes)])
        for h1 in range(holes):
            for h2 in range(h1 + 1, holes):
                clauses.append((-var(p, h1), -var(p, h2)))
    for h in range(holes):
        for p in range(pigeons):
            for q in range(p + 1, pigeons):
                clauses.append((-var(p, h), -var(q, h)))
    return n, clauses


def clique_three_coloring(vertices):
    """3-coloring SAT of K_vertices: SAT for <=3, UNSAT for >=4."""
    if vertices < 1:
        raise ValueError("positive number of vertices required")
    clauses = []
    def variable(v, c):
        return 3 * v + c + 1
    for v in range(vertices):
        clauses.append(tuple(variable(v, c) for c in range(3)))
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append((-variable(v, c), -variable(v, d)))
    for v in range(vertices):
        for w in range(v + 1, vertices):
            for c in range(3):
                clauses.append((-variable(v, c), -variable(w, c)))
    return 3 * vertices, clauses
