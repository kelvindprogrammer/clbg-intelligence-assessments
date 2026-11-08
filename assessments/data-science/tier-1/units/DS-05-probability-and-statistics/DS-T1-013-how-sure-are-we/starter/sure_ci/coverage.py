"""Coverage experiments (requirement R5)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class CoverageResult:
    coverage: float      # share of intervals containing the true value
    mc_se: float         # Monte Carlo standard error of `coverage`
    mean_width: float
    miss_below: float    # share of intervals lying entirely BELOW the true value (upper < truth)
    miss_above: float    # share of intervals lying entirely ABOVE the true value (lower > truth)
    reps: int


def coverage_experiment(sampler: Callable, true_value: float, method: Callable, n: int, reps: int,
                        rng: np.random.Generator) -> CoverageResult:
    """Estimate the coverage of an interval method by simulation.

    sampler(rng, n) returns one sample of size n; method(sample, rng) returns (lower, upper).
    Draw `reps` samples, build one interval per sample, and summarise. An interval whose
    endpoint equals the true value counts as covering it.
    """
    raise NotImplementedError("R5: implement coverage_experiment")
