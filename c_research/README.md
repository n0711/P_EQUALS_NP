# C17 SAT research baseline

This C17 exact DPLL solver reads DIMACS CNF, propagates units, branches and verifies its own satisfying witnesses. `test_and_analyze.py` generates 240 seeded small CNFs and cross-checks every SAT/UNSAT decision with exhaustive enumeration, producing `c_sat_results.json`.

Windows PowerShell, with Python 3.13 and clang installed:

```powershell
Set-Location .\c_research
& "C:\Program Files\LLVM\bin\clang.exe" -std=c17 -O2 -Wall -Wextra -o sat_solver.exe sat.c
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" test_and_analyze.py .\sat_solver.exe
```

Bash with gcc/clang and Python 3: `bash run.sh`. MATLAB/Octave optional: `analyze` from this directory.

The code is a baseline, NOT an EFSA compression solver and NOT a P=NP proof. Worst-case time is exponential; input DIMACS parser has a 4096-byte line buffer, and benchmarks intentionally use only tiny instances. Use memory/time caps for any larger tests. Tests validate a finite sample, not a theorem.
