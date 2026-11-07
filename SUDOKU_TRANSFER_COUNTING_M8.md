# M8 - Exact Sudoku partition-function evaluation by graph row transfers

Researcher: Charalampos Nadiotis / PELAOS Tech
Date: 7 November 2026
Status: theory and implementation; GitHub test evidence must be recorded separately.
Prior milestone: M7 Sudoku as precolored graph coloring and RioTuner-inspired Fourier equality integrals.
ResearchGate: the author reports posting the preceding M7 paper; no DOI or publication metadata was independently retrieved for M8.

## Question

The M7 integral represents a Sudoku conflict exactly, but the partition function still sums over q^(q^2) complete colorings. Can graph structure eliminate redundant intermediate summation *without losing exactness*?

M8 builds a sparse, deterministic, row-transfer dynamic program, an exact integer analogue of variable elimination, with memoized boundary signatures. It is a legitimate reduction from naive full-color enumeration for some instances and a way to measure whether distinct assignments collapse to the same future-relevant state. It is NOT a polynomial-time general algorithm.

## Mathematical model and recurrence

For generalized Sudoku with b-by-b boxes let q=b^2, V have q^2 cell vertices, and the color set be [q]. Every complete Sudoku row is a permutation of [q].

After processing rows 0 through r-1, keep a state

    s_r = (C_0,...,C_(q-1), B_0,...,B_(b-1))

where each C_j is a q-bit mask recording digits already assigned in column j, and each B_k is a q-bit mask of digits already placed in box-column k during the current b-row band. The B masks are reset to zero at each new box-row band. These masks represent precisely the constraints that can affect the unprocessed rows.

For a proposed row permutation p=(p_0,...,p_(q-1)), reject it if it disagrees with givens or if any bit p_j already occurs in column-mask C_j or current box-mask B_floor(j/b). For every accepted p, update both masks. Let T_r(s,p) be this deterministic next state, and let P_r be the permutations consistent with the row's givens.

The exact recurrence is

    F_q(s) = 1,
    F_r(s) = sum_{p in P_r and p compatible with s} F_(r+1)(T_r(s,p)).

The initial state has all masks zero; the solution count is F_0(s_0). Memoization reuses F_r(s) when different earlier row sequences reach the same boundary masks. Reconstruct one witness by storing the first compatible transition with positive suffix count.

### Exactness theorem

A Sudoku solution consists of q row permutations (each row contains q distinct colors), and the masks enforce that no two processed cells in any column or current box share a digit. Conversely, a complete sequence of row permutations that passes every mask transition uses q distinct colors in each column and completed box. Because these units each contain q cells, they necessarily contain every digit once. Givens are checked rowwise. Every solution therefore corresponds to exactly one accepted row path and vice versa. The recurrence sums 1 for each valid path and 0 for all rejected paths, hence counts Sudoku solutions exactly.

The M7 Fourier partition function

    Z = sum_{c in [q]^V} product_{edges (u,v)} (1 - delta(c_u,c_v))
                                   product_{given v} delta(c_v,g_v)

equals the M8 count. The transfer DP groups terms by the constraints visible at a row boundary; no numerical Fourier approximation is required.

### Symmetry theorem for clue-free boards

On a board with NO givens, every global permutation of digit labels sends a solution to another solution. Because the first row of every solution is a permutation, exactly one digit relabeling maps it to canonical first row (1,2,...,q). The group action is free, so each canonical first-row solution corresponds to exactly q! original solutions:

    Z_blank = q! * F_0^canonical.

The first-row constraint is NOT applied if any given clue exists, since arbitrary digit relabeling would generally violate fixed clues. This is a genuine exact symmetry reduction. It reduces one row of search by q! but does not remove the exponential worst case.

## Upper bound, not P=NP

There are q columns with q-bit masks and b active box groups with q-bit masks. Thus a boundary description uses at most q^2+bq bits. A loose bound on the number of distinct transfer states over q rows is q * 2^(q^2+bq). At each state the implementation may inspect up to q! row permutations and q entries. Thus a valid coarse total upper bound is

    T(q) = poly(q) * q! * 2^(q^2+bq)

as a loose bit-complexity upper bound, where poly(q) includes dictionary, parsing and arbitrary-precision count arithmetic. Memory is similarly exponential in the worst case. These bounds describe a deterministic exact method, but NOT a polynomial-time algorithm as q increases. The number of cells is q^2 and the number of possible row permutations is q!, so measuring fast 4x4 or partially filled 9x9 cases cannot establish any P=NP conclusion. This is a loose upper bound, NOT a SAT complexity lower bound.

The state mask recurrence is a standard transfer-matrix/dynamic-programming technique. We do not assert it is novel.

## Implementation and test protocol

Files:
- sudoku_transfer_count.py: exact integer count and model, row masks, box-band masks, state memoization, optional first-row symmetry, explicit resource limits.
- test_sudoku_transfer_count.py: independent counts against the M7 exhaustive oracle of 288 valid 4x4 grids, 240 seeded random clue subsets, 160 additional random adversarial clue sets, all 288 completed boards, exact 9x9 and constructed 16x16 checks, and incomplete resource-limit handling.
- run_sudoku_transfer_benchmark.py: compares clue-free 4x4 transfer with and without first-row symmetry, exact 4x4 reference counts, solved and partially solved 9x9, bounded unknown 9x9 and synthetic solved 16x16. Raw JSON is retained in CI.

Reproduction:

    python -m unittest -v test_sudoku_transfer_count.py
    python run_sudoku_transfer_benchmark.py > m8-transfer-results.json

