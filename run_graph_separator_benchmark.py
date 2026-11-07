"""Reproducible, bounded separator-vs-DPLL exploratory measurements.

The timing fields reflect one host/run, not asymptotic complexity or speedup.
"""
import argparse
import itertools
import json
import random
from time import perf_counter

from graph_separator_sat import graph_separator_sat
from sat import dpll, verify


def one_gate(blocks):
    clauses = []
    for i in range(blocks):
        a, b = 2 * i + 2, 2 * i + 3
        clauses.extend(((1, a, b), (-1, -a, b), (a, -b)))
    return 2 * blocks + 1, clauses


def two_gates(blocks):
    clauses = []
    for i in range(blocks):
        a, b = 2 * i + 3, 2 * i + 4
        clauses.extend(((1, 2, a, b), (-1, -2, -a, -b)))
    return 2 * blocks + 2, clauses


def dense_unsat(n):
    clauses = [tuple(-v if values[v-1] else v for v in range(1, n+1))
               for values in itertools.product((False, True), repeat=n)]
    return n, clauses


def random_3cnf(n, seed):
    rng = random.Random(seed + n)
    clauses = [tuple(rng.choice((-1,1)) * rng.randrange(1,n+1)
                     for _ in range(3)) for _ in range(4*n)]
    return n, clauses


def measure(family, n, clauses, seed, max_calls):
    begin = perf_counter()
    reference = dpll(n, clauses)
    reference_seconds = perf_counter() - begin
    model, metrics = graph_separator_sat(n, clauses, max_calls=max_calls)
    if metrics['status'] == 'completed':
        if (model is None) != (reference is None):
            raise AssertionError((family, seed, 'SAT disagreement'))
        if model is not None and not verify(n, clauses, model):
            raise AssertionError((family, seed, 'invalid witness'))
    return {"family": family, "seed": seed, "n": n, "clauses": len(clauses),
            "baseline_sat": reference is not None,
            "baseline_seconds": round(reference_seconds, 6), **metrics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-calls', type=int, default=100000)
    args = parser.parse_args()
    results = []
    for blocks in (4, 8, 12):
        for name, create in (("one_gate", one_gate), ("two_gates", two_gates)):
            n, clauses = create(blocks)
            results.append(measure(name, n, clauses, None, args.max_calls))
    for n in (4, 6, 8):
        N, clauses = dense_unsat(n)
        results.append(measure("dense_unsat", N, clauses, None, args.max_calls))
    for n in (8, 10, 12):
        for seed in (101, 202, 303):
            N, clauses = random_3cnf(n, seed)
            results.append(measure("random_3cnf", N, clauses, seed, args.max_calls))
    print(json.dumps({"research_status": "structural SAT prototype, not P=NP",
                      "timing_note": "single Python host/run; do not infer speedups",
                      "max_calls": args.max_calls, "results": results}, indent=2))


if __name__ == '__main__':
    main()
