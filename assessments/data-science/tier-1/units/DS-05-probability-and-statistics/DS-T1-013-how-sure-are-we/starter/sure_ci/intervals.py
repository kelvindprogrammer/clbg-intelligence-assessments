"""Analytical intervals (requirements R1-R2).

Every function returns (lower, upper) as Python floats and raises ValueError for invalid
input (level outside (0, 1); a sample that is not 1-D or has fewer than 2 values; counts that
are not integers with 0 <= k <= n and n > 0). Proportion intervals are clipped to [0, 1].
"""
from __future__ import annotations


def t_interval(x, level: float = 0.95) -> tuple[float, float]:
    """Student-t interval for a population mean."""
    raise NotImplementedError("R1: implement t_interval")


def wald_interval(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Wald (normal-approximation) interval for a proportion, k successes in n trials."""
    raise NotImplementedError("R2: implement wald_interval")


def wilson_interval(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for a proportion (derive it by inverting the score test)."""
    raise NotImplementedError("R2: implement wilson_interval")


def clopper_pearson_interval(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact (Clopper-Pearson) interval for a proportion via beta quantiles. You may use scipy.stats.beta."""
    raise NotImplementedError("R2: implement clopper_pearson_interval")
