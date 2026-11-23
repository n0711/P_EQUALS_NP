"""M11: exact arithmetic-zeta invariants of the Boolean SAT scheme.

For the M10 quadratic encoding E(F), X_F is the finite Z-scheme
representing satisfying assignments. For each prime p and r>=1,
#X_F(F_(p^r)) = #SAT(F) = S, and the arithmetic zeta is zeta(s)**S.
This established identity is NOT a polynomial-time way to find S.
Only bounded exhaustive counting is implemented here.
"""
from __future__ import annotations

from itertools import product

from rh_grh_bridge import _normalized


def count_sat_bounded(n, clauses, *, max_variables=16):
    """Enumerate satisfying assignments; O(2**n * input_size) time.

    This is a demonstration/reference implementation, NOT an efficient
    algorithm for arbitrary SAT instances. Explicitly refuses large n.
    """
    if type(max_variables) is not int or max_variables < 0:
        raise ValueError("max_variables must be a nonnegative integer")
    clauses = _normalized(n, clauses)
    if n > max_variables:
        raise ValueError("exhaustive #SAT disabled above max_variables")
    return sum(
        all(
            any(bits[abs(lit) - 1] == int(lit > 0) for lit in clause)
            for clause in clauses
        )
        for bits in product((0, 1), repeat=n)
    )


def local_zeta_coefficients(model_count, degree):
    """Return [t^0,...,t^degree] in Z_X(t)=(1-t)^(-model_count).

    This formula holds for the finite Boolean scheme over any prime field.
    Requires S=#SAT as *input*: does not compute or approximate S.
    """
    if type(model_count) is not int or model_count < 0:
        raise ValueError("model_count must be a nonnegative integer")
    if type(degree) is not int or degree < 0:
        raise ValueError("degree must be a nonnegative integer")
    coefficients = [1]
    for k in range(1, degree + 1):
        previous = coefficients[-1]
        numerator = previous * (model_count + k - 1)
        coefficients.append(numerator // k)
        assert numerator % k == 0
    return tuple(coefficients)


def pole_order_at_one(model_count):
    """Pole order of global zeta_X(s) at s=1: S (zero if no pole).

    Returns S supplied by the caller: no analytic evaluation is used.
    """
    if type(model_count) is not int or model_count < 0:
        raise ValueError("model_count must be a nonnegative integer")
    return model_count


def symbolic_euler_exponent(model_count):
    """Return exponent S for zeta_X(s)=zeta(s)^S, Re(s)>1.

    Not an algorithm to recover S from a CNF formula.
    """
    return pole_order_at_one(model_count)
