"""Quadratic integer-polynomial encoding of CNF-SAT (research milestone M10).

This reduction is unconditional. It does not assume RH or GRH and does not
give a polynomial-time algorithm for deciding arbitrary CNF-SAT.
A polynomial is a dict mapping a sorted tuple of 1-based variable indices
(with repetition) to its integer coefficient; () denotes the constant term.
"""
from __future__ import annotations


def _add(a, b, sign=1):
    out = dict(a)
    for monomial, coefficient in b.items():
        out[monomial] = out.get(monomial, 0) + sign * coefficient
        if out[monomial] == 0:
            del out[monomial]
    return out


def _multiply(a, b):
    out = {}
    for left, ca in a.items():
        for right, cb in b.items():
            monomial = tuple(sorted(left + right))
            out[monomial] = out.get(monomial, 0) + ca * cb
            if out[monomial] == 0:
                del out[monomial]
    return out


def _variable(i):
    return {(i,): 1}


def _false_factor(literal):
    # A positive literal is false if x=0; a negative one if x=1.
    # A clause is false exactly when the product of these factors is 1.
    if literal > 0:
        return {(): 1, (literal,): -1}
    return {(-literal,): 1}


def _normalized(n, clauses):
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    result = []
    for clause in clauses:
        validated = []
        for literal in clause:
            if type(literal) is not int or literal == 0 or abs(literal) > n:
                raise ValueError("literals must be signed, nonzero variable IDs in 1..n")
            validated.append(literal)
        result.append(tuple(validated))
    return result


def cnf_to_quadratic_system(n, clauses):
    """Return (number_of_variables, polynomial_equations).

    All returned equations have degree at most two and O(1) monomials per
    equation. O(n + total literal occurrences + number of clauses) output
    equations/variables; encoding indices adds logarithmic factors.
    Every zero over any field forces an original Boolean satisfying assignment.
    """
    clauses = _normalized(n, clauses)
    equations = [
        _add({(i, i): 1}, {(i,): 1}, -1)
        for i in range(1, n + 1)
    ]
    total = n
    for clause in clauses:
        factors = [_false_factor(lit) for lit in clause]
        if not factors:
            equations.append({(): 1})  # 1=0: empty clause
        elif len(factors) == 1:
            equations.append(factors[0])
        elif len(factors) == 2:
            equations.append(_multiply(factors[0], factors[1]))
        else:
            total += 1
            equations.append(
                _add(_variable(total), _multiply(factors[0], factors[1]), -1)
            )
            for factor in factors[2:-1]:
                previous = total
                total += 1
                equations.append(
                    _add(_variable(total), _multiply(_variable(previous), factor), -1)
                )
            equations.append(_multiply(_variable(total), factors[-1]))
    # Explicit Boolean constraints on auxiliary variables simplify the proof.
    equations.extend(
        _add({(i, i): 1}, {(i,): 1}, -1)
        for i in range(n + 1, total + 1)
    )
    return total, equations


def evaluate_equation(polynomial, values, modulus=None):
    """Evaluate at integer values; modulus may be a prime for field tests."""
    if modulus is not None and (type(modulus) is not int or modulus < 2):
        raise ValueError("modulus must be an integer >= 2")
    result = 0
    for monomial, coefficient in polynomial.items():
        term = coefficient
        for variable_id in monomial:
            term *= values[variable_id - 1]
        result += term
    return result if modulus is None else result % modulus


def is_common_zero(equations, values, modulus=None):
    return all(evaluate_equation(e, values, modulus) == 0 for e in equations)


def lift_boolean_assignment(n, clauses, values):
    """Extend a Boolean assignment to the auxiliary prefix-product variables.

    The returned tuple is a common zero iff the original assignment satisfies
    the CNF. A nonsatisfying assignment still has a well-defined extension.
    """
    clauses = _normalized(n, clauses)
    if len(values) != n or any(v not in (0, 1) for v in values):
        raise ValueError("values must be a Boolean assignment of length n")
    lifted = [int(value) for value in values]
    for clause in clauses:
        falsities = [
            (1 - lifted[lit - 1]) if lit > 0 else lifted[-lit - 1]
            for lit in clause
        ]
        if len(falsities) >= 3:
            running = falsities[0] * falsities[1]
            lifted.append(running)
            for factor in falsities[2:-1]:
                running *= factor
                lifted.append(running)
    return tuple(lifted)
