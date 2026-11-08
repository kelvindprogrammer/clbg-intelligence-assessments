"""The output contract for DS-T2-001. Fixed: the tests import it. Do not change it.

Definitions (README section D.1 is the authoritative text):

  reading          one row of readings/*.csv after removing exact duplicates
                   (same meter_id, interval_start and kwh), wherever they appear
  date             the local (WAT) calendar date of interval_start, NOT the file name
  reporting meter  a meter with at least one reading in the interval (or day)
  supplied         an interval of a feeder is supplied when at least one of its meters
                   reports and at least half of the reporting meters have kwh > 0
"""
from __future__ import annotations

ENGINES = ("pandas_inmemory", "pandas_chunked", "polars", "duckdb")

BAND_MIN_HOURS = {"A": 20, "B": 16, "C": 12, "D": 8, "E": 4}

# one row per (feeder_id, date) with at least one reading; sorted by feeder_id, date
FEEDER_DAILY_COLUMNS = ["feeder_id", "date", "reporting_meters", "energy_kwh", "supplied_intervals", "supply_hours"]
FEEDER_DAILY_DTYPES = {"reporting_meters": "int64", "energy_kwh": "float64", "supplied_intervals": "int64",
                       "supply_hours": "float64"}

# one row per feeder in feeders.csv; sorted by feeder_id
COMPLIANCE_COLUMNS = ["feeder_id", "band", "band_min_hours", "days", "mean_supply_hours",
                      "share_days_meeting_band", "compliant"]
