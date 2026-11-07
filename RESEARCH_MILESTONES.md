# P_EQUALS_NP - Research milestone ledger

**Researcher and manuscript author:** Charalampos Nadiotis (PELAOS Tech)
**Last updated:** 2026-11-07
**Scope:** Graph-theoretic and algebraic exact SAT research, with every result labeled by evidence class.
**Status:** No proof of P = NP. This record is a research log, not a priority claim.

## Documentation convention for every milestone

Each new milestone MUST record:
1. **ID / date / question / hypothesis** and prior work or cited literature.
2. **Mathematical result:** definitions, precisely scoped theorem, proof or counterexample, and explicit missing proof obligations.
3. **Implementation:** immutable commit, files, algorithms, input contracts, output and limit semantics.
4. **Experimental protocol:** generator, seeds, baseline, input bit-size convention, machine/runtime, budgets, independently verified output, work metrics and raw artifact.
5. **Verification status:** not run, local pass, CI pass or peer reviewed. Never call a run successful based only on written tests.
6. **Outcome:** hypothesis supported, falsified, inconclusive or pending; limitations and next falsifiable gate.
7. **Paper integration:** precise XeLaTeX subsection and evidence that may be cited. Keep unverified results explicitly provisional.

**No silent rewriting of prior outcomes.** Append a dated correction/amendment if an earlier claim changes. The manuscript source is
[paper/structural-sat-milestones.tex](paper/structural-sat-milestones.tex).
Build with \`cd paper && xelatex structural-sat-milestones.tex && xelatex structural-sat-milestones.tex\`.
The prior graph-search manuscript is separate and remains in \`paper/graph-search.tex\`.

## Milestone index

| ID | Date | Milestone | Theory | Execution / evidence | Manuscript |
| --- | --- | --- | --- | --- | --- |
| M0 | 2026-10-30 | Prior formal P vs NP foundations | Conditional Cook-Levin route, no general proof | Repository ResearchGate citation; original full text not independently checked | Introduction, attribution |
| M1 | 2026-10-30 | BFS/DFS/A*/Dijkstra and graph matrices | Correctness for finite explicit graph under contracts; no polynomial SAT conclusion | \`search.mjs\`, \`search.test.mjs\`, \`VALIDATION.md\` | Background |
| M2 | 2026-11-02 | Clause-frontier dynamic programming | Exactness and \`poly(N) 2^w\` bound; fixed-order exponential residual counterfamily | \`frontier_sat.py\`, \`test_frontier_sat.py\`, \`FRONTIER_COMPLEXITY.md\` | Background, limitations |
| M3 | 2026-11-07 | Incidence-component factorization | SAT iff every component SAT; #SAT product; bounded-component conditional polynomial | \`component_sat.py\`, \`test_component_sat.py\`, PR #4 merged | Section: decomposition |
| M4 | 2026-11-07 | Exact primal-graph separator conditioning | Correct by exhaustive separator assignments plus independent component solving; exponential worst case | \`graph_separator_sat.py\`, \`test_graph_separator_sat.py\`; 9 local methods, 900 oracle cases, 210 renamings; 18 benchmark cases; GitHub Actions passed before this branch's later changes | Section: separator search |
| M5 | 2026-11-07 | Affine recognizer + GF(2) / graph-adversary benchmark infrastructure | Exact equivalence for recognized complete XOR clause blocks, standard Gaussian elimination; connected odd-charge Tseitin contradiction | \`structural_hybrid_sat.py\`, \`graph_research_instances.py\`, \`test_structural_hybrid_sat.py\`, \`run_structural_benchmark.py\`; **CI on M5 head pending verification** | Section: algebraic shortcut, evaluation plan |

## M5 hypothesis and mathematical scope

**Question.** Can an exact graph-oriented solver safely bypass separator branching for CNFs that encode XOR systems, even if their primal graphs are connected?

**Construction.** Group distinct non-tautological clauses by their unsigned variable support of size 1, 2 or 3. If and only if a support contains exactly all \`2^(k-1)\` forbidden assignments with one fixed parity, that group encodes a k-variable XOR equation with the opposite parity. If every group passes, solve the resulting system over GF(2) using deterministic elimination, then verify the reconstructed model against the original clauses. Otherwise use the complete separator solver. This recognizer is conservative: unrecognized affine CNFs may fall back without threatening correctness.

**Proof obligation A (recognition).** A CNF clause over fixed variables is false on exactly the assignment with the opposite values of its signed literals. A complete list of the parity-\`p\` falsifying assignments is true exactly on the parity-\`1-p\` assignments. Conjunction over complete support groups is therefore precisely a system of XOR equations. Gaussian elimination decides and constructs a satisfying assignment in polynomial bit time for explicit input. The fallback solver is exact by M4's invariant. Thus the hybrid is exact as an abstract algorithm, **not polynomial for arbitrary CNF**.

**Proof obligation B (odd-charge graph parity).** For Tseitin constraints on a connected undirected graph, XORing all vertex equations cancels each edge-variable twice, leaving \`0 = XOR_v charge(v)\`. Any odd total charge is contradictory. With even total charge, connected-graph incidence equations have rank \`|V|-1\`, so a solution exists. 3-regular source graphs generate 3-CNF parity constraint blocks.

**Structural measurements.** The min-fill elimination width is an **upper bound** on primal treewidth; degeneracy is a **lower bound**. Neither bound is a lower bound on the runtime of general SAT algorithms. Connectedness and high width are *stress conditions*, not proofs of hardness.

**Experiment matrix.** Deterministically generate cubic Tseitin SAT/UNSAT systems, pigeonhole 3-CNF UNSAT examples, and 3-colorability SAT/UNSAT CNFs. Compare the existing DPLL, the separator solver and the hybrid under separately enforced wall-clock limits. Preserve status \`completed\`, \`limit_calls\` and \`timeout\` and never conflate the latter two with UNSAT. Record tracemalloc allocations but do not call them total RSS. Different solvers' recursive-call metrics are not comparable without normalization.

**Reproduce after checkout:**
\`\`\`sh
python -m unittest -v test_structural_hybrid_sat.py
python run_structural_benchmark.py --quick --timeout-seconds 3 --max-calls 1200 > structural-results.json
python -m unittest -v test_sat.py test_frontier_sat.py test_component_sat.py test_graph_separator_sat.py test_structural_hybrid_sat.py test_proof_obligations.py
\`\`\`

**Current evidence:** M5 code and test definitions are pushed; tests are not evidence of success until local or CI execution is checked. A new PR and its CI result should be recorded in a dated addendum.

## M5 falsification and next gates

- Check whether non-affine connected formulas with high min-fill widths still force exponential search.
- Search adversarial CNFs where the recognizer fails, separator discovery overhead exceeds useful pruning, or memoization grows rapidly.
- Add finite independent correctness checks on every SAT witness, crosschecks on UNSAT decisions and certificate verification when available.
- Establish explicit **worst-case total bit cost** for all input lengths before any P = NP claim. No such bound is currently known in this repository.
- Preserve distinct categories: **previously published research**, **standard theorems**, **new implementation**, **new measured observations**.

## Prior art and manuscript citations

- Thomas J. Schaefer, *The Complexity of Satisfiability Problems*, STOC 1978, https://doi.org/10.1145/800133.804350.
- Rina Dechter and Robert Mateescu, *AND/OR Search Spaces for Graphical Models*, Artificial Intelligence 171 (2007), https://doi.org/10.1016/j.artint.2006.11.003.
- Prior Charalampos Nadiotis ResearchGate manuscript as linked in \`RESEARCH_NOTES.md\`: https://www.researchgate.net/publication/417206732_On_the_Proposition_P_NP_Formal_Foundations_Necessary_Proof_Obligations_and_Research_Directions.
