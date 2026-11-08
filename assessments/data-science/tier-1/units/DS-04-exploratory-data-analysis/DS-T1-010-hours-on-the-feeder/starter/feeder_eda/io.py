"""Loading and constants (provided complete in the starter)."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

TIME_FORMAT = "%Y-%m-%d %H:%M"
PERIOD_START = dt.datetime(2025, 1, 1)
EXPORT_TIME = dt.datetime(2025, 7, 1)  # end of the analysis period and time of export
BAND_MIN_HOURS = {"A": 20, "B": 16, "C": 12, "D": 8, "E": 4}  # NERC service-based tariff minimums


def load_feeders(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["customers"] = df["customers"].astype(int)
    return df


def load_events(path: str | Path) -> pd.DataFrame:
    """Raw events: every column is text. Blank `end` means the event was never closed."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_coverage(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["logging_ok"] = df["logging_ok"].astype(int)
    return df


def load_all(data_dir: str | Path):
    d = Path(data_dir)
    return load_events(d / "outage_events.csv"), load_feeders(d / "feeders.csv"), load_coverage(d / "log_coverage.csv")
