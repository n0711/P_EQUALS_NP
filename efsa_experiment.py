import json
import random
import time
import itertools
from sat import verify
from sat_benchmark import solve_counted

SEED = 20261031
SIZES = [8, 10, 12, 14, 16]
INSTANCES = 8
MAX_STATES = 100000
MAX_SECONDS = 10

rng = random.Random(SEED)
results = []

class LimitReached(Exception):
    pass

def normalize(clauses):
    """Canonical residual CNF; remove tautologies and duplicates."""
    normalized = set()
    for clause in clauses:
        c = frozenset(clause)
        if any(-lit in c for lit in c):
            continue
        normalized.add(tuple(sorted(c)))
    return tuple(sorted(normalized, key=lambda c: (len(c), c)))

def assign(formula, lit):
    reduced = []
    for clause in formula:
        if lit in clause:
            continue
        reduced.append(tuple(x for x in clause if x != -lit))
    return normalize(reduced)

def symbolic_sat(clauses):
    cache = {}
    metrics = {"states": 0, "cache_hits": 0, "transitions": 0}
    start = time.perf_counter()

    def visit(formula):
        if time.perf_counter() - start > MAX_SECONDS:
            raise LimitReached("time")

        if formula in cache:
            metrics["cache_hits"] += 1
            return cache[formula]

        if metrics["states"] >= MAX_STATES:
            raise LimitReached("states")

        metrics["states"] += 1

        if not formula:
            answer = True
        elif any(len(c) == 0 for c in formula):
            answer = False
        else:
            unit = next((c[0] for c in formula if len(c) == 1), None)

            if unit is not None:
                metrics["transitions"] += 1
                answer = visit(assign(formula, unit))
            else:
                pivot = formula[0][0]
                answer = False

                for lit in (pivot, -pivot):
                    metrics["transitions"] += 1
                    if visit(assign(formula, lit)):
                        answer = True
                        break

        cache[formula] = answer
        return answer

    try:
        answer = visit(normalize(clauses))
        status = "completed"
    except LimitReached as exc:
        answer = None
        status = "limit_" + str(exc)

    return answer, status, metrics, time.perf_counter() - start

for n in SIZES:
    for i in range(INSTANCES):
        clauses = [
            tuple(
                rng.choice((-1, 1)) * rng.randint(1, n)
                for _ in range(3)
            )
            for _ in range(round(4.3 * n))
        ]

        baseline_start = time.perf_counter()
        witness, baseline = solve_counted(n, clauses, "first")
        baseline_seconds = time.perf_counter() - baseline_start
        baseline_sat = witness is not None

        answer, status, metrics, seconds = symbolic_sat(clauses)

        if status == "completed" and answer != baseline_sat:
            raise AssertionError(f"Mismatch at n={n}, instance={i}")

        if witness is not None and not verify(n, clauses, witness):
            raise AssertionError("Invalid DPLL witness")

        if n <= 10:
            oracle = any(
                verify(n, clauses, a)
                for a in itertools.product((False, True), repeat=n)
            )
            if oracle != baseline_sat:
                raise AssertionError("Exhaustive oracle mismatch")

        row = {
            "n": n,
            "instance": i,
            "status": status,
            "sat": baseline_sat,
            "dpll_calls": baseline["calls"],
            "dpll_seconds": round(baseline_seconds, 6),
            "symbolic_states": metrics["states"],
            "cache_hits": metrics["cache_hits"],
            "transitions": metrics["transitions"],
            "symbolic_seconds": round(seconds, 6),
            "verified": status == "completed"
        }

        results.append(row)

        print(
            f"n={n:2d} | case={i:2d} | {status:15s} | "
            f"DPLL={baseline['calls']:6d} | "
            f"EFSA={metrics['states']:6d} | "
            f"hits={metrics['cache_hits']:5d} | "
            f"verified={row['verified']}",
            flush=True
        )

with open("efsa-results.json", "w", encoding="utf-8") as f:
    json.dump({
        "seed": SEED,
        "max_states": MAX_STATES,
        "max_seconds_per_symbolic_instance": MAX_SECONDS,
        "results": results
    }, f, indent=2)

completed = [r for r in results if r["verified"]]
print("\n=== FINAL REPORT ===")
print("Experiments:", len(results))
print("Completed and verified:", len(completed))
print("Limited:", len(results) - len(completed))
print("DPLL calls:", sum(r["dpll_calls"] for r in completed))
print("EFSA unique states:", sum(r["symbolic_states"] for r in completed))
print("Cache hits:", sum(r["cache_hits"] for r in completed))
print("Results: efsa-results.json")
print("No general polynomial-time bound established.")
