"""Bootstrap intervals from scratch (requirements R3-R4).

`stat` is a VECTORISED statistic with the NumPy reduction signature `stat(arr, axis=-1)`,
for example np.mean or np.median. Calling it on a (B, n) array must return B values.
All randomness comes from the `rng` argument (a numpy.random.Generator).
scipy.stats.bootstrap must NOT be used in this module (you may use it in your own tests).
"""
from __future__ import annotations

import numpy as np


def bootstrap_replicates(x, stat, B: int, rng: np.random.Generator) -> np.ndarray:
    """Return B nonparametric bootstrap replicates of stat(x), shape (B,).
    Raises ValueError if x is not 1-D with at least 2 values, or if B < 1."""
    raise NotImplementedError("R3: implement bootstrap_replicates")


def percentile_interval(x, stat, B: int = 2000, level: float = 0.95, rng=None) -> tuple[float, float]:
    """Percentile bootstrap interval (use np.quantile with its default interpolation)."""
    raise NotImplementedError("R3: implement percentile_interval")


def basic_interval(x, stat, B: int = 2000, level: float = 0.95, rng=None) -> tuple[float, float]:
    """Basic (reverse-percentile) bootstrap interval."""
    raise NotImplementedError("R3: implement basic_interval")


def jackknife_values(x, stat) -> np.ndarray:
    """The n leave-one-out values of stat, in the order of the omitted observation."""
    raise NotImplementedError("R4: implement jackknife_values")


def bca_interval(x, stat, B: int = 2000, level: float = 0.95, rng=None) -> tuple[float, float]:
    """Bias-corrected and accelerated (BCa) bootstrap interval (Efron 1987).

    The bias correction z0 uses the proportion of replicates strictly less than stat(x);
    the acceleration uses the jackknife. If every replicate is identical, return (value, value).
    Your code must not produce infinite or NaN endpoints when that proportion is 0 or 1.
    """
    raise NotImplementedError("R4: implement bca_interval")
