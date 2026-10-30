# Python and MATLAB SAT experiment

Author: Charalampos Nadiotis, PELAOS Tech. These are executable research baselines, **not a proof that P = NP**.

- `sat.py`: 2-SAT via strongly connected components, O(n+m) time and space in the number of variables and literal occurrences; general DPLL via unit propagation and branching (exponential worst case).
- `test_sat.py`: exhaustive 2-clause 2-SAT cross-checks against enumeration and deterministic randomized general-CNF cross-checks against enumeration.
- `matlab/two_sat.m`: independent pedagogical 2-SAT using implication reachability and SCC construction (dense O(n^3) time / O(n^2) space). Requires MATLAB; not verified by MATLAB execution in this environment.

Run with `python -m unittest -v test_sat.py`. MATLAB example: `[sat, assignment] = two_sat(2,{[1,2],[-1,2]})`.

For unrestricted SAT, the DPLL baseline branches and may explore exponentially many assignments. The polynomial guarantee for the restricted 2-SAT problem does not extend automatically to unrestricted 3-SAT. See `PROOF_STATUS.md`.
