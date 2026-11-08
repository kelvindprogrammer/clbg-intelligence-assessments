"""Daily supply hours and per-feeder summaries (R3, R4)."""
from __future__ import annotations

import datetime as dt

import pandas as pd

from .io import EXPORT_TIME, PERIOD_START


def daily_supply(clean: pd.DataFrame, feeders: pd.DataFrame, coverage: pd.DataFrame,
                 start: dt.datetime = PERIOD_START, end: dt.datetime = EXPORT_TIME, merge: bool = True) -> pd.DataFrame:
    """R3: one row per feeder per calendar day in [start, end), sorted by feeder_id then date.

    Columns: feeder_id, date ("YYYY-MM-DD"), outage_hours, supply_hours, status ("ok" | "no_coverage").
    With merge=True, outage time is the union of the feeder's outage intervals. With merge=False
    (the naive method used for Q6), it is the plain sum of event durations. Either way, outage
    hours are capped at 24. Days whose business unit had logging_ok == 0 get status "no_coverage"
    and NaN hours.
    """
    raise NotImplementedError("R3: implement daily_supply")


def feeder_summary(daily: pd.DataFrame, feeders: pd.DataFrame) -> pd.DataFrame:
    """R4: one row per feeder, computed over "ok" days only.

    Columns: feeder_id, band, days_observed, mean_supply, median_supply, p10_supply,
    share_days_meeting_band, meets_band_on_average.
    """
    raise NotImplementedError("R4: implement feeder_summary")
