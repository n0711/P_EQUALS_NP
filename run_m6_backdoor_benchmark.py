"""Isolated, bounded mixed-affine backdoor benchmarks with raw JSON evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from time import perf_counter

from graph_research_instances import (clique_three_coloring,
                                      cubic_tseitin_3cnf, pigeonhole_3cnf,
                                      graph_profile)
from mixed_affine_sat import mixed_affine_sat
from sat import dpll, verify


def cases(quick):
    items = []
    sizes = (8,) if quick else (8, 12, 16)
    for vertices in sizes:
        for charge in ("even", "odd"):
            n, base = cubic_tseitin_3cnf(vertices, seed=733, charge=charge)
            if charge == "even":
                witness, _ = mixed_affine_sat(n, base)
                assert witness is not None
                extra = tuple(v if witness[v-1] else -v for v in (1,2,3,4))
            else:
                extra = (1,2,3,4)
            items.append((f"cubic_xor_{charge}_v{vertices}_plus_general",
                          n, base + [extra], charge == "even"))
    n, clauses = pigeonhole_3cnf(3 if quick else 4)
    items.append(("non_affine_pigeonhole", n, clauses, False))
    if not quick:
        n, clauses = clique_three_coloring(4)
        items.append(("non_affine_three_color_K4", n, clauses, False))
    return items


def worker():
    payload = json.load(sys.stdin)
    n, clauses = payload["n"], payload["clauses"]
    start = perf_counter()
    method = payload["solver"]
    if method == "dpll":
        model = dpll(n, clauses)
        metrics = {"status": "completed", "method": "dpll"}
    elif method == "separator":
        from graph_separator_sat import graph_separator_sat
        model, metrics = graph_separator_sat(
            n, clauses, max_calls=payload["max_calls"], pair_scan_limit=24)
    elif method == "mixed":
        model, metrics = mixed_affine_sat(n, clauses,
                                          max_calls=payload["max_calls"])
    else:
        raise ValueError("bad solver")
    if metrics["status"] == "completed" and model is not None:
        assert verify(n, clauses, model)
    json.dump({"status": metrics["status"],
               "sat": (model is not None) if metrics["status"] == "completed" else None,
               "solver_seconds": round(perf_counter() - start, 6),
               "metrics": metrics}, sys.stdout)


def measure(n, clauses, solver, timeout, max_calls):
    request = {"n": n, "clauses": clauses, "solver": solver,
               "max_calls": max_calls}
    before = perf_counter()
    try:
        proc = subprocess.run([sys.executable, __file__, "--worker"],
                              input=json.dumps(request), text=True,
                              capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "sat": None,
                "wall_seconds": round(perf_counter() - before, 6)}
    if proc.returncode:
        return {"status": "error", "sat": None,
                "error": proc.stderr[-1200:],
                "wall_seconds": round(perf_counter() - before, 6)}
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "sat": None, "error": "invalid JSON response"}
    result["wall_seconds"] = round(perf_counter() - before, 6)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", action="store_true")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--timeout-seconds", type=float, default=3.0)
    p.add_argument("--max-calls", type=int, default=10000)
    args = p.parse_args()
    if args.worker:
        worker()
        return
    if args.max_calls < 1 or args.timeout_seconds <= 0:
        p.error("positive limits required")
    data = {"status": "research benchmark; no P=NP result",
            "python": sys.version,
            "limits": {"seconds_per_solver": args.timeout_seconds,
                       "recursive_calls": args.max_calls},
            "cases": []}
    for name, n, clauses, expected in cases(args.quick):
        encoded = json.dumps({"n": n, "clauses": clauses},
                             separators=(",", ":"), sort_keys=True).encode()
        row = {"name": name, "n": n, "clauses": len(clauses),
               "sha256_input": hashlib.sha256(encoded).hexdigest(),
               "expected_sat": expected,
               "graph": graph_profile(n, clauses),
               "solvers": {}}
        for solver in ("dpll", "separator", "mixed"):
            result = measure(n, clauses, solver,
                             args.timeout_seconds, args.max_calls)
            if result["status"] == "completed" and result["sat"] != expected:
                raise AssertionError((name, solver, "incorrect decision", result))
            row["solvers"][solver] = result
        data["cases"].append(row)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
