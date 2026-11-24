# M15 (24 November 2026) — Bellman–Ford as an exact Boolean difference-constraints SAT solver

**Author:** Charalampos Nadiotis / PELAOS Tech  
**Status:** Restricted-class theorem with implemented solver and finite-oracle CI. **No proof of P=NP, P!=NP, RH, or GRH.**

## 1. Research objective

Use the **Bellman–Ford shortest-path algorithm** rigorously in the existing SAT research program. Its known guarantee is polynomial-time feasibility testing of a system of difference constraints. It does not solve arbitrary SAT, because a generic disjunction cannot be represented as a single difference inequality. The repository already has a general 2-SAT strongly-connected-components solver with a better linear-time bound; M15 provides an independently checkable negative-cycle UNSAT witness, not a stronger complexity result.

## 2. Exactly supported CNF grammar

Let a CNF F have n explicitly named Boolean variables. First remove duplicate literals within each clause and remove tautological clauses containing a variable and its negation. For each remaining clause, accept only:

- the empty clause (contradiction),
- a positive or negative unit literal x_i or NOT x_i,
- a mixed-sign binary implication clause (NOT x_i OR x_j), equivalent to x_i <= x_j.

The two-literal clause (x_i OR x_j) and the two-negative clause (NOT x_i OR NOT x_j) do **not** belong to the difference-constraint grammar. A wider non-tautological clause does not either. The solver returns **unrecognized**, not SAT or UNSAT, on an unsupported formula, even when the formula is independently trivial.

## 3. Exact graph construction

Introduce integer-valued potentials d_0,d_1,...,d_n. Interpret x_i=d_i-d_0. A weighted directed edge (u,v,c) represents the inequality

\[
d_v-d_u\le c.
\]

For each variable i introduce bounding edges

\[
(0,i,1),\qquad (i,0,0).
\]

These encode 0 <= d_i-d_0 <= 1.

For a positive unit x_i add (i,0,-1), forcing d_i-d_0=1. For a negative unit NOT x_i add (0,i,0), forcing d_i-d_0=0. For an implication (NOT x_i OR x_j) add (j,i,0), forcing d_i-d_0 <= d_j-d_0. For an empty clause add the explicit negative-weight self-loop (0,0,-1).

The edge count is bounded by 2n+m after deduplication; there are n+1 vertices. Introduce an implicit super-source with weight-zero edges to every vertex by initializing every Bellman–Ford distance to zero.

## 4. Theorem M15.1 (soundness, completeness, polynomial bit complexity)

For an explicitly encoded CNF F satisfying the grammar in Section 2, Bellman–Ford detects a negative-weight cycle if and only if F is unsatisfiable. If no negative cycle exists, its integer shortest-path distances recover a Boolean satisfying assignment

\[
x_i=d_i-d_0\in\{0,1\}.
\]

The algorithm runs in O((n+1)(2n+m)) relaxations and polynomial bit complexity on this restricted class.

**Proof.** Each accepted clause was converted into an equivalent inequality under Boolean assignments, as shown by its truth table. The added bounding inequalities ensure that any *integer* feasible potential solution has every difference d_i-d_0 in {0,1}. Conversely every Boolean assignment that satisfies F, extended with d_0=0 and d_i=x_i, satisfies all graph inequalities. The standard difference-constraints theorem establishes that a finite system of inequalities d_v <= d_u+c is feasible over the reals if and only if its weighted graph has no negative-weight directed cycle. Because all edge weights are integers, the Bellman–Ford distances from a super-source are integers, so the bounding constraints convert the feasible real system into a Boolean model without any integrality gap. If a negative cycle exists, adding its edge inequalities yields 0 <= sum(c)<0, contradiction, and thus proves UNSAT. If it does not, Bellman–Ford gives feasible integer distances, hence a satisfying Boolean assignment. The graph has n+1 vertices and O(n+m) edges; standard Bellman–Ford needs O(VE) relaxations. The absolute distance and certificate lengths are polynomially bounded because weights are in {-1,0,1} and feasible simple shortest paths have O(n) edges. The input-count and output-size conventions are explicit, so bit complexity is polynomial. QED.

**Negative-cycle certificate:** the solver returns ordered graph edges (u,v,w) that form a directed cycle whose total weight is negative. The source construction makes each edge an independently verifiable inequality, so summing them is a short contradiction certificate for this recognized grammar.

## 5. Implication example and scope

The CNF

\[
F=(x_1)\land(\neg x_1\lor x_2)
   \land(\neg x_2\lor x_3)\land(\neg x_3)
\]

forces x1=1, x2>=x1, x3>=x2, x3=0, a contradiction. Its graph includes (1,0,-1), (2,1,0), (3,2,0), and (0,3,0), which form the negative cycle

\[
0\rightarrow3\rightarrow2\rightarrow1\rightarrow0
\]

of total weight -1.

Removing the final negative unit permits x1=x2=x3=1, and Bellman–Ford constructs such a witness.

## 6. Crucial limits: SAT vs #SAT vs P=NP

- Bellman–Ford decides this **restricted** CNF class in polynomial time. In fact the established 2-SAT algorithm already handles a larger class in O(n+m).
- The method by itself **does not count satisfying assignments**. An empty formula in two variables has four models; the valid implication (NOT x1 OR x2) leaves three models. Both are feasible difference systems and Bellman–Ford merely finds a witness.
- Hence M11's zeta exponent S(F)=#SAT(F) is **not** obtained by running Bellman–Ford, and the Riemann Hypothesis is not required for the decision proof.
- Arbitrary 3-SAT contains clauses outside the accepted grammar. Encoding an exponentially large implicit search-state graph and running Bellman–Ford would still cost exponential time. No conclusion for general P vs NP follows.
- For soundness, the production solver checks the returned assignment against the original CNF. For unsupported input, the graph result is never substituted for a general SAT decision.

## 7. Reproducibility record

- \`bellman_ford_boolean_sat.py\`: integer potential graph construction, Bellman–Ford relaxation, ordered negative-cycle recovery, verified Boolean model.
- \`test_bellman_ford_boolean_sat.py\`: independent exhaustive truth-table tests, cross-checks against the existing SCC-based 2-SAT solver, explicit cycle checks, unsupported clause rejection, seeded variable permutations and a 350-variable implication-chain case.
- \`structural_hybrid_sat.py\`: conservative integration, after affine recognition and before general graph fallback.
- \`.github/workflows/m15-bellman-ford.yml\`: automated regression and Python compilation gate.

The initial dedicated M15 run **45349679396** passed 11 tests before portfolio integration. Subsequent changes must be judged by the workflow on their exact commit; do not infer green from a previous run. Executed tests demonstrate finite agreement and regressions, not a general proof beyond the theorem above.

## 8. Future experiment

Integrate Bellman–Ford as a fast *decision-only* residual checker alongside M14's linear-form-rank counting. Count and decision must remain separate: a polynomial SAT decision routine cannot automatically be treated as an exact model counter.

**References:** Bellman (1958), *On a Routing Problem*, Quarterly of Applied Mathematics; established shortest-path/difference-constraints theorem; the repository's existing \`sat.py\` SCC-based 2-SAT baseline.
