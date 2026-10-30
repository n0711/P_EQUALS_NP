# Mathematical baseline: decidability, 2-SAT, DPLL, and proof boundaries

**Charalampos Nadiotis — PELAOS Tech — 30 October 2026**

**Status:** Proofs in this note concern the specified algorithms and restricted SAT. They do **not** establish that P = NP.

## 1. Notation and input size

Let (F=C_1\land\cdots\land C_m) be a CNF formula over (n) Boolean variables, represented as a list of signed literals. Let (L=\sum_i |C_i|) be the total literal-occurrence count and (N) its complete bit-encoded input length. A polynomial bound in (n+L) is polynomial in (N) when the encoding explicitly lists all variables and clauses. An exponential bound in (n) is not a polynomial guarantee in (N).

## 2. Theorem: polynomial-time 2-SAT

For a clause ((a\lor b)), introduce the implications ((\lnot a\to b)) and ((\lnot b\to a)). A unit clause ((a)) gives ((\lnot a\to a)). A formula with an empty clause is unsatisfiable.

**Theorem.** A 2-CNF formula without an empty clause is satisfiable if and only if no variable (x) and its negation (\lnot x) belong to the same strongly connected component of the implication graph.

**Proof (necessity).** Suppose (x) and (\lnot x) are mutually reachable. Implications along a path preserve truth: if its starting literal is true under a satisfying assignment, its final literal is true. Any Boolean assignment sets exactly one of (x,\lnot x) true. Taking the mutual-reachability path from whichever is true forces the other also to be true, a contradiction.

**Proof (sufficiency).** Contract the strongly connected components to obtain a directed acyclic graph. Negation maps each component to a distinct negated component and reverses implications: an implication (a\to b) has the contrapositive edge (\lnot b\to\lnot a). Process the condensation graph's components in reverse topological order, assigning true to a component whose literals have not been assigned, and false to its negated component (or equivalently use a suitable component-order comparison). The absence of self-negating components makes this assignment consistent. If an implication (a\to b) had (a) true and (b) false, its component order together with the contrapositive would contradict the chosen reverse-topological assignment. Hence every implication is respected, so every original 2-CNF clause is true. QED.

**Complexity.** There are (2n) vertices and (O(L)) directed implication edges. An SCC algorithm using adjacency lists runs in (O(n+L)) graph operations, with (O(n+L)) storage. Constructing and reading the explicit input costs at least its encoded length. On a standard bit-cost model, processing variable indices adds representation-dependent logarithmic factors, still polynomial in (N). This theorem applies to 2-SAT, **not** arbitrary CNF.

## 3. Theorem: recursive DPLL is correct but not proved polynomial

Consider the decision procedure that repeatedly propagates unit clauses, then branches on a remaining literal (\ell), recursively examining both (F|_{\ell=\mathrm{true}}) and (F|_{\ell=\mathrm{false}}). Each restriction removes satisfied clauses and deletes falsified literals. A formula with no clauses is SAT; one containing an empty clause is UNSAT.

**Lemma (restriction).** For a Boolean assignment fixing a literal (\ell) true, the restricted formula (F|_\ell) is satisfiable exactly when (F) has a satisfying extension setting (\ell) true.

**Proof.** A clause satisfied by (\ell) imposes no further constraint and is removed. A clause containing (\lnot\ell) loses its false literal. All other clauses are unchanged. Thus truth under any assignment extending (\ell) is preserved in both directions. QED.

**Theorem (DPLL soundness, completeness and termination).** The above procedure reports SAT if and only if the original CNF is satisfiable and otherwise reports UNSAT; it terminates on every finite input.

**Proof.** Induct on the number of variables not yet fixed. A unit clause must be satisfied in every model, so setting its literal true preserves satisfiability by the restriction lemma. If propagation produces an empty clause, no extension satisfies it. If no clauses remain, the accumulated assignments satisfy the formula. Otherwise choose an unset literal (\ell). Every satisfying assignment sets it either true or false. By the restriction lemma, the original formula is satisfiable if and only if at least one of the two restricted formulas is satisfiable. Both recursive calls strictly reduce the number of unassigned variables, so the induction applies and termination follows. QED.

**Complexity limitation.** With up to two branches per variable, the search tree can contain (2^{n+1}-1) nodes. Straightforward implementations do polynomial work per node, yielding a general upper bound of the form (2^{O(n)}\operatorname{poly}(N)), **not** a polynomial worst-case bound. Clever branching and unit propagation do not remove this proof obligation. Correctness, termination, and empirical speed are distinct claims.

## 4. Why benchmark tests cannot establish P = NP

Even exhaustive experiments on all formulas up to some finite size (N_0) prove only a *finite-domain statement*. For any finite (N_0), an algorithm may work quickly on inputs of length at most (N_0) while growing exponentially beyond that threshold. Inference to all input sizes requires a mathematical invariant and a bound quantified over **every** input length.

## 5. Open target theorem

To resolve P versus NP in the affirmative using this direction, one must produce an **unrestricted CNF-SAT** deterministic solver and establish, for fixed constants (C,c) and every formula of encoded length (N),

[
T(F)\le C N^c,
]

with a total bound including all encoding, state generation, reductions, branches, heuristic computations, and storage operations, plus a proof that the solver returns SAT exactly for satisfiable formulas and UNSAT otherwise.

No argument or code in this repository currently supplies that theorem. Tests and independent review remain necessary for the restricted baselines, but cannot bridge the missing general complexity bound.
