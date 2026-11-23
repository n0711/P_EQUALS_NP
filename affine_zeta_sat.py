"""M12: certified counting and zeta coefficients for recognized affine CNF.

This module ONLY handles the conservative complete-XOR-block grammar already
implemented by structural_hybrid_sat.try_affine_sat (supports widths 1..3).
It never treats unrecognized CNF as UNSAT and never uses enumeration for
recognized inputs.

For a consistent system of linear equations Ax=b over GF(2), with n named
Boolean variables and rank r, the EXACT number of models is 2**(n-r).
For an inconsistent system the number of models is zero.

Computing rank and this (n+1)-bit model-count integer takes polynomial
time/bit complexity in an explicitly represented CNF input. Coefficients
of the local zeta function are computed only for requested finite degree;
their output size must be included in complexity accounting.

Neither this code nor the Riemann-zeta representation proves P=NP or P!=NP.
"""
from __future__ import annotations

from structural_hybrid_sat import try_affine_sat
from zeta_sat import local_zeta_coefficients


def affine_zeta_profile(n, clauses, *, local_degree=3):
    """Compute an exact #SAT and local zeta profile on recognized affine CNF.

    Returns one of:
      status='counted', model_count=int, local_coefficients=tuple,
      rank=int, free_variables=int or None, witness=list or None;
      status='unrecognized', model_count=None, local_coefficients=None.

    Zero models is a *proved* UNSAT outcome only when recognition succeeds.
    Unrecognized means the formula may be satisfiable or unsatisfiable.
    The caller must use a separate general SAT decision method if needed.

    local_degree is a nonnegative integer; producing degree d output costs
    polynomial time in n, explicit CNF size and d, not in log(d).
    """
    if type(local_degree) is not int or local_degree < 0:
        raise ValueError("local_degree must be a nonnegative integer")
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")

    recognized, witness, stats = try_affine_sat(n, clauses)
    if not recognized:
        return {
            "status": "unrecognized",
            "model_count": None,
            "local_coefficients": None,
            "rank": None,
            "free_variables": None,
            "witness": None,
        }

    rank = stats["rank"]
    if rank < 0 or rank > n:
        raise AssertionError("affine recognizer reported invalid rank")

    count = 0 if witness is None else 1 << (n - rank)
    return {
        "status": "counted",
        "model_count": count,
        "local_coefficients": local_zeta_coefficients(count, local_degree),
        "rank": rank,
        "free_variables": n - rank if count else None,
        "witness": witness,
    }
