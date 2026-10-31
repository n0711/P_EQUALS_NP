#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${CC:=cc}"
"$CC" -std=c17 -O2 -Wall -Wextra -Wpedantic -o sat_solver sat.c
python3 test_and_analyze.py "$(pwd)/sat_solver"
