"""climfuse: align daily gridded climate, annual crop statistics and annual indicators (DS-T2-004).

Only these six functions are fixed by the tests: they are the alignment primitives that every design
in your comparison depends on. Build your analysis (point selection, weighting, seasons, flags,
uncertainty) on top of them in modules and scripts of your own.
"""
from __future__ import annotations

import pandas as pd


def read_power(path) -> pd.DataFrame:
    """Daily NASA POWER point JSON -> long frame [date, parameter, value]; fill values become NaN (R1)."""
    raise NotImplementedError("R1: read_power")


def season_aggregate(daily: pd.DataFrame, start: str = "06-01", end: str = "09-30", how: str = "sum",
                     min_coverage: float = 0.9) -> pd.DataFrame:
    """Aggregate [date, value] daily data to one row per season-year (R2). See README for every rule."""
    raise NotImplementedError("R2: season_aggregate")


def weighted_mean(series: dict, weights: dict) -> pd.DataFrame:
    """Combine {name: Series(year -> value)} with {name: weight} into [year, value, weight_used] (R3)."""
    raise NotImplementedError("R3: weighted_mean")


def read_faostat_wide(path, area: str, items, element: str) -> pd.DataFrame:
    """FAOSTAT bulk wide CSV -> long [year, item, value, unit, flag] (R4)."""
    raise NotImplementedError("R4: read_faostat_wide")


def detrend(s: pd.Series, method: str = "linear") -> pd.Series:
    """Remove the trend from an annual series indexed by year (R5)."""
    raise NotImplementedError("R5: detrend")


def align(frames: dict, how: str = "inner") -> pd.DataFrame:
    """Join annual frames into one row per year, carrying provenance columns along (R6)."""
    raise NotImplementedError("R6: align")
