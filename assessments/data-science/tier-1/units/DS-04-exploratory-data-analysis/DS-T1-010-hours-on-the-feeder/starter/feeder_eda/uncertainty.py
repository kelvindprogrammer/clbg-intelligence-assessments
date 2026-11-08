"""Bootstrap intervals and band-level summaries (R5-R7).

The resampling procedures are specified exactly in README R5-R7 so that results are
reproducible with a fixed seed. Follow them precisely.
"""
from __future__ import annotations

import pandas as pd


def block_bootstrap_mean_ci(values, block: int = 7, n_boot: int = 2000, seed: int = 0,
                            alpha: float = 0.05) -> tuple[float, float]:
    """R5: non-overlapping block bootstrap percentile interval for the mean of a date-ordered series.

    NaN values are dropped first. Raise ValueError if nothing is left.
    """
    raise NotImplementedError("R5: implement block_bootstrap_mean_ci")


def flag_misbanded(daily: pd.DataFrame, feeders: pd.DataFrame, n_boot: int = 2000, seed: int = 0) -> pd.DataFrame:
    """R6: one row per feeder: feeder_id, band, band_min, mean_supply, ci_low, ci_high, misbanded."""
    raise NotImplementedError("R6: implement flag_misbanded")


def band_summary(daily: pd.DataFrame, feeders: pd.DataFrame, n_boot: int = 2000, seed: int = 0) -> pd.DataFrame:
    """R7: one row per band (A..E): band, n_feeders, mean_supply, ci_low, ci_high, band_min."""
    raise NotImplementedError("R7: implement band_summary")
