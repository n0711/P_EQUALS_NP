# Graph search and the SAT research direction

Working notes for Charalampos Nadiotis / PELAOS Tech, 30 October 2026.
These notes present standard facts and elementary derivations for review. No novelty or resolution of P versus NP is claimed.

## Relationship to the supplied paper

The supplied October 2026 paper, [On the Proposition P = NP: Formal Foundations, Necessary Proof Obligations, and Research Directions](https://www.researchgate.net/publication/417206732_On_the_Proposition_P_NP_Formal_Foundations_Necessary_Proof_Obligations_and_Research_Directions), gives a conditional route through SAT and proposes restricted-family milestones. It contains no executable SAT algorithm. This project supplies a concrete graph-search baseline and separates correctness from state-space size. It does not evaluate the unavailable 2023 argument.

## Correctness arguments for the implemented methods

**BFS.** Before a vertex at distance d is processed, all discovered vertices at smaller distances have been processed. Its undiscovered successors therefore have shortest distance d + 1. Marking a vertex on insertion prevents duplicate queue entries. Parent links reconstruct an actual path of that length. An empty queue exhausts all reachable vertices.

**DFS.** Each discovered vertex has a path from the start through its parent links. A vertex is discovered only once. Each frame eventually scans every outgoing edge unless the goal is found. Thus any reachable goal is eventually discovered on a finite graph. The invariant makes no shortest-path assertion. Frames avoid language-level recursion limits.

**Bidirectional BFS.** Each direction discovers complete distance layers, using reversed edges on the goal side. Before the first intersecting layer, the two discovered balls are disjoint. If their radii are a and b, a start-goal path of length at most a + b would already force an intersection. Expanding a whole layer on one side increases that radius by one. An intersection then gives a path of length at most a + b + 1, while the previous disjointness rules out a shorter path. We inspect the full layer and use its minimum distance sum. The relative sizes of the frontiers do not change this layer invariant.

**A*.** Store the cheapest discovered cost g(v), and order open entries by f(v) = g(v) + h(v). Under admissibility, an open frontier vertex on an optimal route has f at most the optimal goal cost once its optimal prefix is available. Relaxation and reopening preserve such a frontier until the optimal goal cost is obtained. Since h(goal) = 0, selecting a more expensive goal before that frontier would contradict minimum-f selection. Strict improvement prevents equal-cost cycling. On a finite graph with nonnegative integer costs, each finite g value can strictly decrease only finitely many times; the algorithm terminates. This termination observation is not a polynomial bound in the bit length of the weights.

Consistency, h(u) <= w(u,v) + h(v), ensures a vertex's cost is optimal when expanded and avoids reopening. An admissible heuristic can be inconsistent, so the implementation must retain the reopening rule. The tests contain a specific example where removing it would be incorrect.

## A concrete obstruction: a depth heuristic provides no SAT guidance

Suppose a SAT search state assigns the first d of n variables, every edge assigns one more variable at unit cost, and goals are satisfying complete assignments. Then g = d. The proposed heuristic h = n - d is admissible, but

    f = g + h = d + (n - d) = n.

Every generated state has the same priority. This heuristic supplies no discrimination between promising and unpromising assignments; tie breaking determines the order. A complete binary assignment tree contains 2^(n+1) - 1 states. Pruning might avoid much of it, but a polynomial guarantee requires a proof about that pruning. A*'s shortest-path theorem supplies no such bound by itself.

If partial satisfying assignments are accepted as goals, the argument's goal convention changes: h = n - d can then overestimate the distance to a goal and need not be admissible. The goal predicate and heuristic must be specified together.

## A second obstruction: distinct residual formulas can grow exponentially

Consider the simple CNF family

    F_k = AND over i=1..k of (x_i OR y_i).

Assign all x variables first. Let S be the indices for which x_i is false. The residual formula is

    R_S = AND over i in S of y_i.

There are 2^k choices of S. They define distinct Boolean functions over the y variables: if S and T differ, choose j in S but not T (swap the names if necessary), set y_j false, and every other y true. Then R_S is false and R_T true.

Thus a state representation that identifies states only when their residual Boolean functions are equal still has 2^k different states at this level of this fixed variable order. Exact duplicate removal alone does not provide a polynomial bound in encoded formula length, which is O(k log k) with binary variable indices.

This is not a hard SAT family: every residual is satisfiable, and setting all y variables true settles the original formula. A stronger method can stop early, use a different order, or merge states under a weaker decision-preserving relation. The example isolates the limitation of one proposed compression criterion, rather than proving a lower bound for all SAT solvers.

## What a substantive extension must establish

For a SAT-to-search construction on formula F of encoded length N, specify:

1. A state encoding, initial state, successor rule, and goal predicate with explicit bit costs.
2. Why a reachable goal exists exactly when F is satisfiable, and how a witness is recovered if promised.
3. A sound pruning rule: no satisfying completion is lost.
4. Any state equivalence used for merging, with a proof that merging preserves the required answer.
5. A bound on generated states, scanned edges, repeated expansions, stored information, and heuristic computation, all in terms of N.
6. Termination and a correct UNSAT answer when there is no goal.

A clause-variable graph may have polynomial size, but ordinary reachability in that graph is not a SAT decision procedure: reachability does not enforce a single assignment consistent with all clauses. An assignment graph may encode those choices faithfully but have exponential size. The missing theorem must address both correctness of representation and its total computational cost.

## Next measurable milestone

Use a restricted family with a known polynomial algorithm as an independent oracle, for example 2-SAT via its implication graph. Verify a proposed representation and pruning rule on that family before general CNF. Then formulate the exact lemma that would extend the restriction. For graph-search engineering, larger sparse graphs, domain-specific admissible heuristics, and preprocessing amortized over repeated queries are separate measurable targets.

The current deliverables establish a tested implementation baseline, explicit assumptions, reproducible examples, and two limitations of naive SAT extensions. They do not establish a general polynomial-time SAT algorithm.
