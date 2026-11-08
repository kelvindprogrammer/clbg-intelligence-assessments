"""Collision and guessing probabilities (requirements R1-R4).

All functions raise ValueError for invalid input (negative or non-integer n, N < 1,
probabilities outside their range). Results must be accurate for N up to at least 31**10 and
n up to at least 10**6: think about what happens to 1 - (something very close to 1) in
floating point.
"""
from __future__ import annotations


def p_collision_exact(n: int, N: float) -> float:
    """P(at least two of n independent uniform draws from N equally likely values coincide), exactly
    (no approximation beyond floating point). Returns 0 for n <= 1 and 1 for n > N."""
    raise NotImplementedError("R1: implement p_collision_exact")


def expected_colliding_pairs(n: int, N: float) -> float:
    """Expected number of unordered pairs (i < j) with equal draws."""
    raise NotImplementedError("R2: implement expected_colliding_pairs")


def p_collision_approx(n: int, N: float) -> float:
    """The Poisson approximation to p_collision_exact, based on expected_colliding_pairs."""
    raise NotImplementedError("R2: implement p_collision_approx")


def p_collision_nonuniform(n: int, probs) -> float:
    """Poisson approximation to the collision probability when value i has probability probs[i].
    Raises ValueError if probs is not a probability vector."""
    raise NotImplementedError("R3: implement p_collision_nonuniform")


def max_n_for_risk(N: float, risk: float) -> int:
    """Largest n with p_collision_exact(n, N) <= risk, for 0 < risk < 1."""
    raise NotImplementedError("R4: implement max_n_for_risk")


def guess_success_prob(active: int, N: float, guesses: int) -> float:
    """P(at least one of `guesses` independent uniform random guesses equals one of the
    `active` currently valid codes out of N)."""
    raise NotImplementedError("R4: implement guess_success_prob")


def min_code_length(alphabet_size: int, n_per_window: int, collision_risk: float,
                    guesses: int = 0, guess_risk: float = 1.0) -> int:
    """Smallest length L such that n_per_window random codes over alphabet_size**L values have an
    exact collision probability <= collision_risk and, if guesses > 0, a guessing success
    probability (with n_per_window active codes) <= guess_risk."""
    raise NotImplementedError("R4: implement min_code_length")
