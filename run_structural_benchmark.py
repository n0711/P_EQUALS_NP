"""Bounded, independent-process comparison of exact SAT research baselines.

Each solver is isolated behind a wall-clock timeout. Timeout/limit/error
is never converted into UNSAT. Tracemalloc measures tracked allocations,
not total resident memory. Counts between solvers are not interchangeable.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tracemalloc
from time import perf_counter

from graph_research_instances import (clique_three_coloring, cubic_tseitin_3cnf,
                                      graph_profile, pigeonhole_3cnf)
from sat import dpll, verify


def cases(quick):
    collection = [
        ("tseitin_cubic_even_v8", *cubic_tseitin_3cnf(8, seed=17, charge="even"), True),
        ("tseitin_cubic_odd_v8", *cubic_tseitin_3cnf(8, seed=17, charge="odd"), False),
        ("pigeonhole_3", *pigeonhole_3cnf(3), False),
        ("three_color_K4", *clique_three_coloring(4), False),
    ]
    if not quick:
        collection.extend([
            ("tseitin_cubic_even_v12", *cubic_tseitin_3cnf(12, seed=29, charge="even"), True),
            ("tseitin_cubic_odd_v12", *cubic_tseitin_3cnf(12, seed=29, charge="odd"), False),
            ("tseitin_cubic_even_v16", *cubic_tseitin_3cnf(16, seed=47, charge="even"), True),
            ("tseitin_cubic_odd_v16", *cubic_tseitin_3cnf(16, seed=47, charge="odd"), False),
            ("pigeonhole_4", *pigeonhole_3cnf(4), False),
            ("pigeonhole_5", *pigeonhole_3cnf(5), False),
            ("three_color_K3", *clique_three_coloring(3), True),
        ])
    return collection


def worker():
    payload = json.load(sys.stdin)
    n, clauses = payload["n"], payload["clauses"]
    method = payload["method"]
    max_calls = payload["max_calls"]
    tracemalloc.start()
    start = perf_counter()
    if method == "dpll":
        model = dpll(n, clauses)
        details = {"status": "completed", "method": "dpll"}
    elif method == "separator":
        from graph_separator_sat import graph_separator_sat
        model, details = graph_separator_sat(n, clauses, max_calls=max_calls,
                                            pair_scan_limit=24)
    elif method == "hybrid":
        from structural_hybrid_sat import structural_hybrid_sat
        model, details = structural_hybrid_sat(n, clauses, max_calls=max_calls,
                                               pair_scan_limit=24)
    else:
        raise ValueError("unrecognized solver")
    elapsed = perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    status = details["status"]
    if status == "completed" and model is not None and not verify(n, clauses, model):
        raise AssertionError("invalid SAT witness")
    json.dump({"status": status, "sat": (model is not None) if status == "completed"
               else None, "elapsed_seconds": round(elapsed, 6),
               "peak_tracemalloc_bytes": peak, "metrics": details}, sys.stdout)


def run_one(n, clauses, method, max_calls, timeout):
    payload = {"n": n, "clauses": clauses, "method": method,
               "max_calls": max_calls}
    started = perf_counter()
    try:
        result = subprocess.run([sys.executable, __file__, "--worker"],
                                input=json.dumps(payload), text=True,
                                capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "sat": None,
                "wall_seconds": round(perf_counter() - started, 6)}
    if result.returncode:
        raise RuntimeError(f"{method} worker failed: {result.stderr[:800]}")
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{method} invalid JSON response: {result.stdout[:800]}") from exc
    output["wall_seconds"] = round(perf_counter() - started, 6)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=3.0)
    parser.add_argument("--max-calls", type=int, default=1200)
    args = parser.parse_args()
    if args.worker:
        worker()
        return
    if args.timeout_seconds <= 0 or args.max_calls < 1:
        parser.error("positive limits required")
    report = {"scope": "finite empirical comparisons, not a P=NP proof",
              "timeout_seconds_per_solver": args.timeout_seconds,
              "max_calls_separator": args.max_calls,
              "memory_measurement": "tracemalloc Python allocated bytes, not RSS",
              "timing_measurement": "one machine per run, include process startup in wall_seconds",
              "cases": []}
    for family, n, clauses, expected in cases(args.quick):
        profile = graph_profile(n, clauses)
        entries = {}
        for method in ("dpll", "separator", "hybrid"):
            result = run_one(n, clauses, method, args.max_calls,
                             args.timeout_seconds)
            if result["status"] == "completed" and result["sat"] != expected:
                raise AssertionError((family, method, "incorrect SAT/UNSAT", result))
            entries[method] = result
        report["cases"].append({"name": family, "n": n, "m": len(clauses),
                                "expected_sat": expected,
                                "graph": profile, "solvers": entries})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
