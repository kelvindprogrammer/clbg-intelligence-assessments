"""R1-R5: the numbers behind honest uncertainty displays.

QuantileCrossingError, level_columns and quantile_columns are provided. The rest is yours.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class QuantileCrossingError(ValueError):
    """Raised when a quantile table is not non-decreasing across its quantile columns."""


def wilson_interval(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """R1: the Wilson score interval (lo, hi) for k successes out of n.

    Raise ValueError unless 0 <= k <= n, n > 0 and 0 < level < 1.
    """
    raise NotImplementedError("R1: implement wilson_interval")


def quantile_dots(samples, n_dots: int = 20) -> np.ndarray:
    """R2: the n_dots sample quantiles at probabilities (i + 0.5) / n_dots, i = 0..n_dots-1.

    Use numpy's default (linear) quantile method. Raise ValueError for n_dots < 1,
    empty samples, or any NaN.
    """
    raise NotImplementedError("R2: implement quantile_dots")


def stack_dots(values, bin_width: float, origin: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """R3: (x, y) dot positions for a stacked dotplot, in sorted value order.

    Bins are [origin + j*bin_width, origin + (j+1)*bin_width). x is the bin centre and
    y is the 0-based stack height within the bin. Raise ValueError for bin_width <= 0.
    """
    raise NotImplementedError("R3: implement stack_dots")


def prob_exceed(samples, threshold: float) -> float:
    """R4: the share of samples strictly greater than threshold."""
    raise NotImplementedError("R4: implement prob_exceed")


def level_columns(level: float) -> tuple[str, str]:
    """Provided helper: the quantile column names bounding a central interval.

    level_columns(0.8) == ("q0.1", "q0.9").
    """
    lo, hi = (1 - level) / 2, (1 + level) / 2
    return f"q{round(lo, 6):g}", f"q{round(hi, 6):g}"


def quantile_columns(df: pd.DataFrame) -> list[str]:
    """Provided helper: the 'q<prob>' columns of df, sorted by probability."""
    cols = [c for c in df.columns if c.startswith("q")]
    return sorted(cols, key=lambda c: float(c[1:]))


def check_quantiles(df: pd.DataFrame) -> list[int]:
    """R5a: positional row indices (0-based) whose quantile values decrease anywhere
    as the probability increases. An empty list means the table is coherent."""
    raise NotImplementedError("R5: implement check_quantiles")


def repair_quantiles(df: pd.DataFrame) -> pd.DataFrame:
    """R5b: return a NEW DataFrame in which every row's quantile values are rearranged
    into non-decreasing order (monotone rearrangement). Other columns are unchanged."""
    raise NotImplementedError("R5: implement repair_quantiles")
