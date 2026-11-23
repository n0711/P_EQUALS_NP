# P_EQUALS_NP - Research milestone ledger

**Researcher and manuscript author:** Charalampos Nadiotis (PELAOS Tech)
**Last updated:** 2026-11-23
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
| M10 | 2026-11-23 | RH/GRH bridge: CNF to quadratic integer polynomial systems | Unconditional field-independent polynomial-sized reduction, GRH only for general HN upper bound | `rh_grh_bridge.py`, `test_rh_grh_bridge.py`, dedicated CI; execution pending | M10: algebraic feasibility and number theory |
| M11 | 2026-11-23 | Arithmetic zeta encoding of CNF-SAT | For every finite field extension, point count equals #SAT; global zeta = Riemann zeta to power #SAT; pole criterion is SAT-equivalent | `zeta_sat.py`, `test_zeta_sat.py`, isolated CI; execution pending | M11: exact zeta identity and computational barrier |
| M12 | 2026-11-23 | Counting/zeta exponent for complete affine CNF blocks | Consistent GF(2) rank r gives #SAT=2^(n-r), inconsistent system #SAT=0; polynomial bit time on this restricted class | `affine_zeta_sat.py`, `test_affine_zeta_sat.py`; 19 combined unittest methods passed in M12 CI | M12: affine rank/count theorem |
| M13 | 2026-11-23 | Cutset #SAT and zeta exponents for mixed non-affine/affine components | Provided |S|<=log N, large components affine-recognized, non-affine components <=log N: polynomial bit-time exact counting or explicit unrecognized | `cutset_zeta_sat.py`, `test_cutset_zeta_sat.py`; 29 combined unittests passed in M13 CI | M13: cutset product-sum theorem |

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

## M7 — Structural hybrid lower bound, 16 November 2026

Can the existing uncapped structural hybrid decide every 3-CNF in polynomial time? The M7 theorem in [the working manuscript](paper/structural-sat-milestones.tex) disproves this for the implementation at `65de5e025d5f3a23f35c4717c80277d6ed7dc01e`. A linear-clause family forces a full binary prefix tree under maximum-frequency branching and exact residual memoization. This advances the M6 falsification gate and leaves the general P versus NP question open.

Reproduce with `python3 -m unittest -v test_structural_branch_lower_bound`. The deterministic generator uses no seed. The UNSAT baseline is the elementary five-variable counting contradiction proved in the manuscript. The test checks the public hybrid without a call limit. Local root Python test discovery passed all 55 methods on x86_64, Python 3.12.14. Recorded recursive calls include the initial call and cache lookups.

| k | Variables | Clauses | Recursive calls | Fallback branches |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 9 | 86 | 11 | 5 |
| 2 | 18 | 158 | 23 | 11 |
| 3 | 27 | 230 | 47 | 23 |
| 4 | 36 | 302 | 95 | 47 |
| 5 | 45 | 374 | 191 | 95 |

The proof gives a lower bound for every k. Exact counts above are finite measurements. The input uses O(k log(k+1)) bits under binary variable indexing. A next falsifiable question is whether a variable order or clause selection rule can detect this embedded contradiction before branching on the private blocks, including after variable renaming. Success there would cover this family only.

## M8 — Signed five-variable contradiction and a surviving lower bound

The public structural hybrid now returns five signed literals as an independently checkable UNSAT certificate when all ten complementary clause pairs occur. The manuscript proves recognition for every signed renaming of the M7 family and gives an alternate odd-cycle core that still forces exponential fallback calls. The original separator algorithm and its lower-bound regression remain available.

Local verification on x86_64, Python 3.12.14: 58 root unittest methods passed. Run `python3 -m unittest -v test_structural_branch_lower_bound` to reproduce. The test covers 32 seeded signed renamings across k=1,2,5,20, all 20 one-clause deletions of the isolated core, the old fallback and the revised solver. With no call cap, the odd-cycle variant produced 7, 15, 31, 63 and 127 recursive calls for k=1 through 5. These measurements are distinct from the all-k lower bound. The next research question is how to propagate implied parity constraints in a mixed CNF before branching.

## M9 — Binary parity extraction in mixed CNF

Starting from M8 commit `dc1f6c8196abeb55512393eddf1b9559a85af830`, the structural hybrid extracts equality and inequality edges, rejects inconsistent components before recursive search, and substitutes signed representatives into consistent residuals. The M9 manuscript section proves soundness, model lifting and a surviving lower bound for an equivalent all-ternary encoding.

Reproduce with `python3 -m unittest discover -v`. On x86_64 with Python 3.12.14 all 61 root tests passed, including 250 seeded mixed-formula comparisons with exhaustive search, explicit original-model reconstruction and both odd-cycle encodings. The former M8 family is decided at the root even with max_calls=1. Uncapped recursive calls on the guarded family for k=1 through 5 were 15, 31, 63, 127 and 191. These are finite observations. The lower bound for all k follows from the manuscript. The next falsifiable step is deriving the missing binary clauses by resolving opposite guard literals, with the number and cost of derived clauses accounted for.

