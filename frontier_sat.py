"""Exact clause-frontier SAT dynamic programming (research baseline).

States are satisfaction bitmasks for clauses crossing the variable-order cut,
not complete assignments. Worst-case exponential in frontier width, NOT a P=NP proof.
"""
from __future__ import annotations

import time
from sat import _validate, verify


def frontier_sat(n, clauses, order=None, max_states=200_000, max_seconds=10.0):
    """Return (model_or_none, metrics). status: completed or limit_*.

    A completed None means UNSAT. Limited runs have no SAT/UNSAT decision.
    State key: satisfied clauses active across the prefix/suffix cut.
    """
    start = time.perf_counter()
    clauses = _validate(n, clauses)
    order = list(range(1, n + 1)) if order is None else list(order)
    if sorted(order) != list(range(1, n + 1)):
        raise ValueError("order must be a permutation of 1..n")
    if max_states < 1 or max_seconds <= 0:
        raise ValueError("positive resource limits required")

    normalized = set()
    for clause in clauses:
        c = frozenset(clause)
        if any(-lit in c for lit in c):
            continue  # tautology
        normalized.add(tuple(sorted(c)))
    formula = sorted(normalized)
    m = len(formula)
    metrics = {"status": "completed", "variables": n, "clauses": m,
               "max_frontier": 0, "peak_states": 1, "states_created": 1,
               "transitions": 0, "pruned": 0, "merged": 0,
               "elapsed_seconds": 0.0}

    def finish(model, status):
        metrics["status"] = status
        metrics["elapsed_seconds"] = time.perf_counter() - start
        if status == "completed" and model is not None:
            assert verify(n, clauses, model)
        return model, metrics

    if () in formula:
        return finish(None, "completed")

    positions = {v: i for i, v in enumerate(order)}
    truth = [0] * (n + 1)
    falsehood = [0] * (n + 1)
    closing = [0] * n
    active_after = [0] * n
    for j, clause in enumerate(formula):
        bit = 1 << j
        first = min(positions[abs(lit)] for lit in clause)
        last = max(positions[abs(lit)] for lit in clause)
        closing[last] |= bit
        for boundary in range(first + 1, last + 1):
            active_after[boundary - 1] |= bit
        for lit in clause:
            if lit > 0:
                truth[lit] |= bit
            else:
                falsehood[-lit] |= bit
    metrics["max_frontier"] = max((x.bit_count() for x in active_after), default=0)

    # One witness bitmask per reachable frontier state; not a path enumeration.
    states = {0: 0}
    for t, variable in enumerate(order):
        if time.perf_counter() - start > max_seconds:
            return finish(None, "limit_seconds")
        following = {}
        for state, witness in states.items():
            if time.perf_counter() - start > max_seconds:
                return finish(None, "limit_seconds")
            for value, satisfied in ((False, falsehood[variable]),
                                     (True, truth[variable])):
                metrics["transitions"] += 1
                combined = state | satisfied
                if (combined & closing[t]) != closing[t]:
                    metrics["pruned"] += 1
                    continue
                successor = combined & active_after[t]
                if successor in following:
                    metrics["merged"] += 1
                    continue
                if len(following) >= max_states:
                    return finish(None, "limit_states")
                following[successor] = witness | ((1 << (variable - 1)) if value else 0)
        states = following
        metrics["states_created"] += len(states)
        metrics["peak_states"] = max(metrics["peak_states"], len(states))
        if not states:
            return finish(None, "completed")

    if 0 not in states:
        raise AssertionError("terminal frontier must be empty")
    bits = states[0]
    model = [bool((bits >> i) & 1) for i in range(n)]
    return finish(model, "completed")
