"""C DIMACS edge-case regression suite; checks exact SAT decision, not a P=NP claim."""
import json
import pathlib
import subprocess
import sys
import tempfile

CASES = [
    ("empty CNF", "p cnf 0 0\n", True),
    ("empty clause", "p cnf 0 1\n0\n", False),
    ("positive unit", "p cnf 1 1\n1 0\n", True),
    ("contradictory units", "p cnf 1 2\n1 0\n-1 0\n", False),
    ("tautological clause", "p cnf 1 1\n1 -1 0\n", True),
    ("all units satisfied", "p cnf 3 3\n1 0\n2 0\n3 0\n", True),
    ("unsat after branching", "p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n", False),
    ("multiline clause", "p cnf 2 1\n1\n2 0\n", True),
    ("negative model", "p cnf 2 2\n-1 0\n-2 0\n", True),
]
INVALID = [
    ("missing header", "1 0\n"),
    ("too few clauses", "p cnf 1 2\n1 0\n"),
    ("too many clauses", "p cnf 1 1\n1 0\n-1 0\n"),
    ("literal out of range", "p cnf 1 1\n2 0\n"),
    ("unterminated clause", "p cnf 1 1\n1\n"),
]

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python test_edge_cases.py path/to/sat_solver")
    binary = str(pathlib.Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory() as work:
        file = pathlib.Path(work) / "input.cnf"
        for name, source, expected in CASES:
            file.write_text(source, encoding="ascii")
            process = subprocess.run([binary, str(file)], capture_output=True, text=True, timeout=5)
            assert process.returncode == 0, (name, process.stderr)
            actual = json.loads(process.stdout)
            assert actual["sat"] is expected, (name, actual, expected)
        for name, source in INVALID:
            file.write_text(source, encoding="ascii")
            process = subprocess.run([binary, str(file)], capture_output=True, text=True, timeout=5)
            assert process.returncode != 0, (name, "invalid DIMACS accepted")
    print(f"PASS {len(CASES)} edge decisions and {len(INVALID)} invalid-input cases")

if __name__ == "__main__":
    main()
