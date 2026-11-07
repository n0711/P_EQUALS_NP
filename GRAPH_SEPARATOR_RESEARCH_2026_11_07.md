# Graph Separator SAT - exact cutset conditioning prototype

Author: Charalampos Nadiotis / PELAOS Tech  
Date: 7 November 2026  
Status: prototype and bounded structural result. **Neither a proof of P = NP nor a claim of mathematical priority.**

## Algorithm and graph-theory infrastructure

Given a CNF formula F, normalize duplicate literals/clauses and discard tautologies. Construct its *primal graph*: one vertex per variable occurring in the residual formula, with an undirected edge for every pair of variables appearing in a common clause. A clause induces a clique. The graph is rebuilt after every substitution and unit propagation.

The exact solver in graph_separator_sat.py:
1. Propagates forced unit literals. An empty clause proves the current branch UNSAT.
2. Finds connected components of the primal graph and solves disjoint subformulas independently (AND decomposition).
3. For a connected graph, searches deterministically for a separating vertex, then for a separating pair if permitted by pair_scan_limit. Among candidates of the same size it minimizes the largest residual graph component.
4. Enumerates every Boolean assignment to the selected separator (OR conditioning) and recursively solves the restricted formula.
5. If no eligible separator is found, branches on the most frequent residual variable, breaking ties by smallest variable ID.
6. Memoizes completed residual-CNF answers, including a partial witness for a satisfiable residual. It constructs and verifies the final witness against the original CNF.

The pair_scan_limit skips expensive *separator discovery*, not SAT branches. All fallback branches remain exhaustive. An optional max_calls ceiling returns status=limit_calls and **does not return a SAT/UNSAT decision**. Without that limit, the abstract algorithm is complete, although the Python program remains subject to runtime memory and interpreter limits.

This is an implementation of ideas in exact cutset conditioning and AND/OR search, not an unprecedented complexity algorithm. References:
- Dechter and Mateescu, [AND/OR Cutset Conditioning](https://ijcai.org/proceedings/2005/220), IJCAI 2005.
- Mateescu and Dechter, [A Comparison of Time-Space Schemes for Graphical Models](https://ijcai.org/proceedings/2007/378), IJCAI 2007.
- Ganian and Szeider, [New width parameters for SAT and #SAT](https://doi.org/10.1016/j.artint.2021.103460), Artificial Intelligence 2021.

## Exactness theorem

Let S be a set of variables and let F|alpha be the formula obtained by assigning alpha in {0,1}^S, deleting satisfied clauses and removing falsified literals.

**Theorem.** F is SAT if and only if there exists alpha in {0,1}^S such that every connected component of the primal graph of F|alpha defines a satisfiable subformula (provided no empty clause appears).

**Proof.** Substitution preserves satisfiability among extensions of alpha. If F has a satisfying complete assignment, its restriction alpha to S satisfies this condition, and every component is satisfiable under the original assignment. Conversely, with fixed alpha, distinct components have pairwise disjoint remaining variables. Independently satisfying their respective clauses and adjoining alpha yields one satisfying assignment for F. All 2^|S| separator assignments are examined unless a satisfying extension is found. Unit propagation preserves equivalence, memoized residuals have identical remaining constraints, and fallback branching covers both truth values. Induction on the number of unassigned variables yields exact SAT/UNSAT decisions on every finite input with unlimited calls. QED.

**Restricted complexity proposition.** If a polynomial-time discovered separator S of size at most s leaves, under every assignment alpha, components with at most b variables, each independently solved by DPLL, then full decision and witness reconstruction cost at most poly(N)*2^{O(s+b)} for explicit input size N. Consequently, s+b=O(log N) yields a polynomial bound on that restricted family. This is an upper bound for a *separator followed by component solving*; it does not assert that the greedy separator used by this implementation always finds such an S, nor that arbitrary CNF admits this property. Its unrestricted worst case remains exponential and its memoization space can also be exponential. Separator construction, repeated graph searches, memo-key normalization and witness output have computational costs that must be counted.

## Reproducible finite validation

Commands:

    python -m unittest -v test_graph_separator_sat.py
    python run_graph_separator_benchmark.py > graph-separator-results.json

Local Python 3.13.5 run on 7 November 2026: 9 unittest methods passed, with 900 seeded small-CNF trials (n=0..8, 100 per n) checked against an independent full truth-table oracle, plus 210 renaming invariance cases. Every tested satisfiable output was verified against its input. These finite checks do not prove the general implementation bug-free, or any polynomial worst-case bound.

The benchmark evaluates 18 generated instances: articulation-star gadgets, two-vertex-cut gadgets, exhaustive dense UNSAT constraints, and seeded random 3-CNFs. All 18 completed and agreed with the repository DPLL SAT/UNSAT baseline. Representative *graph algorithm recursive call counts* (not directly comparable with baseline DPLL recursion or elapsed time):

| Family | Variables | Separator cuts | Component splits | Calls |
| --- | ---: | --- | ---: | ---: |
| one_gate(4) | 9 | one 1-variable | 1 | 14 |
| one_gate(12) | 25 | one 1-variable | 1 | 38 |
| two_gates(4) | 10 | one 2-variable | 1 | 10 |
| two_gates(12) | 26 | one 2-variable | 1 | 26 |
| dense_unsat(8) | 8 | none | 0 | 15 |

These are **structural demonstrations**, not evidence of improved runtime. In the same local run, DPLL was faster than the graph-separator prototype on all five representative cases (the graph search pays overhead for inspecting separators). No speedup or novelty is claimed. Timings vary by host and implementation; the benchmark prints raw measurements and seeds.

## Unresolved research gates

1. Measure more connected high-treewidth SAT and UNSAT families, including expansion-like and parity-constraint encodings, rather than only easy gadgets.
2. Add a common work-unit instrumentation scheme before making operational comparisons with DPLL, CDCL, frontier DP and independent solvers.
3. Prove a bound on the **total** cost of generating, finding and evaluating useful compressed states. Demonstrate counterfamilies for every proposed universal polynomial bound.
4. Connect with the author's [earlier ResearchGate manuscript](https://www.researchgate.net/publication/417206732_On_the_Proposition_P_NP_Formal_Foundations_Necessary_Proof_Obligations_and_Research_Directions), preserving the previously published research attribution.
5. Keep the open P versus NP question separate from any subexponential ETH advances.

**Research conclusion:** this commit gives an exact executable graph-separator SAT prototype with falsifiable experiments. It does not settle P versus NP.
