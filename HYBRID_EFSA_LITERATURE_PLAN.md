# Hybrid symbolic SAT research: literature comparison and falsifiable milestone

Date: 2026-10-31
Status: research proposal; **not** a proof of P=NP.

## Baseline evidence
The user's local EFSA run reported 40/40 completed SAT/UNSAT agreement checks on seeded random 3-CNF with n=8,10,12,14,16 (8 each); DPLL recursive calls=388, symbolic states=853, memoization cache hits=2. These are different work units, so the aggregates do not show a speedup. Output was shown in chat, not independently reproduced on this branch; raw JSON is not committed. Exhaustive oracle checks covered n<=10 only, and correctness on general CNF requires separate proof.

## Related approaches and lessons
- DPLL: exact recursive branching/propagation. Existing repository baseline; exponential worst-case.
- CDCL: conflict learning, two-watched literals, restart strategies; verified implementations exist. Add clause learning only with a sound invariant and checked UNSAT evidence; never conflate efficiency with a polynomial worst-case bound. https://pmc.ncbi.nlm.nih.gov/articles/PMC6044257/
- OBDD, d-DNNF, knowledge compilation: shared subgraphs can make queries tractable *after* compiling, but compilation size and construction cost must count. Darwiche & Marquis, JAIR 17 (2002). https://doi.org/10.1613/jair.989
- Structural decompositions: separator/component caching and bounded-width dynamic programming can deliver parameterized guarantees but do not imply polynomial time for arbitrary unbounded-width formulas.
- Competitive exact solvers: compare against Kissat/CaDiCaL as external benchmarks, not proofs. SAT Competition 2024: https://satcompetition.github.io/2024/results.html
- Open problem statement: https://www.claymath.org/millennium/p-vs-np/

## Proposed hybrid design (not implemented)
1. Normalize and simplify CNF soundly (unit propagation; duplicate-clause removal; tautological-clause removal).
2. Split disconnected variable-clause incidence components; solve independently and combine SAT decisions. This is an *exact* semantic decomposition: F1 AND F2 is SAT iff each component is SAT.
3. Canonicalize residual CNF and memoize exact, completed answers. Record cost of canonicalization and memory.
4. Compare fixed deterministic branching with an occurrence heuristic. Optionally implement a separate checked CDCL baseline; don't merge learned-clause context into cache keys without proving correctness.
5. On small instances compare to exhaustive enumeration. On larger cases check satisfying witnesses and independently verify UNSAT proof certificates when available. Agreement between two solvers is not an independent UNSAT certificate.
6. Track wall time, peak RSS, residual-state count, cache hits, component splits, input bit length and completed vs limited instances.

## Measurable next milestone
Implement component decomposition + memoization with regression tests:
(a) disjoint SAT+SAT => SAT; (b) SAT+UNSAT => UNSAT;
(c) equivalent renamings; (d) contradictory units and empty clauses;
(e) random general CNF <= 12 variables against exhaustive oracle;
(f) adversarial formula families and per-case time/memory budgets.

Measure cache-hit fraction, component decomposition frequency, full processing time, and peak memory on 16 GB RAM with no GPU requirement. Publish every input seed and raw result. The first hypothesis is *empirical*: component decomposition lowers median state visits for some structured families vs the current EFSA, not universally.

## Precise proof obligation
For arbitrary encoded CNF F of bit length N, a fixed deterministic algorithm must terminate, decide SAT correctly, and perform at most C*N^k bit operations for universal constants C and k. Account for constructing, recognizing, and evaluating compressed states, all memory operations, preprocessing, and any external inference. A small explicit control graph with exponentially many register valuations does not suffice. Successful tests cannot imply this uniform bound.
