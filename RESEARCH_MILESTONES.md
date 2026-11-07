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
| M6 | 2026-11-07 | Polarity signatures and identical-primal-graph SAT/UNSAT constructions | Exact pure/unit preprocessing and complete clause-pattern UNSAT certificate, with three K_n 3-CNF families of distinct SAT status | `polarity_sat.py`, `dense_cnf_families.py`, `test_polarity_sat.py`, `run_polarity_benchmark.py`; M6 CI verification initially pending | Section: polarity-aware graph counterexample |
| M7 | 2026-11-07 | Nondeterministic generalized Sudoku graph coloring and RioTuner-inspired Fourier integral | NP certificate verification, exact one-hot CNF encoding, Fourier character orthogonality, nonuniform-window leakage | sudoku_graph_np.py, sudoku_graph_to_sat.py, sudoku_phase_integrals.py, tests; CI initially pending | Section: Sudoku and Fourier phase constraints |

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


## M5 verification addendum - 2026-11-07 18:32 UTC

**Pull request:** [#5](https://github.com/n0711/P_EQUALS_NP/pull/5), opened after #4 had merged.  
**Verified code and documentation head:** \`4b55c1eace53d957f38548c6a19518316c1ed17b\`.  
**Evidence source:** [GitHub Actions SAT research run 42401754276](https://github.com/n0711/P_EQUALS_NP/actions/runs/42401754276), plus associated cross-language and graph-search workflows on the same head.

- **SAT research verification:** succeeded. The Python regression step ran **37 unittest methods** in **0.523 seconds on the GitHub runner**, all passed. Eleven belong to \`test_structural_hybrid_sat.py\`.
- **New M5 test scope:** 640 seeded small CNFs compared against an exhaustive oracle (n=0..7), 120 variable-renaming/ordering comparisons, 120 sampled small XOR systems, parity Tseitin SAT and UNSAT tests on even-sized connected cubic graphs, pigeonhole contradictions, graph three-coloring, and width-bound invariants. These are finite regressions, not complexity proofs.
- **Bounded benchmark reproduction:** succeeded for the CI quick case set; input labels and results are retained in workflow artifact \`structural-sat-results\` (artifact ID 13586040475; run 42401754276). The workflow step exited successfully, and its script asserts expected outcomes for completed runs. Limits/timeouts remain \`UNDECIDED\`.
- **Graph-separator benchmark artifact:** \`graph-separator-results\` (artifact ID 13585573119; same run).
- **Other workflows on the same head:** SAT and graph-search verification (three successful jobs) and SAT cross-language verification (one successful job).
- **Boundaries:** No independently audited runtime speedup, memory improvement, SAT certificate proof beyond implementation crosschecks, or unrestricted polynomial upper bound is claimed. The benchmarks measure a finite sample on one CI platform.
- **Paper update:** M5 can now cite the observed regression statuses, still without claiming an unrestricted theorem or a peer-reviewed scientific result.

This addendum does not overwrite the originally pending M5 status; it records the subsequent evidence with an immutable workflow ID.


## M5 XeLaTeX manuscript build evidence - 2026-11-07 18:36 UTC

- **Source:** \`paper/structural-sat-milestones.tex\` at PR #5, author Charalampos Nadiotis.
- **Workflow:** [XeLaTeX milestone manuscript, run 42402089931](https://github.com/n0711/P_EQUALS_NP/actions/runs/42402089931).
- **Result:** successful XeLaTeX compilation, twice, followed by PDF existence check and successful artifact upload.
- **Artifact:** \`structural-sat-milestone-paper\`, ID 13585444810, generated from head commit \`9ae829680c22f7fd2aa4f6bd5e250f4e403f4e50\`. GitHub workflow artifacts have limited retention.
- **Build correction preserved:** initial run 42401955056 failed because the build environment lacked the \`pzdr\` font metric. Workflow dependency \`texlive-fonts-recommended\` was added, and rerun 42402089931 succeeded. The original failure is not reclassified as a pass.
- **Publication status:** compile-successful, author-attributed **working XeLaTeX manuscript**, not independently peer reviewed, not yet a claim of a novel complexity result or a proof of P = NP.

For later milestones, append a new log entry and extend the XeLaTeX source with only verified claims and commit-specific evidence. Preserve old artifacts, add corrected versions with new run IDs, and do not quietly alter past experimental outcomes.


## M6 research hypothesis and falsifiable construction - 2026-11-07

**Question:** Can a high-treewidth connected SAT formula be trivially solved using literal polarity, and can two formulas with the *same* graph have opposite SAT status? **Answer:** Yes, by explicit constructions. This refutes any claim that connectivity, treewidth or separator size alone determines satisfiability or the actual search effort.

**Definition, for n >= 3.** Let T_n be all three-element subsets of [n] and let G be the primal variable graph. Define:

1. **A_n (positive):** conjunction over T in T_n of the clause containing all three positive variables. All-True is a satisfying assignment. Every active variable is pure positive, so one full pure-literal reduction solves it.
2. **B_n (full patterns):** for every T, include all eight signed clauses with support T. A particular triple's eight clauses collectively exclude *every* truth assignment to its three variables, proving UNSAT without SAT branching.
3. **C_n (opposing monotone):** for every T, include both the all-positive and all-negative clause. The positive clauses require the number of False values <= 2; the negative clauses require the number of True values <= 2. With n >= 3, C_n is SAT iff n <= 4. Its unit/pure/signature preprocessor detects none of these contradictions for n >= 5; complete fallback is necessary.

**Graph theorem.** All A_n, B_n and C_n have exactly the primal graph K_n, because every pair of variables appears together in some triple. Thus their treewidth is exactly n-1, they are connected, and neither one- nor two-vertex deletion separates any graph when n >= 4. Yet A_n is SAT, B_n is UNSAT, and C_n has a threshold at n=5. **These are standard constructions and elementary arguments, not a new proof of any SAT complexity lower bound.**

**Support-pattern certificate.** A non-tautological clause with one signed occurrence of each variable in a support S excludes one assignment to S. If all 2^{|S|} sign patterns occur, every assignment violates one clause: the formula is UNSAT. The implementation searches only support widths <=3 (configurable), in time polynomial in explicit CNF length.

**Reduction theorem.** Unit propagation fixes logically necessary values. A pure variable appears in only one sign and may safely be assigned to satisfy every remaining clause mentioning it, leaving an equisatisfiable residual CNF. Iteration terminates in at most n variable-elimination stages. The residual is solved by the previous exact affine-or-separator portfolio. Assigned values are restored, and the final model is verified against the original clauses. A complete-support contradiction is sound independently of the rest of the formula. The complete combined solver is correct, with unrestricted exponential worst case.

**Implementation:** \`polarity_sat.py\` supplies the polynomial preprocessing and exact fallback; \`dense_cnf_families.py\` supplies three graph-identical mathematical construction families; \`test_polarity_sat.py\` includes 810 seeded independently enumerated CNF oracle cases (n=0..8, 90 each), 210 signed-renaming cases, witness validation, family threshold and graph-width invariants, affine fallback checks and explicit undecided resource limit semantics. \`run_polarity_benchmark.py\` compares DPLL, previous hybrid, and new portfolio as separate processes with explicit wall-time/call ceilings, retaining raw JSON and statuses.

**Verification at initial commit:** tests and benchmark workflow added; *do not claim passing CI until the run completes*. Neither new theorem claims a worst-case SAT advantage: these are previously recognized easy or locally contradictory families. The mixed-polarity C_n family remains a useful input on which this preprocessing has no simplification; no claim is made that C_n is computationally hard.

**Paper placement:** add Section 'Same-primal-graph SAT and UNSAT families' to \`paper/structural-sat-milestones.tex\`, and maintain the existing P-vs-NP proof obligation. Add immutable CI run/artifact IDs in a dated verification addendum.

**Next falsification:** search residual high-width 3-SAT examples with no unit, pure variable, locally complete support or affine structure; measure whether exact solver state counts still grow exponentially. An impossibility theorem for any proposed universal polynomial-time rule would need an independent rigorous proof, not a histogram.


## M6 verification addendum - 2026-11-07 18:58 UTC

**Reviewed source head:** \`eaa214129f4ec4861dead806c6942aa07b8dc526\` in [PR #6](https://github.com/n0711/P_EQUALS_NP/pull/6), branch \`research/m6-polarity-signatures-20261107\`.

- [SAT research GitHub Actions run 42403877621](https://github.com/n0711/P_EQUALS_NP/actions/runs/42403877621): **success**, 48 Python unittest methods passed in 0.609 seconds on its runner. Exactly **11** are new \`test_polarity_sat.py\` methods.
- The M6 test method loops include **810** seeded independent exhaustive-SAT oracle comparisons for n=0..8, and **210** signed variable-renaming checks for n=1..7. Satisfying models are verified against original clauses. Graph invariants and family thresholds are additionally asserted; these counts describe checked finite cases, not a complexity theorem.
- Graph and graph-search CI (3 jobs) and SAT cross-language CI (1 job) on the same source head: **success**.
- The M6 bounded benchmark job completed and uploaded JSON artifact \`m6-same-primal-graph-results\` (ID **13586087780**, GitHub Actions run 42403877621). The script runs **9 generated inputs** (n=4,6,8 times 3 families) across three solver backends. Per-worker \`timeout\` and \`limit_calls\` are *undecided*, never UNSAT; workflow completion does not imply every individual solver run completed.
- Existing graph-separator and structural benchmark artifacts in that run: \`graph-separator-results\` ID 13586816066 and \`structural-sat-results\` ID 13586697402.
- M6 paper build is tracked in the separate XeLaTeX workflow. Record the successful artifact ID only after a verified build.

**Outcome:** finite correctness regressions and same-graph constructions passed; performance superiority and the general polynomial-time SAT bound remain **unproved**. The three-family theorem follows from the written elementary proof, not solely these finite observations. No P = NP proof is claimed.


## M6 XeLaTeX compile evidence - 2026-11-07 19:00 UTC

- Source commit \`64dd783195f924e5d2c57dd30f8d2a7141cd570a\` includes the M6 mathematical statement, elementary proof, and verified 48-test evidence.
- [XeLaTeX manuscript workflow 42404007834](https://github.com/n0711/P_EQUALS_NP/actions/runs/42404007834): **success**, two XeLaTeX passes and PDF output validation.
- PDF artifact: \`structural-sat-milestone-paper\`, artifact ID **13586169439** (69,609 bytes reported by GitHub). This is a generated, reproducible working manuscript rather than a peer-reviewed publication. Artifacts are subject to GitHub retention limits.
- The milestone log is append-only: this documentation update does not change the paper source or retrospectively alter earlier test observations.

The subsequent research gate remains unrestricted, non-affine connected SAT formulas with explicit complexity accounting; nothing recorded here establishes a polynomial-time algorithm for general 3-SAT.


## M7 hypothesis, proof obligations, and numerical experiment (2026-11-07)

**Research question:** Transfer phase-demodulation mathematics from the separately maintained, private n0711/riotuner Rust pitch engine to generalized Sudoku graph coloring. Can a Fourier integral directly eliminate nondeterministic guessing? **Answer to the demonstrated mathematics:** the Fourier expression is an exact *constraint evaluator*, not an efficient solution generator.

- **Source provenance:** The original RioTuner engine uses weighted complex sinusoidal demodulation and phase-slope regression on overlapping audio blocks (engine/src/partials.rs), a four-term Blackman-Harris analysis window (engine/src/window.rs), and YIN for coarse pitch estimation (engine/src/yin.rs). None of this private implementation code is copied. Only the standard complex Fourier mathematics is adapted in a new Python experiment, which is a different workload.
- **Graph model:** For box width b, let q=b^2. Sudoku contains q^2 vertices, colors 1..q, and peer edges sharing row/column/box. The original 9x9 case has 81 vertices and 810 undirected edges. A complete proper coloring preserving givens is exactly a Sudoku completion.
- **Nondeterministic membership:** A guessed q-color assignment is a witness of q^2 digit labels. One deterministic pass through colors, edges and givens verifies it in polynomial time. This proves generalized Sudoku in NP; it does not turn nondeterministic guesses into a deterministic polynomial-time search.
- **Exact Fourier integral theorem:** For integer a,b in 1..q,

      delta_{a,b} = (1/(2pi)) integral_0^{2pi} exp(i(a-b)t) dt
                 = (1/q) sum_{k=0}^{q-1} exp(2pi i k(a-b)/q).

  Character orthogonality yields 1 if a=b and 0 otherwise. For a complete coloring c, sum over all edges of delta(c_u,c_v) counts exact conflicts; zero *plus preserved givens* is equivalent to a valid coloring. For incomplete Sudoku, zero assigned-edge conflicts is inconclusive. Explicit phase projection costs O(q|E|), while integer edge checking costs O(|E|); this is not a runtime improvement.
- **Window falsification:** Blackman-Harris weights are not uniform. Weighted phase projection lacks exact Kronecker-delta orthogonality in general, and a solved Sudoku can have nonzero numeric absolute phase leakage. Never use weighted or floating phase scores as an exact SAT decision.
- **Polynomial encoding theorem:** sudoku_graph_to_sat.py encodes each cell-color pair as one Boolean variable (q^3 Boolean variables), exact-one-color constraints, peer inequalities and givens, with O(q^4) explicit CNF size. A satisfying assignment corresponds exactly to a Sudoku solution. This is Sudoku <=p SAT, not SAT <=p Sudoku.
- **Partition function limitation:** Expressing the count of solutions as a sum over colorings of products of (1-delta) edge factors and clue-delta factors retains q^(q^2) candidate colorings. Rewriting delta factors as integrals does not prove a polynomial algorithm for evaluating the partition function.
- **Practical experiment:** sudoku_graph_np.py provides graph construction, exact witness verification and deterministic domain-propagating backtracking with a distinct undecided node-limit state. Tests include an independent 4x4 Sudoku enumeration oracle, seeded clue sets, a known 9x9 solution, synthetic 16x16 validation, Fourier delta orthogonality, exact conflict counts and CNF witness conversion. run_sudoku_phase_experiment.py records solved/invalid/partial Sudoku phase diagnostics in JSON.
- **Initial execution status:** tests are committed but have no passed status until actual CI checks finish. This remains unproven as a universal deterministic polynomial Sudoku algorithm.
- **Next falsification:** Compare signed-phase integration, exact graph-edge checking and candidate ordering on general Sudoku as size b grows, including adversarial solutions and unsatisfiable puzzles. Count *total* integral evaluation cost, graph construction and all backtracking states. A probabilistic or nondeterministic certificate is not a deterministic polynomial worst-case proof.

Technical research note: SUDOKU_RIOTUNER_PHASE_M7.md. Working XeLaTeX draft: paper/structural-sat-milestones.tex. Branch: research/m7-sudoku-graph-np-20261107, PR #7.


## M7 verified CI and experimental evidence - 2026-11-07 21:20 UTC

- **PR:** [#7](https://github.com/n0711/P_EQUALS_NP/pull/7), M7 branch research/m7-sudoku-graph-np-20261107. The M7 code head tested was commit 0df1ae8a254e85629df4d7e4075627cc2a529862.
- [SAT research run 42415413946](https://github.com/n0711/P_EQUALS_NP/actions/runs/42415413946): **completed/success**. GitHub job 128532292855 ran **68 Python unittest methods in 1.128 seconds**, all passed. Exactly 20 methods are new M7 tests: 11 in test_sudoku_graph_np.py and 9 in test_sudoku_phase_integrals.py. The other 48 prior tests remain passing.
- **Independent checker evidence:** an independent 4x4 oracle enumerates 288 completed grids. The tests compare 240 seeded clue subsets and 300 seeded random clue grids to the oracle (540 total 4x4 puzzle evaluations). They also test the conventional 9x9 example, constructed 16x16 validation, conflicting givens, a resource-budget undecided status and CNF witness round-tripping.
- **Phase/integral evidence:** tests check 1-,2-,4-,9-,16-color character orthogonality on every color pair; 240 seeded complete 4x4 random assignments compare complex projection with exact graph edge-clash counts. Nonuniform Blackman-Harris projection exhibits nonzero leakage on a correct full Sudoku. Numerical phase results are **not** used as exact solver decisions.
- **Reproducible experiment:** the M7 JSON-producing program completed successfully in the CI run and uploaded artifact **m7-sudoku-phase-results**, ID **13590907805**. It measures solved, conflicted and partially filled 9x9 boards; a 4x4 graph-search example; and the Fourier-vs-direct candidate edge scores. Explicit Fourier evaluation is O(q|E|), vs O(|E|) for exact integer comparisons, so no speedup claim is made.
- The corresponding SAT cross-language, SAT and graph-search (three jobs) and XeLaTeX workflows on the tested code head also completed successfully. The *M7-updated* XeLaTeX manuscript will have a separate build run after the paper is pushed; do not conflate it with the older manuscript build.
- **Scope/novelty:** The analytic equality and Sudoku-to-SAT encoding are established mathematics. The experiment is an implementation of the Fourier phase idea, inspired by RioTuner's signal processing. This does not produce a polynomial-time solver for generalized Sudoku or prove P=NP.

No independent expert or peer review is claimed; maintain a separate dated addendum if any M7 result requires correction.


## M7 numerical evidence addendum - 2026-11-07, GitHub artifact 13590907805

The artifact m7-sudoku-phase-results.zip from SAT research run 42415413946 was downloaded and inspected. It contains m7-sudoku-phase-results.json with these measured values for the standard Sudoku graph (81 vertices, 810 edges):

| Complete/partial 9x9 case | Exact equal-color graph edges | Uniform phase projection (real sum) | Blackman-Harris phase absolute sum |
| --- | ---: | ---: | ---: |
| Valid complete coloring | 0 | 4.50380473656e-14 | 208.315358276 |
| Changed one digit | 2 | 2.0000000000000773 | 208.189111477 |
| One blank cell | 0 among 790 assigned edges | 4.02455846427e-14 | 203.019813249 |

The valid solution's small nonzero uniform result is floating-point rounding, not an exact mathematical contradiction; the exact character sum is 0. Replacing one cell's color in this chosen construction produces **two graph-conflicting edges**, which uniform phase projection faithfully approximates. Blackman-Harris weighting creates a large nonzero absolute sum even on a valid coloring, falsifying any inference that the weighted audio window is an exact Sudoku conflict indicator.

For one blank 9x9 cell, only 790 of the 810 edges had both endpoints assigned. An exact conflict count of zero therefore does not certify satisfiability, because a complete witness is missing.

A tested 4x4 puzzle was solved in **2 recursive nodes** by the deterministic graph backtracker (one finite example, not a worst-case bound). Candidate Fourier scores matched the integer peer counts within numerical error. For the first cell of a one-blank solved grid, digit 1 had an approximate phase clash score 4.79e-15 (exact 0); other digits had exact clashes 2 or 3.

**Interpretation:** The phase integral is mathematically equivalent to the equality predicate; RioTuner's nonuniform audio window is not. No measured speedup or polynomial solver is claimed. The experiment's raw JSON, workflow ID and source commit remain preserved in the M7 PR.