The API returns (count, witness, metrics). Count=0 with status="completed" establishes UNSAT. Count=None with status="limit_states" or "limit_row_permutations" is UNDECIDED and must never be reported as zero or UNSAT.

Every positive witness is independently verified using M7's graph-coloring certificate checker. Reference counts for finite 4x4 boards come from the separate M7 permutation oracle, not from the transfer implementation.

## Falsifiable M9 gate

1. On a clue-free 4x4 board show exact 288 completions, with/without symmetry; the normalized count should be 12 and the group multiplier 4!=24.
2. For the published 9x9 example, independently distinguish solving one completion (easy in some instances) from counting all completions (may hit a budget).
3. Audit whether the row/column/box boundary state can be soundly compressed beyond q^2+bq bits for all generalized instances; counterexamples must check exact counts, not just feasibility.
4. Derive any claimed polynomial worst-case bound with all enumeration, memoization and arithmetic costs included. No such proof has been established in M8.

**Publication boundary:** this is a research continuation of the author's reported ResearchGate M7 post, with established algorithmic techniques, a proof of correctness and a still-exponential upper bound. It does not establish P = NP.


## M8 verified experimental addendum - 2026-11-07 21:55 UTC

**PR #8** (stacked on open M7 PR #7): https://github.com/n0711/P_EQUALS_NP/pull/8.
**Tested source head:** cd2de285f83d6424a5e0f67780970c0987360f9c.
**GitHub Actions:** SAT research workflow run **42418159452**, job **128540623940**, completed successfully.
**Result:** **81 Python unittest methods passed** in **1.046 seconds** on the runner, including **13 new M8 tests**. The M8 tests compare 240 seeded clue subsets, 160 adversarial random clue configurations, and all 288 full 4x4 Sudoku reference solutions against independent expected counts, plus 9x9/16x16 cases, digit relabeling and resource limit semantics. These finite checks support the implementation's tested behavior, not an asymptotic complexity claim.
**Raw artifact:** m8-sudoku-transfer-results, ID **13592321531**, from the same run. The JSON has been retrieved and inspected.

| Case | Exact count | Status | Memoized states | Accepted row transitions | Row trials |
|---|---:|---|---:|---:|---:|
| Empty 4x4, no symmetry | 288 | completed | 85 | 240 | 2040 |
| Empty 4x4, normalized first row times 4! | 288 | completed | 15 | 26 | 337 |
| 4x4 puzzle with four blanks | 1 | completed | 4 | 4 | 4 |
| Completed 9x9 grid | 1 | completed | 9 | 9 | 9 |
| One blank on completed 9x9 | 1 | completed | 9 | 9 | 9 |
| Standard 9x9 example, 60-state limit | unknown | limit_states | 60 | 60 | 41262 |
| Empty 9x9, max 5000 row permutations | unknown | limit_row_permutations | 0 | 0 | 0 |
| Completed constructed 16x16 | 1 | completed | 16 | 16 | 16 |

The blank 4x4 count satisfies the exact symmetry identity: 12 normalized-first-row completions times 4! = 288. This experiment shows **85 to 15** memoized-state reduction and **2040 to 337** row trials for this finite example; these are work counts, not an asymptotic speedup result.

The existing graph solver found a single valid witness on the given 9x9 example in one recursive search node; M8's exact counting reached its 60-state cap without concluding a count. Finding one witness and counting all witnesses are different tasks. None of these results establishes P=NP.

**Scientific limitation and next falsification:** The masks are exact future-dependent state invariants, but they require O(q^2+bq) bits, allowing exponentially many distinct states. Any proposed polynomial compression of these states must preserve exact counts across all clue configurations, not only SAT/UNSAT on small tests.


## Independent elementary 4x4 count derivation (not based on DP)

On an empty 4x4 Sudoku, use global digit renaming to fix row 1 to (1,2,3,4). Row 2 must use (3,4) in its first box and (1,2) in its second box, so the only possibilities are:

| Second row | Compatible bottom row pairs | Justification |
| --- | ---: | --- |
| 3 4 1 2 | 4 | Column leftovers and bottom two boxes permit four ways |
| 3 4 2 1 | 2 | Column leftovers and bottom box constraints permit two ways |
| 4 3 1 2 | 2 | Symmetric case to 3 4 2 1 |
| 4 3 2 1 | 4 | Symmetric case to 3 4 1 2 |

Once the third row is chosen, the fourth row is forced by the unused digit in each column; checking bottom-box uniqueness yields the listed 4+2+2+4=12 possibilities. Multiplying by 4! different first rows gives **288** completions. This is a finite combinatorial result, independently checked in the new analytic-test case and the prior 288-grid oracle. It is not a claim about the asymptotic complexity of Sudoku.


## Second verification addendum - 7 November 2026, 22:01 UTC

After adding an independent elementary enumeration of the 4x4 first-row-normalized boards, GitHub Actions [run 42418569685](https://github.com/n0711/P_EQUALS_NP/actions/runs/42418569685) completed successfully: **82 Python test methods passed in 0.798 seconds** on the runner, including **14 M8 methods**. The new analytic enumeration regression directly checks the four second-row cases yielding 4, 2, 2 and 4 lower completions, and verifies their sum 12 times 4! equals 288. These are finite case results, not a general Sudoku complexity proof.

The earlier 81-test result and raw benchmark artifact 13592321531 remain valid for their recorded commit. The revised XeLaTeX paper also includes the independent finite counting argument. Preserve the first and second verification runs as distinct experimental records.
