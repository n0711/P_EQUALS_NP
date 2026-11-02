"""Bounded, deterministic frontier-width experiment; JSON to stdout."""
import argparse
import json
import random
import tracemalloc

from frontier_sat import frontier_sat
from sat import verify


def experiment(n, clauses, order, family, seed, cap, seconds):
    tracemalloc.start()
    model, stats = frontier_sat(n, clauses, order, cap, seconds)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if stats['status'] == 'completed' and model is not None:
        assert verify(n, clauses, model)
    return {"family": family, "seed": seed, "n": n, "m": len(clauses),
            "sat": None if stats['status'] != 'completed' else model is not None,
            "peak_tracemalloc_mib": round(peak / 1048576, 3), **stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-states', type=int, default=100_000)
    parser.add_argument('--max-seconds', type=float, default=8.0)
    args = parser.parse_args()
    rows = []
    for k in (4, 8, 12, 16):
        n = 2 * k
        cnf = [(i, k + i) for i in range(1, k + 1)]
        grouped = list(range(1, n + 1))
        interleaved = [v for i in range(1, k + 1) for v in (i, k + i)]
        for name, order in (("pairs_grouped", grouped),
                            ("pairs_interleaved", interleaved)):
            rows.append(experiment(n, cnf, order, name, None,
                                   args.max_states, args.max_seconds))
    for n in (8, 10, 12):
        for seed in (101, 202, 303):
            rng = random.Random(seed + n)
            cnf = [tuple(rng.choice((-1, 1)) * rng.randrange(1, n + 1)
                         for _ in range(3)) for _ in range(4 * n)]
            rows.append(experiment(n, cnf, list(range(1, n + 1)),
                                   "random_3cnf", seed, args.max_states,
                                   args.max_seconds))
    print(json.dumps({"method": "clause-frontier exact DP",
                      "resource_limits": {"states": args.max_states,
                                          "seconds": args.max_seconds},
                      "timing_note": "one local run; tracemalloc is not total RSS",
                      "results": rows}, indent=2))


if __name__ == '__main__':
    main()
