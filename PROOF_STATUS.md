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


## M10-M11 addendum (23 November 2026): why the Riemann-zeta bridge is not a P vs NP proof

The quadratic Boolean encoding of CNF formula F is a parsimonious
field-independent algebraic reduction: each satisfying Boolean assignment
has exactly one zero of the polynomial system over every field, and no
nonsatisfying assignment extends to a zero.

Let S(F) be the number of satisfying assignments. For the corresponding
integer algebraic scheme X_F, the finite-field point count satisfies
\(\#X_F(\mathbb F_{p^r})=S(F)\) for every prime p and r>=1. The point-counting
Euler product therefore gives, for Re(s)>1,

\[
\zeta_{X_F}(s)=\zeta(s)^{S(F)}.
\]

The result is exact and unconditional, and the meromorphic continuation
has a pole of order S(F) at s=1 when S(F)>0. When F is UNSAT, the
zeta function is identically 1. This is a standard algebraic
re-encoding of #SAT, not an efficient calculation of S(F).
Finding the exponent or deciding from the compact polynomial input
whether the pole exists requires solving the same counting/decision
problem. The Riemann Hypothesis constrains the *locations* of zeros
of ordinary zeta, not an algorithm for discovering this exponent.

Consequently neither a deterministic polynomial-time SAT algorithm nor
a superpolynomial lower bound for **all** SAT algorithms follows.
No proof that P=NP, P!=NP, RH or GRH is established.

Details: [M10 proof](RIEMANN_HYPOTHESIS_RESEARCH_2026_11_23.md),
[M11 zeta identity](SAT_ZETA_RIEMANN_RESEARCH_2026_11_23.md),
[bounded code and test](zeta_sat.py), and the
[updated research manuscript](paper/structural-sat-milestones.tex).


## M12 addendum (23 November 2026): exact counting for recognized affine formulas

A separate restricted-class theorem extends M11: if a CNF consists
of fully recognized complete XOR clause blocks of width at most
three, it is equivalent to a linear system Ax=b over GF(2).
Gaussian elimination computes its rank r in polynomial bit time,
and the number of satisfying assignments is 0 if inconsistent,
or 2^(n-r) if consistent, where n includes unconstrained variables.

Thus the scheme's arithmetic zeta function is 1 in the inconsistent
case, or zeta(s)^(2^(n-r)) in the consistent case. This is
established affine constraint tractability (Schaefer 1978).
The implementation returns an explicit "unrecognized" outcome
for formulas outside this grammar, not a guessed #SAT count.

**Unfulfilled general obligation remains unchanged:** neither a
deterministic polynomial-time algorithm for arbitrary CNF-SAT
nor a superpolynomial lower bound applying to *every* possible
polynomial-time SAT algorithm has been provided.

M12 mathematical and reproducibility record:
[AFFINE_ZETA_M12_2026_11_23.md](AFFINE_ZETA_M12_2026_11_23.md).


## M13 addendum (23 November 2026): tractable non-affine cutset family, not general SAT

The M13 exact cutset counter sums the model counts for disjoint
assignments of a *supplied*, logarithmically small variable separator.
For each separator assignment, disjoint residual components multiply
their counts; the algorithm uses M12 rank counting for fully
recognized affine components and exhaustive counting only for
residual components of logarithmic variable size.

In the explicit-input convention this is polynomial time on
instances satisfying the checked restrictions, even if the original
formula is not affine. For example, the connected CNF family
`F_k=AND_i(s OR a_i OR b_i OR c_i)` has exactly
`8^k + 7^k` models under this method, and this count is not
a power of two. The arithmetic zeta exponent is exactly that count.

The implementation returns **unrecognized** for a cutset that is
too large or for an unsupported residual component, and makes no
SAT/UNSAT claim in those cases. The cutset is supplied, not
discovered for arbitrary formulas.

This does **not** prove P=NP or P!=NP. The unrestricted
worst-case proof obligation remains unfulfilled. See the
[M13 mathematical record](CUTSET_ZETA_M13_2026_11_23.md).

## M15 addendum (24 November 2026): Bellman–Ford does not prove P versus NP

Bellman–Ford decides feasibility of a difference-constraint graph in O(VE)
time and returns a negative cycle when the constraints are inconsistent.
For the restricted Boolean CNF class consisting of unit clauses and
mixed-sign implication clauses `(-i,j)`, adding Boolean bounding edges
makes each supported clause equivalent to an integer difference
inequality. A negative-weight cycle then certifies UNSAT, and integer
shortest-path distances produce a verified Boolean satisfying assignment.

This restricted language is a **subset of 2-SAT**, which is already
known to be solvable in linear time by the existing SCC implementation.
General disjunctions `(i,j)` and `(-i,-j)`, as well as arbitrary
3-SAT clauses, are not accepted by the Bellman–Ford encoding.
An unsupported input is reported as `unrecognized`, not assigned a
fabricated decision. Bellman–Ford also does **not** count solutions
or compute the arithmetic-zeta exponent in the M11 identity.

Thus there is still no general deterministic polynomial-time SAT
algorithm or superpolynomial lower bound for all possible SAT
algorithms. See [M15 theorem and proof](BELLMAN_FORD_M15_2026_11_24.md).
