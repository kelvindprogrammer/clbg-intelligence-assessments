"""Rates with uncertainty (R1, R2)."""
from __future__ import annotations

import pandas as pd


def wilson_interval(events: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """R1: return the Wilson score interval (low, high) for `events` successes out of `n`.

    Raise ValueError if n <= 0 or events is outside [0, n]. Bounds are clipped to [0, 1].
    """
    raise NotImplementedError("R1: implement wilson_interval")


def rate_table(df: pd.DataFrame, by: list[str], outcome: str = "died_30d", z: float = 1.96) -> pd.DataFrame:
    """R2: one row per combination of the `by` columns, sorted by them.

    Columns, in order: *by, n, events, rate, ci_low, ci_high. `n` and `events` are ints,
    `rate = events / n`, and the interval is the Wilson interval at the given z.
    """
    raise NotImplementedError("R2: implement rate_table")
