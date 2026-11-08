"""R1-R5: parsing and climate indicators.

The constants are part of the specification (README section D). Do not change them.
"""
from __future__ import annotations

import pandas as pd

MISSING = -999.0      # POWER's fill value for missing data
MIN_COVERAGE = 0.9    # a year counts only if at least 90% of its days have valid data
MIN_YEARS = 10        # a 15-year period needs at least 10 valid years to be compared


def read_power_csv(path) -> pd.DataFrame:
    """R1: parse a NASA POWER daily point CSV.

    Returns a DataFrame with a `date` column (datetime64) followed by one float column
    per parameter, named in lower case (e.g. t2m_max, prectotcorr), sorted by date.
    Handles the -BEGIN HEADER- ... -END HEADER- block (or no header at all), both the
    YEAR,DOY and the YEAR,MO,DY date layouts, and turns -999 into NaN.
    """
    raise NotImplementedError("R1: implement read_power_csv")


def annual_hot_days(df: pd.DataFrame, threshold: float, col: str = "t2m_max", min_coverage: float = MIN_COVERAGE) -> pd.Series:
    """R2: number of days per calendar year with `col >= threshold`, indexed by year.

    Years whose valid (non-NaN) days are fewer than min_coverage x days-in-that-year
    get NaN, never a smaller count.
    """
    raise NotImplementedError("R2: implement annual_hot_days")


def percentile_threshold(df: pd.DataFrame, q: float = 0.9, base: tuple[int, int] = (1991, 2005), col: str = "t2m_max") -> float:
    """R3: the q-quantile (numpy default method) of valid daily `col` values in the base years, inclusive."""
    raise NotImplementedError("R3: implement percentile_threshold")


def period_change(annual: pd.Series, base: tuple[int, int] = (1991, 2005), recent: tuple[int, int] = (2010, 2024)) -> dict:
    """R4: compare two periods of an annual series (years inclusive, NaN years ignored).

    Returns {"base_mean", "recent_mean", "change" (recent - base), "n_base", "n_recent"}.
    Raises ValueError if either period has fewer than MIN_YEARS valid years.
    """
    raise NotImplementedError("R4: implement period_change")


def monthly_climatology(df: pd.DataFrame, years: tuple[int, int], col: str = "t2m_max") -> pd.Series:
    """R5: mean of daily `col` per calendar month over the given years (inclusive), index 1..12."""
    raise NotImplementedError("R5: implement monthly_climatology")
