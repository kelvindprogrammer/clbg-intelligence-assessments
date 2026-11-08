"""Provided loader."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_rainfall(path: str | Path) -> pd.DataFrame:
    """Load rainfall.csv: station_id (str), date (datetime64[ns]), rain_mm (float64, NaN = missing).

    Rows are returned in file order. Nothing is sorted, filled or dropped.
    """
    df = pd.read_csv(path, dtype={"station_id": str, "rain_mm": "float64"}, keep_default_na=False,
                     na_values={"rain_mm": [""]})
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d").astype("datetime64[ns]")
    return df[["station_id", "date", "rain_mm"]]
