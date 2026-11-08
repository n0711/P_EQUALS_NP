# M7 - Generalized Sudoku and RioTuner-inspired phase integrals

Author: Charalampos Nadiotis / PELAOS Tech
Date: 7 November 2026
Status: mathematical construction and experimental implementation; no proof of P=NP.

## Question and transfer from n0711/riotuner

Can the complex phase demodulation used for RioTuner pitch estimation provide a useful integral representation of generalized Sudoku graph constraints? The private RioTuner repository has a Rust engine with complex sinusoidal demodulation in engine/src/partials.rs, Blackman-Harris weighting in engine/src/window.rs and YIN period detection in engine/src/yin.rs. The present work reuses the mathematical Fourier projection principle, not the private implementation, audio signals or pitch estimators.

In RioTuner the sampled complex projection of signal x around reference frequency f is

    X_m(f) = sum_j w_j x(t_mj) exp(-2 pi i f t_mj).

In generalized Sudoku, with box width b and q=b^2 digits, the graph has q^2 cell-vertices, with edges connecting cells in the same row, column or box. A Sudoku solution is a q-coloring of this graph preserving all givens. A nondeterministic machine may guess a q-color for every vertex and verify the certificate in deterministic polynomial time; this proves membership in NP, NOT an efficient deterministic finder.

## Fourier integral identity

For digit labels a,b in {1,...,q}, exact mathematics gives

    delta(a,b)
      = (1/2pi) integral from 0 to 2pi of exp(i(a-b)t) dt
      = (1/q) sum for k=0..q-1 of exp(2 pi i k(a-b)/q)
      = 1 if a=b, else 0.

The discrete equality follows from character orthogonality: a-b is zero or nonzero mod q, and the geometric series cancels when nonzero. The graph collision energy for a completed coloring c is

    E(c) = sum over edges (u,v) of delta(c(u),c(v)).

Exactly E(c)=0 means no Sudoku peer conflict, but original givens must be preserved too. A partial assignment with no assigned conflicts is NOT a satisfying certificate.

The straightforward direct edge checker costs O(|E|), while the explicit q-term Fourier projection costs O(q|E|): this formulation is *less efficient*, not a polynomial-time breakthrough. Floating-point Fourier cancellation is only approximate. The exact integer edge checker is always authoritative.

RioTuner's Blackman-Harris window is excellent for suppressing audio spectral leakage but uses nonuniform weights. Substituting these weights into the finite character average destroys exact orthogonality and creates nonzero diagnostic leakage even for valid Sudoku. Weighted Fourier energy must NEVER determine whether a Sudoku is solved.

## Reduction and counting obstruction

sudoku_graph_to_sat.py makes q^3 one-hot Boolean variables for cell and digit combinations, then explicitly enforces exactly one color per cell, distinct colors along graph edges and fixed clues. This is a polynomial-size reduction in the direction generalized Sudoku <=p SAT, with O(q^4) total clause scale. The converse direction is NOT demonstrated here.

The number of Sudoku completions can be represented by a partition function

    Z = sum_{c in [q]^V} [prod_{edges (u,v)}(1-delta(c(u),c(v)))]
                       [prod_{given v}delta(c(v), clue(v))].

This contains q^(q^2) candidate complete colorings. Rewriting each delta as a Fourier sum or integral does not remove that exponential summation. To prove P=NP, one needs a separate deterministic polynomial-time *evaluation* or *decision* method valid for every generalized instance.

## Reproducibility files

- sudoku_graph_np.py: exact graph verifier, synthetic solutions, deterministic backtracking with propagation, explicit undecided resource limit.
- sudoku_graph_to_sat.py: SAT encoding and witness round-trip.
- sudoku_phase_integrals.py: character projection, window comparison, exact peer count diagnostic.
- test_sudoku_graph_np.py: independent 4x4 oracle, 9x9 example, 16x16 constructed example, explicit invalid/unsatisfiable cases.
- test_sudoku_phase_integrals.py: Fourier orthogonality, Blackman-Harris leakage, 240 random complete 4x4 assignments, CNF witness tests.
- run_sudoku_phase_experiment.py: reproducible JSON from solved, conflicted and partial examples.

Run:

    python -m unittest -v test_sudoku_graph_np.py test_sudoku_phase_integrals.py
    python run_sudoku_phase_experiment.py > m7-sudoku-phase-results.json

The benchmark and manuscript must preserve a verified GitHub Actions run ID. Until CI has been checked, do not describe these tests as passed.

**Next research gate:** independently measure whether any Fourier-derived candidate ordering can outperform exact neighbor counts after including the O(q) phase projection cost. An algorithm for NP-complete generalized Sudoku must prove worst-case polynomial time, not just find solutions in tested instances.
