"""Bounded, reproducible structural comparison on same-graph CNF families.

A timeout or call ceiling is UNDECIDED, never UNSAT.
The graph profile is identical across each triple of family examples.
"""
import argparse
import json

from dense_cnf_families import (all_positive_triples,
                                all_signs_on_each_triple,
                                opposite_monotone_triples)
from graph_research_instances import graph_profile
from run_structural_benchmark import run_one


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=3.0)
    parser.add_argument("--max-calls", type=int, default=1800)
    args = parser.parse_args()
    if args.timeout_seconds <= 0 or args.max_calls <= 0:
        parser.error("positive resource budgets required")
    results = []
    ns = (4, 6, 8) if args.quick else (3, 4, 5, 6, 8, 10)
    for n in ns:
        for family, builder in (
            ("positive_complete_3cnf", all_positive_triples),
            ("every_triple_all_signs", all_signs_on_each_triple),
            ("opposite_monotone_triples", opposite_monotone_triples),
        ):
            width, clauses = builder(n)
            expected = (family == "positive_complete_3cnf"
                        or (family == "opposite_monotone_triples" and n <= 4))
            solvers = {}
            for method in ("dpll", "hybrid", "polarity"):
                result = run_one(width, clauses, method, args.max_calls,
                                 args.timeout_seconds)
                if result["status"] == "completed" and result["sat"] != expected:
                    raise AssertionError((family, n, method, "incorrect result"))
                solvers[method] = result
            results.append({
                "family": family, "n": width, "m": len(clauses),
                "expected_sat_from_mathematical_construction": expected,
                "graph_profile": graph_profile(width, clauses),
                "solvers": solvers,
            })
    print(json.dumps({
        "research_milestone": "M6",
        "claim": "same primal graph need not imply the same SAT status",
        "scope": "standard preprocessing plus exact fallback, not P=NP",
        "python_tracemalloc_warning": "tracked allocations are not RSS",
        "timing_warning": "one runner, per-solver subprocess wall budgets",
        "max_calls": args.max_calls,
        "timeout_seconds": args.timeout_seconds,
        "cases": results,
    }, indent=2))


if __name__ == "__main__":
    main()
