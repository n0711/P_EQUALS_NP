# Formal proof record: graph search, SAT, and the P versus NP gap

**Author:** Charalampos Nadiotis (PELAOS Tech)  
**Date:** 30 October 2026  
**Status:** Proven statements below are restricted propositions and a conditional theorem. **No proof of P = NP is established.**

This document distinguishes what can be rigorously proved from what would be required to settle the P versus NP problem. It accompanies [RESEARCH_NOTES.md](RESEARCH_NOTES.md) and the [technical paper](paper/graph-search.tex).

## Definitions

Let SAT denote the language of satisfiable Boolean formulas in a standard finite encoding. A deterministic polynomial-time SAT algorithm is a deterministic algorithm which halts on **every** input formula, correctly answers SAT or UNSAT, and uses at most (O(N^c)) steps for an input of bit length (N), for one fixed constant (c).

## Theorem 1 (conditional route through SAT)

**Statement.** If SAT has a deterministic polynomial-time decision algorithm, then (P=NP).

**Proof.** SAT belongs to NP: a proposed Boolean assignment has polynomial length and can be checked in polynomial time. By the Cook–Levin theorem, every language (L\in NP) has a polynomial-time many-one reduction (r_L) to SAT. Suppose SAT is decided by a deterministic algorithm (A) whose running time is polynomial in its input length. To decide membership (x\in L), compute (r_L(x)), then run (A(r_L(x))). The reduction output length is polynomial in (|x|), so composition remains polynomial time. Thus every (L\in NP) belongs to (P), yielding (NP\subseteq P). Since (P\subseteq NP), equality follows. QED.

**Logical limitation:** This theorem does not exhibit a polynomial-time SAT algorithm. Its antecedent is the missing step, so this is not a proof of the antecedent or of (P=NP).

## Proposition 2 (depth-only A* priorities do not discriminate)

**Statement.** Consider a complete-assignment SAT search tree on (n) variables with a fixed assignment order, one unit-cost edge per variable assignment, and satisfying *complete* assignments as goals. At depth (d), use (h=n-d). Every generated state has the same A* priority (f=n).

**Proof.** Every tree edge has unit cost, hence the cost of the unique root-to-state path is (g=d). Therefore (f=g+h=d+(n-d)=n) for every state. If a satisfying completion is reachable, it must involve exactly (n-d) further assignments, so (h) is a lower bound on the remaining distance; if none exists, the remaining distance is infinite, again making the heuristic admissible. Equal priorities confer no SAT-specific discrimination; tie breaking determines search order. QED.

**Limitation:** The full binary tree has (2^{n+1}-1) states, but this is *not* a lower bound on visits for all algorithms or a proof that A* visits all of them on every instance.

## Proposition 3 (exponentially many distinct residual Boolean functions)

**Statement.** For the CNF family
[
F_k=\bigwedge_{i=1}^{k}(x_i\lor y_i),
]
assign the (x_i) variables before any (y_i). After those (k) assignments, there are (2^k) distinct residual Boolean functions over the (y_i) variables.

**Proof.** Each assignment to the (x_i) determines a subset (S=\{i:x_i=\mathrm{false}\}\subseteq\{1,\dots,k\}\). Substitution simplifies the formula to
[
R_S=\bigwedge_{i\in S}y_i,
]
where the empty conjunction is true. For any two distinct subsets (S,T), choose an index in their symmetric difference and, without loss of generality, let (j\in S\setminus T). Set (y_j=\mathrm{false}) and all other (y_i=\mathrm{true}). Then (R_S) is false while (R_T) is true. Thus (R_S\ne R_T) as Boolean functions whenever (S\ne T). There are exactly (2^k) subsets, hence exactly (2^k) distinct residual functions. QED.

**Limitation:** This easy SAT family does not yield a general complexity lower bound. A solver may choose a different variable order or terminate early. The proposition rules out a polynomial state bound *solely* from merging identical residual functions at this fixed search layer.

## Unfulfilled proof obligation

To turn the research program into an unconditional (P=NP) proof, produce a fully specified deterministic algorithm (A) for **arbitrary** CNF-SAT and prove both:

1. **Soundness and completeness:** for every formula (F), (A(F)=\mathrm{SAT}) if and only if (F) has a satisfying assignment; it halts and returns UNSAT otherwise.
2. **Worst-case bit complexity:** for a fixed (c), there exists a constant (C) such that for every input of encoded length (N), the *total* bit-operation cost, including generating or representing states, successors, pruning, merging, heuristic computation, bookkeeping, and termination, is at most (C N^c).

The current repository contains no proof meeting both obligations. Finite experiments, optimized search on explicit graphs, and conditional implications cannot substitute for them.

## Reproducibility and attribution

The graph-search code and recorded test results remain in [search.mjs](search.mjs), [search.test.mjs](search.test.mjs), and [VALIDATION.md](VALIDATION.md). This proof record is attributed to Charalampos Nadiotis. The mathematical ingredients include established facts; attribution of this document must not be taken as a claim to have discovered those facts or settled an open problem.
