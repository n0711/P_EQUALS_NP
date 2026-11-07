"""Exact mixed XOR/CNF SAT by extracting complete parity blocks.

The unrecognized CNF variables form an explicit strong affine backdoor:
for r distinct residual-clause variables, exhaustive search followed by
Gaussian elimination costs poly(N)*2^r in the explicit input size N.
This is an established backdoor-style parameterization, NOT P = NP.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from time import perf_counter

from sat import _validate, verify


class _CallLimit(Exception):
    pass


def _canonical(clauses):
    """Deterministic normalization; an empty clause remains a contradiction."""
    normalized = set()
    for clause in clauses:
        literals = set(clause)
        if any(-lit in literals for lit in literals):
            continue
        normalized.add(tuple(sorted(literals, key=lambda x: (abs(x), x))))
    return tuple(sorted(normalized, key=lambda c: (len(c), c)))


def extract_affine_blocks(n, clauses):
    """Return (equations, residual_cnf, metrics), preserving conjunction.

    One equation is (bit-mask of variables, XOR parity right-hand side).
    Supports of size >3, incomplete blocks and mixed parity groups stay in CNF.
    """
    formula = _canonical(_validate(n, clauses))
    groups = defaultdict(list)
    for clause in formula:
        support = tuple(abs(lit) for lit in clause)
        groups[support].append(clause)
    extracted = set()
    equations = []
    for support, members in sorted(groups.items()):
        k = len(support)
        if not 1 <= k <= 3 or len(members) != (1 << (k - 1)):
            continue
        excluded_parities = {
            sum(lit < 0 for lit in clause) & 1 for clause in members
        }
        if len(excluded_parities) != 1:
            continue
        # Negative literals indicate the forbidden variable value 1.
        rhs = 1 ^ next(iter(excluded_parities))
        equations.append((sum(1 << (v - 1) for v in support), rhs))
        extracted.update(members)
    remainder = tuple(c for c in formula if c not in extracted)
    residual_vars = {abs(lit) for c in remainder for lit in c}
    metrics = {"equations": len(equations), "extracted_clauses": len(extracted),
               "residual_clauses": len(remainder),
               "residual_variables": len(residual_vars)}
    return tuple(equations), remainder, metrics


def _linear_solve(equations, assigned):
    """RREF over GF(2); (consistent, forced vars, extending assignment)."""
    assigned_mask = sum(1 << (v - 1) for v in assigned)
    true_bits = sum(1 << (v - 1) for v, value in assigned.items() if value)
    basis = {}
    for original_mask, original_rhs in equations:
        mask = original_mask & ~assigned_mask
        rhs = original_rhs ^ ((original_mask & true_bits).bit_count() & 1)
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (mask, rhs)
                break
            mask2, rhs2 = basis[pivot]
            mask ^= mask2
            rhs ^= rhs2
        if not mask and rhs:
            return False, {}, {}
    # Remove lower-index pivot terms from all higher rows.
    for pivot in sorted(basis):
        row, rhs = basis[pivot]
        for upper in sorted(k for k in basis if k > pivot):
            top, top_rhs = basis[upper]
            if top & (1 << pivot):
                basis[upper] = (top ^ row, top_rhs ^ rhs)
    forced = {pivot + 1: bool(rhs)
              for pivot, (row, rhs) in basis.items() if row == 1 << pivot}
    extension = {pivot + 1: bool(rhs) for pivot, (_, rhs) in basis.items()}
    return True, forced, extension


def _restrict(formula, assignments):
    simplified = []
    for clause in formula:
        if any((lit > 0) == assignments[abs(lit)]
               for lit in clause if abs(lit) in assignments):
            continue
        remaining = tuple(lit for lit in clause if abs(lit) not in assignments)
        if not remaining:
            return ((),)
        simplified.append(remaining)
    return tuple(simplified)


def mixed_affine_sat(n, clauses, *, max_calls=None):
    """Return (model_or_none, metrics): completed None means UNSAT.

    On status=limit_calls None is UNDECIDED. Without max_calls, abstract
    search is complete, though Python has practical runtime limits.
    """
    started = perf_counter()
    original = _validate(n, clauses)
    if max_calls is not None and (not isinstance(max_calls, int)
                                  or isinstance(max_calls, bool) or max_calls < 1):
        raise ValueError("max_calls must be a positive integer or None")
    equations, residual, extraction = extract_affine_blocks(n, original)
    stats = {**extraction, "status": "completed", "method": "mixed_affine",
             "calls": 0, "branches": 0, "gaussian_calls": 0,
             "linear_conflicts": 0, "linear_forced": 0, "cnf_units": 0,
             "peak_depth": 0, "elapsed_seconds": 0.0}
    equations_by_variable = Counter(
        v for mask, _ in equations
        for v in range(1, n + 1) if mask & (1 << (v - 1))
    )

    def solve(formula, assigned, depth):
        stats["calls"] += 1
        stats["peak_depth"] = max(stats["peak_depth"], depth)
        if max_calls is not None and stats["calls"] > max_calls:
            raise _CallLimit
        while True:
            if () in formula:
                return None
            stats["gaussian_calls"] += 1
            consistent, linear_forced, extension = _linear_solve(equations, assigned)
            if not consistent:
                stats["linear_conflicts"] += 1
                return None
            proposed = dict(linear_forced)
            for clause in formula:
                if len(clause) == 1:
                    v, value = abs(clause[0]), clause[0] > 0
                    if v in proposed and proposed[v] != value:
                        return None
                    proposed[v] = value
            new = {}
            for v, value in proposed.items():
                if v in assigned:
                    if assigned[v] != value:
                        return None
                else:
                    new[v] = value
                    if v in linear_forced:
                        stats["linear_forced"] += 1
                    else:
                        stats["cnf_units"] += 1
            if not new:
                break
            assigned = {**assigned, **new}
            formula = _restrict(formula, new)
        if not formula:
            full = {**assigned, **extension}
            return [full.get(v, False) for v in range(1, n + 1)]
        counts = Counter(abs(lit) for clause in formula for lit in clause)
        variable = min(counts, key=lambda v: (-counts[v],
                                              -equations_by_variable[v], v))
        for value in (False, True):
            stats["branches"] += 1
            chosen = {variable: value}
            found = solve(_restrict(formula, chosen), {**assigned, **chosen},
                          depth + 1)
            if found is not None:
                return found
        return None

    try:
        model = solve(residual, {}, 0)
    except _CallLimit:
        model = None
        stats["status"] = "limit_calls"
    stats["elapsed_seconds"] = perf_counter() - started
    if model is not None:
        assert verify(n, original, model)
    return model, stats
