"""Event cleaning and interval arithmetic (R1, R2)."""
from __future__ import annotations

import datetime as dt

import pandas as pd

from .io import EXPORT_TIME

Interval = tuple[dt.datetime, dt.datetime]


def merge_intervals(intervals: list[Interval]) -> list[Interval]:
    """R2: return the union of half-open intervals [start, end) as a sorted list of disjoint intervals.

    Overlapping or touching intervals merge into one. Empty intervals (end <= start) are ignored.
    Works for datetime and for plain numbers.
    """
    raise NotImplementedError("R2: implement merge_intervals")


def parse_events(raw: pd.DataFrame, export_time: dt.datetime = EXPORT_TIME) -> tuple[pd.DataFrame, pd.DataFrame]:
    """R1: clean the raw event log and return (clean, issues).

    clean:  event_id, feeder_id, start, end (pandas Timestamps), cause, logged_by, closed_by,
            sorted by event_id. Invalid events are excluded; open events are closed by the rule in README R1.
    issues: event_id, issue_type (one row per invalid or open event), sorted by event_id.
    Never modify `raw`.
    """
    raise NotImplementedError("R1: implement parse_events")
