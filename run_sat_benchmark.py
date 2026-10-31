"""CLI to compare deterministic branching; no runtime claims from node counts."""
import argparse
import json
import random
from sat_benchmark import solve_counted

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261031)
    p.add_argument("--variables", type=int, default=10)
    p.add_argument("--instances", type=int, default=20)
    p.add_argument("--clauses", type=int, default=35)
    args = p.parse_args()
    if args.variables < 1 or args.instances < 0 or args.clauses < 0:
        p.error("variables must be positive; instances and clauses nonnegative")
    rng = random.Random(args.seed)
    result = []
    for i in range(args.instances):
        cnf = [tuple((1 if rng.getrandbits(1) else -1) * rng.randint(1, args.variables)
                     for _ in range(3)) for _ in range(args.clauses)]
        a, left = solve_counted(args.variables, cnf, "first")
        b, right = solve_counted(args.variables, cnf, "occurrence")
        if (a is None) != (b is None):
            raise AssertionError("solvers disagree")
        result.append({"instance": i, "satisfiable": a is not None,
                       "first": left, "occurrence": right})
    print(json.dumps({"seed": args.seed, "variables": args.variables,
                      "clauses": args.clauses, "results": result}, indent=2))

if __name__ == "__main__":
    main()
