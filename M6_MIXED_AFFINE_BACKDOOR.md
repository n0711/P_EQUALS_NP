# M6: Exact mixed affine-CNF backdoor search and graph stress testing

**Author:** Charalampos Nadiotis, PELAOS Tech  
**Date:** 7 November 2026  
**Evidence state:** mathematical reduction explained, source code/tests pushed, CI verification tracked separately.  
**Claim boundary:** no proof of P = NP, no new general complexity result, no claimed solver speedup.

## The research question

Previous M5 recognized only formulas where *every* clause belonged to a supported complete XOR block. Practical formulas may contain many affine constraints mixed with a few genuinely non-affine clauses. Can we exploit that algebraic structure without silently treating the remaining clauses as satisfied?

The answer is a precisely scoped **existing-style strong-backdoor method**, implemented here for reproducibility. Relevant prior art: Ryan Williams, Carla P. Gomes, Bart Selman, *Backdoors To Typical Case Complexity*, IJCAI 2003, https://ijcai.org/proceedings/2003/167; Schaefer, *The Complexity of Satisfiability Problems*, STOC 1978, https://doi.org/10.1145/800133.804350. We do not claim priority for backdoor search or Gaussian elimination.

## Exact extraction

Normalize a finite CNF formula F by removing tautologies, repeated literals and duplicate clauses, without changing its models. Group clauses by the unsigned set of variables (support).

For each support S of k=1,2,3 variables, a complete parity block has exactly 2^(k-1) clauses, one for each assignment of fixed excluded parity. Replace that block with the equivalent single XOR equation over GF(2); leave **all other clauses** untouched. The result is

    F = A AND R

as a semantic equivalence, where A is a conjunction of affine equations and R is the unrecognized residual CNF. Both constraints may share variables. The code extracts only blocks recognizable in polynomial time and does not claim to identify every affine representation.

Let B be the distinct variables appearing in R and define r=|B|, measured **after** extraction. This is an explicitly constructed affine backdoor: after assigning any truth values to B, all clauses of R are decided and only the affine equations of A remain.

## Theorem: exactness and explicit parameterized upper bound

For explicit input bit length N that includes all variable slots and output assignments, the algorithm (i) extracts supported XOR blocks, (ii) recursively branches on residual-CNF variables, (iii) detects unit implications from both CNF and GF(2) row reduction, (iv) at a branch satisfying R, solves the remaining system A, and (v) verifies the returned model against the original F.

**Theorem.** The unbounded abstract algorithm returns SAT precisely when F has a satisfying assignment and UNSAT otherwise. Its total worst-case bit operation count is poly(N) * 2^r, with r the number of distinct variables in unrecognized residual clauses after polynomial extraction.

**Proof.** Every extracted block is equivalent to an XOR equation, hence F and A AND R have identical solutions. Assign every variable in B. Every clause of R then evaluates true or false. If any is false the branch cannot contain a model; if all are true, extending the assignment to satisfy A is a GF(2) linear-feasibility problem solvable in polynomial bit time by elimination. A satisfying model of F restricts to one of the 2^r possible assignments of B, whose affine extension will be accepted. Conversely, an accepted assignment satisfies both A and R, hence the original F. The implementation's unit and linear implications are logical consequences of the current branch and do not remove any possible model. The complete binary branching tree on B has at most 2^(r+1)-1 nodes, and extraction, simplification, Gaussian elimination, bookkeeping and verification have polynomial cost per node. Therefore total cost is poly(N)2^r. QED.

**Corollary.** If the chosen extraction produces r = O(log N), this algorithm has a polynomial bound on that explicitly restricted class. Nothing proves r = O(log N) for every CNF: a general CNF may leave r=n.

The algorithm uses GF(2) elimination repeatedly to detect contradictions and derive singleton equations. The reduced row-echelon operations are standard. Each returned SAT model is checked against the original clauses. Resource-limit status limit_calls is **undecided**, not UNSAT. Python interpreter recursion/memory limits are practical boundaries separate from the abstract theorem.

## Implemented infrastructure

- mixed_affine_sat.py - exact affine extraction, residual CNF search, matrix elimination and evidence metrics.
- test_mixed_affine_sat.py - standalone brute-force truth-table oracle plus mixed regression families, parity contradictions, renaming, and limits.
- run_m6_backdoor_benchmark.py - deterministic connected cubic parity graphs with added 4-literal *non-affine* clauses, pigeonhole and graph-coloring controls; isolated DPLL, separator, mixed solver processes; input SHA-256, bounded time and recursive calls, raw JSON.
- .github/workflows/sat-research-verification.yml - CI test and artifact generation.

The graph-theory component uses the M5 cubic graph construction: one Boolean variable per graph edge, parity equations at vertices, and optional general clauses. The source graph and its Boolean primal graph are different mathematical objects; their vertices and metrics must not be conflated. An odd total charge proves the affine subsystem inconsistent, even when the resulting CNF has connected incidence and primal graphs.

## Experiments and falsifiable hypotheses

Hypothesis H6.1: exact affine extraction reduces the number of *searched* Boolean variables on mixed parity-plus-general CNF instances. This can be checked directly by extracting r and counting branches.

Hypothesis H6.2: the mixed solver has lower elapsed time on some high-width, parity-dominated instances than the current pure DPLL or separator search. **This is an empirical hypothesis, not a claim of verified speedup.** Record timeouts, machine conditions, trials and variation.

Hypothesis H6.3: there exist connected, non-affine CNFs with r=n for which the algorithm does not reduce the worst-case exponential search. Exhibit and record such instances; this is a valid falsification of an unrestricted polynomial bound on this method.

Benchmark outcomes include completed, limit_calls, timeout and error; only completed SAT/UNSAT decisions count as decisions. Models are independently checked. Expected outcomes for Tseitin benchmarks follow parity arithmetic, not solver agreement. Graph min-fill width is only an upper bound on treewidth, and degeneracy only a lower bound.

## Reproduction

    python -m unittest -v test_mixed_affine_sat.py
    python -m unittest -v test_sat.py test_frontier_sat.py test_component_sat.py test_graph_separator_sat.py test_structural_hybrid_sat.py test_mixed_affine_sat.py test_proof_obligations.py
    python run_m6_backdoor_benchmark.py --quick --max-calls 2500 --timeout-seconds 3 > m6-results.json
    cd paper
    xelatex structural-sat-milestones.tex
    xelatex structural-sat-milestones.tex

**Before publication:** record exact successful/failed CI run IDs, test counts and artifact digests in RESEARCH_MILESTONES.md. Do not substitute anticipated outcomes for verified runs.

## New research gate after M6

1. Compare CNF-based clause support extraction to stronger polynomial extraction schemes, accounting for discovery cost and model equivalence.
2. Investigate overlapping parity systems and graph separators simultaneously, with a proof that a decomposition respects residual XOR coupling.
3. Run scaling experiments on connected non-affine CNFs, and report counterexamples rather than only favorable samples.
4. Reconcile raw benchmark evidence and the XeLaTeX working paper before making publication claims.

All milestones are cumulative contributions to a reproducible research program, not a resolution of P versus NP.