## M10 addendum (23 November 2026): Riemann hypotheses and exact SAT

**Question:** Can classical RH or GRH be used as a valid step in a proof of P=NP?

**Proven result (standard construction, rederived):** CNF-SAT has a polynomial-size quadratic integer-polynomial feasibility encoding over every field under the conventional explicit-input measure. Auxiliary prefix products avoid an exponential expanded-clause representation. The equivalence needs neither RH nor GRH. See [the full statement, proof, caveats, and bibliography](RIEMANN_HYPOTHESIS_RESEARCH_2026_11_23.md).

**Known conditional theorem:** Koiran's 1996 GRH-conditional placement of general HN in RP^NP / the polynomial hierarchy does not show HN is in deterministic P and does not settle P versus NP. The distinction RH versus GRH is explicit.

**Implementation:** `rh_grh_bridge.py`, `test_rh_grh_bridge.py`, and isolated GitHub Actions workflow `.github/workflows/rh-grh-bridge.yml`. **Current execution classification:** CI pending verification at branch creation. Do not claim test success without inspecting the run. The XeLaTeX working manuscript includes the theorem and citation; its build is also subject to verification.

**Falsification gate:** brute-force over small prime fields must agree with independent Boolean truth-table SAT; Boolean lifts must satisfy the equations iff the original assignment satisfies the formula; long clauses must remain quadratic with linear-sized auxiliary encodings. Any failed check blocks merge. **Missing proof obligation:** a deterministic polynomial worst-case bit bound for unrestricted SAT (or a general P-vs-NP separation) remains unsolved.

## M11 addendum (23 November 2026): arithmetic zeta counts and the P vs NP proof barrier

**Question:** Can the ordinary Riemann zeta function or RH solve SAT when applied to the M10 quadratic encoding?

**Established identity (standard consequence of point-counting):** Let S(F) be #SAT on all n original variables, and let X_F be the integer polynomial scheme from M10, including its unique auxiliary extensions. Every finite field extension F_(p^r) has exactly S(F) zeros. The local zeta factor equals (1-t)^(-S(F)); the global arithmetic zeta is zeta(s)^(S(F)) for Re(s)>1. The pole at 1 has order S(F), so detecting a pole decides SAT; extracting its order computes #SAT. See [the detailed theorem, proof, and computational limitations](SAT_ZETA_RIEMANN_RESEARCH_2026_11_23.md).

**Implication:** This exact identity is a computational reparameterization, not a polynomial algorithm. RH constrains zeta zero locations, not the exponent S(F). No P=NP, P!=NP, RH or GRH result has been established here.

**Implementation:** `zeta_sat.py` is bounded exhaustive counting, `test_zeta_sat.py` independently enumerates F2 and F4 field-valued zeros, and `.github/workflows/m11-zeta-sat.yml` runs the tests. The XeLaTeX paper contains a mathematical section. **Current execution status:** submitted for GitHub Actions verification, not presumed passing. The core finite tests cannot imply general worst-case complexity statements.

**Next falsifiable gate:** compare every field-point count with the independent Boolean truth-table count, require zero non-Boolean roots in F4, verify the local coefficients are binomial(S+k-1,k), and inspect all new workflow and manuscript build results before merge.


### M10-M11 verified CI evidence (2026-11-23)

