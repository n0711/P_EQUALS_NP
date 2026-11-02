"""Enumerate exact subset IDs for fixed-order residuals of AND_i(x_i OR y_i).

This is NOT a SAT solver and does not materialize residual Boolean formulas.
"""
import json
import time
import tracemalloc

def measure(k):
    if not 0 <= k <= 20:
        raise ValueError("k must be in [0, 20] to bound resource use")
    expected = 1 << k
    tracemalloc.start()
    start = time.perf_counter()
    states = set()
    for mask in range(expected):
        states.add(mask)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    actual = len(states)
    assert actual == expected
    return {"k": k, "expected": expected, "unique": actual,
            "elapsed_seconds": elapsed, "peak_mib": peak / (1024 * 1024)}

if __name__ == "__main__":
    print(json.dumps([measure(k) for k in (4, 8, 12, 16, 18, 20)], indent=2))
