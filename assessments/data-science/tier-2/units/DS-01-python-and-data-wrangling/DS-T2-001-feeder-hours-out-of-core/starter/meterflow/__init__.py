"""meterflow: feeder supply hours from smart-meter data, with interchangeable engines.

The two public functions and the contract are fixed. How you structure the rest of the
package (one module per engine, shared helpers, a storage-conversion step) is your decision.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .contract import (BAND_MIN_HOURS, COMPLIANCE_COLUMNS, ENGINES, FEEDER_DAILY_COLUMNS,  # noqa: F401
                       FEEDER_DAILY_DTYPES)


def compute_feeder_daily(data_dir: str | Path, engine: str, *, memory_limit_mb: int | None = None) -> pd.DataFrame:
    """Return the feeder-day table (FEEDER_DAILY_COLUMNS) for the dataset in data_dir.

    data_dir contains readings/*.csv, meters.csv and feeders.csv (see README section E).
    engine is one of ENGINES. Every engine must return an identical table (README D.1).
    memory_limit_mb, when given, is a budget your engine must respect where the library
    lets you set one, and must design for otherwise (for example, chunk sizes).
    energy_kwh is the plain float sum (tests allow 1e-6); supply_hours = supplied_intervals / 2.
    """
    raise NotImplementedError("R1-R4: implement compute_feeder_daily for every engine")


def compute_compliance(feeder_daily: pd.DataFrame, feeders: pd.DataFrame) -> pd.DataFrame:
    """Return one row per feeder in `feeders` (COMPLIANCE_COLUMNS), sorted by feeder_id.

    days = number of feeder-days in feeder_daily; mean_supply_hours = mean of supply_hours
    (NaN if days == 0); share_days_meeting_band = share of those days with
    supply_hours >= band_min_hours (NaN if days == 0); compliant = mean_supply_hours >=
    band_min_hours (False if days == 0).
    """
    raise NotImplementedError("R5: implement compute_compliance")
