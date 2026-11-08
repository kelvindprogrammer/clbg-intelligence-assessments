"""Simulation and evidence from issued codes (requirements R5-R7)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"   # 31 symbols: no 0, 1, I, L, O


@dataclass(frozen=True)
class Interval:
    estimate: float
    lower: float
    upper: float


@dataclass(frozen=True)
class SpaceEstimate:
    n: int            # number of codes analysed
    pairs: int        # observed colliding pairs
    n_hat: float      # estimated effective space size (math.inf when no pair is observed)
    lower: float
    upper: float      # may be math.inf


def simulate_collision_prob(n: int, N: int, reps: int, rng: np.random.Generator, level: float = 0.95) -> Interval:
    """Monte Carlo estimate of the collision probability for n uniform draws from N values,
    with a Wilson score interval at `level`. All randomness from `rng`."""
    raise NotImplementedError("R5: implement simulate_collision_prob")


def count_colliding_pairs(codes) -> int:
    """Number of unordered pairs of positions holding the same code (a code issued m times gives m(m-1)/2)."""
    raise NotImplementedError("R6: implement count_colliding_pairs")


def estimate_space_size(codes, level: float = 0.95) -> SpaceEstimate:
    """Estimate the effective number of equally likely codes from the observed colliding pairs,
    using the moment estimator implied by expected_colliding_pairs, with an interval obtained by
    inverting an EXACT Poisson interval for the pair count. Raises ValueError for fewer than 2 codes."""
    raise NotImplementedError("R6: implement estimate_space_size")


def char_uniformity_pvalue(codes, alphabet: str = ALPHABET) -> float:
    """Chi-square goodness-of-fit p-value that symbols (pooled over positions) are uniform over
    `alphabet`. Raises ValueError if a code contains a symbol outside the alphabet."""
    raise NotImplementedError("R7: implement char_uniformity_pvalue")


def excess_collision_pvalue(codes, designed_space: float) -> float:
    """One-sided p-value P(pairs >= observed) if the codes really were uniform over designed_space,
    treating the pair count as Poisson with mean expected_colliding_pairs."""
    raise NotImplementedError("R7: implement excess_collision_pvalue")
