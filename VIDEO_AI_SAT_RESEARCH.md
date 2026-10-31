# Video research lead: AI-assisted SAT algorithm discovery

**Repository:** n0711/P_EQUALS_NP  
**Date:** 31 October 2026  
**Reference supplied by researcher:** https://youtu.be/feMnLlt_C7Y  
**Evidence status:** Video transcript/content has **not** been independently verified in this review. The video is a research lead, not evidence of P = NP.

## Relationship to existing work

This note extends the exploratory direction in [RESEARCH_NOTES.md](RESEARCH_NOTES.md), [SAT_EXPERIMENTS.md](SAT_EXPERIMENTS.md), and [PROOF_STATUS.md](PROOF_STATUS.md). The existing Python and MATLAB 2-SAT implementations are polynomial-time **restricted-case baselines**, while general DPLL has exponential worst-case behavior. Nothing here establishes a general polynomial-time SAT algorithm.

## Proposed experiment: AI-generated heuristics, exact verification

A language model or other heuristic generator may propose:
- deterministic variable-ordering rules for CNF SAT;
- sound preprocessing simplifications with independently checkable equivalence certificates;
- candidate structural lemmas and counterexamples.

For every proposed method, independently verify:
1. **Soundness:** Any claimed satisfying assignment evaluates to true under the input formula.
2. **Completeness:** SAT/UNSAT outputs agree with exhaustive enumeration on small instances and trusted exact solvers on larger instances. Finite agreement is experimental evidence, not a universal proof.
3. **Determinism:** Fix a reproducible inference setup; if proposals use randomness, record seeds and distinguish a stochastic heuristic from a deterministic decision algorithm.
4. **Total accounting:** Track input bit length, preprocessing, model inference, token/computation cost, branching nodes, memory, checking cost and runtime. Exclude no work required by the algorithm.
5. **Adversarial validation:** Test crafted unsatisfiable instances, satisfiable instances with narrow witnesses, reordered clauses/variables, and scaling families; report failures.
6. **Generality:** Keep 2-SAT and restricted families separate from arbitrary CNF-SAT.

## Mathematical proof obligation

For arbitrary encoded CNF formula F of length N, an unconditional P = NP result via SAT requires a fixed deterministic decision procedure A and constants C,c such that:

- A(F) halts and returns SAT iff F is satisfiable, otherwise UNSAT;
- total worst-case bit-operation cost is at most C N^c for **every** F.

Measured trends, average-case improvements, neural heuristics, a short generated proof sketch, or a solver that succeeds on benchmark collections do not prove this bound.

## Immediate bounded contribution

Start with a **documented benchmark protocol** comparing the existing general DPLL implementation against a separately specified deterministic heuristic, while retaining exhaustive oracle comparisons for small n. Report dataset construction, machine conditions, seeds when relevant, and exact verification. Before implementing a novel heuristic, state its invariants and the claimed scope.

## Reference limitations

The linked YouTube video was supplied by the researcher. Its precise claims, title, and transcript have not been authenticated in this change. Do not cite it as support for algorithmic or mathematical claims without checking the primary material and timestamps.

**Conclusion:** A potentially useful inspiration for SAT search research; **no proof of P = NP** is added by this note.