- [M10 algebraic SAT workflow run 45254719786](https://github.com/n0711/P_EQUALS_NP/actions/runs/45254719786): **success** on implementation commit `36c27a6b254afd12185da43b1b864044ae64538f`.
- [M11 SAT zeta workflow run 45254719731](https://github.com/n0711/P_EQUALS_NP/actions/runs/45254719731): **success**, 10 combined unittest methods (five M10, five M11) including exhaustive small-field and F4 extension checks and seeded Boolean oracles.
- [Existing SAT and graph search run 45254719775](https://github.com/n0711/P_EQUALS_NP/actions/runs/45254719775): **success** at that same implementation commit.
- [XeLaTeX manuscript run 45254437953](https://github.com/n0711/P_EQUALS_NP/actions/runs/45254437953): **success** on commit `9db9dc0f8d634a3caea7be7c78e22340570ba03c` containing the M11 manuscript section. A later final-head XeLaTeX run was not yet completed when this record was written.

These are CI execution results, not peer review or proof of any open conjecture. The final-head check must be inspected before merge.

## M12 addendum (23 November 2026): efficiently computable zeta exponent for affine SAT

**Question.** Can the number-theoretic zeta exponent from M11 ever be computed in polynomial time from a compact CNF? **Yes, but only for a precisely specified tractable subclass**: CNFs whose complete signed clause blocks on supports of width 1-3 encode a system of XOR equations over GF(2).

**Theorem.** If recognized and consistent, then the number of Boolean models, including unconstrained original variables, is `2^(n-r)`, where `r` is the GF(2) matrix rank. If recognized and inconsistent the count is zero. Therefore the M11 zeta exponent is computable in deterministic polynomial bit time for this restricted class. This is established affine tractability (Schaefer 1978), not a new P-vs-NP result. Complete derivation: [M12 proof and evidence](AFFINE_ZETA_M12_2026_11_23.md).

**Implementation.** `affine_zeta_sat.py` reuses the existing conservative affine recognizer/linear elimination and computes the exact count and requested finite local-zeta coefficients. An input not recognized as an affine block *never* receives a fabricated SAT/UNSAT answer, even if a separate solver could decide it.

**Verified evidence.** [GitHub Actions M12 run 45260360585](https://github.com/n0711/P_EQUALS_NP/actions/runs/45260360585) completed successfully on commit `1aaf0fdebcd24f56b057471e43b32df1d0f19efa`, with **19** unittest methods passed (9 M12 + 5 M11 + 5 M10). Observed CI logs include independent truth-table oracles, F2/F4 finite-extension point counts, seeded variable-renaming checks, a connected Tseitin graph-count family, 200-variable rank reduction, and a 1000-variable unconstrained count.

**Manuscript.** A new XeLaTeX M12 section was added to `paper/structural-sat-milestones.tex`. Its latest build is a separate verification gate; do not claim it passed until the relevant commit's workflow is complete.

**Falsification gate.** Cross-check the recognized output with independent small truth tables and signed relabeling, verify that inconsistent recognized systems give zero, ensure no unrecognized input is silently returned as UNSAT, and audit large input time/bit-size accounting.

**Unresolved target.** No general deterministic polynomial-time SAT algorithm or general superpolynomial SAT lower bound is known here. Hence neither P=NP nor P!=NP has been proved.


## M13 addendum (23 November 2026): polynomial counting beyond affine by logarithmic cutset conditioning

**Mathematical identity:** For a supplied separator S and its Boolean assignments alpha, after conditioning obtain variable-disjoint residual components, and let u_alpha count free original variables. Exact #SAT is the sum across alpha of `2^u_alpha * product_i #component_i`. This is established connected-component model counting / cutset conditioning, not an original solution of P vs NP.

**Proved restricted guarantee:** Under explicit-size proxy `N=max(2,n+m+L)`, accept supplied separator `|S|<=floor(log2 N)`. For each conditioned residual component, either compute its count via the established affine XOR rank method (any size), or enumerate at most `floor(log2 N)` non-affine variables. If a branch has unsupported non-affine components, return `unrecognized` instead of a count. Total bit complexity on accepted instances is `poly(N+d) 2^(|S|+floor(log2 N))`, polynomial in N+d, with d the requested explicit finite local-zeta degree. The algorithm **does not find a separator automatically**, and the class does not include arbitrary SAT.

**Non-affine witness family:** `F_k=AND_i(s OR a_i OR b_i OR c_i)` with distinct private triples. Its global primal graph is connected, but conditioning s gives exact `#F_k=8^k+7^k` and arithmetic zeta `zeta_X(s)=zeta(s)^(8^k+7^k)`. Count is odd >1 and therefore cannot be a GF(2) affine solution-space count. A guarded XOR chain can coexist and be counted by rank.

**Code:** `cutset_zeta_sat.py`, `test_cutset_zeta_sat.py`, `.github/workflows/m13-cutset-zeta.yml`, and manuscript section M13. Full statement and references: [M13 note](CUTSET_ZETA_M13_2026_11_23.md).

**Verified finite execution:** [GitHub Actions run 45261663593](https://github.com/n0711/P_EQUALS_NP/actions/runs/45261663593) passed **29** unittest methods on head commit `148a2ce9936762c4ae7e919716096d1747c2db35` (10 M13, 9 M12, 5 M11, 5 M10); Python syntax verification passed. It includes independent random truth tables, 100 non-affine guarded petals, 120-variable guarded affine XOR chain and mixed component tests. Later manuscript/ledger commits require their own final-head CI before merging.

**Falsification gate:** Never return a numeric count on an input failing the separator bound or a non-affine residual component bound. Check zero-variable, tautological, contradictory and free-variable edge cases against independent exhaustive truth tables. Validate exact bit-cost and representation assumptions separately from measured runtime.

**Open proof obligation:** Finding and exploiting a suitable small structural decomposition for every arbitrary CNF in provably polynomial worst-case bit complexity remains unsolved; nor has a superpolynomial bound for every SAT solver been established. No proof of P=NP or P!=NP is claimed.
