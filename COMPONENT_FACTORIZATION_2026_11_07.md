# Exact component factorization for SAT and #SAT

Author: Charalampos Nadiotis, PELAOS Tech
Date: 7 November 2026
Status: Exact structural milestone, not a proof of P = NP; standard decomposition, no novelty claim.

## Research continuity and source verification

The repository already cites the author's ResearchGate manuscript [On the Proposition P = NP: Formal Foundations, Necessary Proof Obligations, and Research Directions](https://www.researchgate.net/publication/417206732_On_the_Proposition_P_NP_Formal_Foundations_Necessary_Proof_Obligations_and_Research_Directions). The full ResearchGate text and any still-earlier manuscript could not be independently retrieved in this update. This document neither disputes the author's prior publication nor claims to establish priority for a mathematical theorem in that publication.

The November 2026 video https://youtu.be/iw9SZgyahqg describes the October 2026 OpenAI claim. The primary [OpenAI preprint](https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026) claims exact counting of satisfying assignments for fixed-width k-CNF in deterministic polynomial space and time of the form

$$
(n+m)^{O_k(1)} 2^{O_k(n\log\log n/\sqrt{\log n})}.
$$

Its [Lean scope note](https://github.com/openai/math/blob/main/lean/docs/378.md) specifies a weaker formally checked exponent O_k(n (log log n)^2 / sqrt(log n)), plus polynomial factors in the encoded length L. Both bounds are subexponential but not polynomial. A formalization of a statement must also be checked for correspondence with the intended theorem; independent mathematical review matters. The preprint does not establish P = NP.

## Definitions

Let F be a finite CNF over n indexed Boolean variables, written explicitly as a list of clauses. Delete tautological clauses and duplicate clauses, and collapse duplicate literals within clauses. An empty clause makes the formula UNSAT.

Construct the bipartite variable-clause incidence graph: one vertex per variable, one per nontrivial clause, with an incidence edge when a variable occurs in a clause. Let F_1,...,F_r be the nonempty connected-component subformulas, with pairwise disjoint variable sets V_1,...,V_r. Let U be the set of variables in no nontrivial clause.

## Theorem 1 - factorization and exact counting

F is satisfiable if and only if all F_i are satisfiable. Moreover,

$$
\#\operatorname{SAT}(F)=2^{|U|}\prod_{i=1}^{r}\#\operatorname{SAT}(F_i).
$$

Proof: Every non-tautological clause belongs to one component. A complete assignment satisfies F exactly when its restriction to each V_i satisfies F_i. Because the V_i are pairwise disjoint, component satisfying assignments can be combined uniquely. Variables in U have independent arbitrary truth values, contributing 2^|U| choices. This is a bijection from the satisfying assignments of F to the Cartesian product of the component satisfying-assignment sets and assignments on U. The product formula and SAT equivalence follow. QED.

Corollary: A single UNSAT component establishes global UNSAT. Combining one valid witness per component and arbitrary values on U yields a global satisfying assignment.

## Theorem 2 - bounded-component time

Let N be the complete explicit representation size, counting n variable slots as well as all encoded clauses, and let b=max_i |V_i| (b=0 if there are no components). In particular, n <= N. This convention matters because the implementation returns a length-n assignment, including values for unused variables. With an alternative succinct encoding where n is binary and may be exponentially larger than its representation, the complexity statement is in n plus input length, not in that succinct bit length alone. Union-find incidence decomposition, normalization and compact variable remapping cost polynomial time in N.

If each F_i is decided by a correct exponential-time DPLL solver, total worst-case bit time is bounded by

$$
T(F)=\operatorname{poly}(N)+\sum_{i=1}^r 2^{O(|V_i|)}\operatorname{poly}(N)
\subseteq \operatorname{poly}(N)2^{O(b)}.
$$

Thus if b=O(log N), the method is polynomial time on that restricted input class. For arbitrary CNF, b can equal n, and no general polynomial bound follows. The Python implementation also inherits interpreter recursion and practical memory limits, which are separate from the mathematical unbounded-machine bound. No new general SAT algorithm is claimed.

## Why this does not settle P versus NP

When the incidence graph is connected, r=1 and the factorization gives no computational improvement. No polynomial-time process is presently proved to decompose every general 3-CNF into polynomially many equivalent pieces with O(log N) variables and polynomial total representation cost.

For an upper bound of the form poly(N) 2^{f(n)}, proving f(n)=O(log N) suffices to make this particular bound polynomial. The OpenAI headline exponent n log log n / sqrt(log n), and the Lean-checked exponent n (log log n)^2 / sqrt(log n), remain superlogarithmic in n. A subexponential exact counter therefore does not by itself imply P = NP.

## Tested implementation

component_sat.py reuses the repository's existing DPLL solver, after normalization and exact variable-component decomposition. It reconstructs and verifies models against the original CNF and does not return a guessed UNSAT status after a resource limit.

Run: python -m unittest -v test_component_sat.py

Local run on 7 November 2026: six unittest methods passed. Coverage included 640 seeded small CNF cases checked against independent exhaustive truth-assignment enumeration, 210 variable-renaming cases, explicit disconnected SAT and UNSAT components, tautologies, duplicate literals, empty clauses and invalid input. The counts are regression evidence rather than a proof of unrestricted runtime or correctness; the general decomposition correctness is argued above, and DPLL is addressed separately in MATHEMATICAL_BASELINE.md.

No measured runtime speedup is claimed, and there is no implemented version of OpenAI's counting algorithm.

## Next falsifiable research milestone

1. Specify a deterministic, polynomial-time exact reduction for every 3-CNF that guarantees at most O(log N) variables per independent component and polynomial output size, or develop a different complete unrestricted polynomial-time algorithm.
2. Search for a concrete counterfamily of connected high-width satisfiable and UNSAT instances. Document any counterexamples instead of suppressing them.
3. Separately account for reductions, component detection, canonicalization, solver calls, witness checking, total bit operations, and space.
4. Obtain the full original ResearchGate manuscript before claiming that any new theorem or program reproduces its results.

The Clay Mathematics Institute still lists P versus NP as unsolved: https://www.claymath.org/millennium/p-vs-np/ .
