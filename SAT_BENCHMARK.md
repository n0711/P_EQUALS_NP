# Deterministic SAT branching benchmark

Run:

```sh
python -m unittest -v test_sat.py test_sat_benchmark.py
python run_sat_benchmark.py --seed 20261031 --variables 10 --instances 20 --clauses 35 > benchmark-results.json
```

The baseline selects the first literal from the shortest clause, as in `sat.py`. The comparator selects the most frequent variable across remaining clauses, breaking ties by smallest variable number, then selects the more frequent polarity, preferring positive on ties. Both use the same unit propagation and recursive exhaustive branching.

The script generates seeded random 3-literal CNFs (possibly with repeated variables or complementary literals), checks solver agreement and emits JSON for each instance. The tests check both strategies against complete assignment enumeration for small formulas, with a fixed seed. Counts are recursive calls, attempted branches and unit propagation steps, **not** wall-clock speed, model inference cost, or mathematical complexity bounds. The solver remains worst-case exponential. This is a conventional deterministic heuristic, **not an implemented AI model**.

The linked video in `VIDEO_AI_SAT_RESEARCH.md` remains an unverified research lead. Do not interpret finite benchmark outcomes as a proof of P = NP.
