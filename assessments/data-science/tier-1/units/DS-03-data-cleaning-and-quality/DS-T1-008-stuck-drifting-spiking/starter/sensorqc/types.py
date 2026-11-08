"""Shared types and the flag scheme. These are provided, so you don't need to change them."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# Flag bits (README section D, "Flag scheme"). A reading's `flags` value is the bitwise OR of these.
MISSING = 1          # value absent
RANGE = 2            # outside the physical/instrument range
STUCK = 4            # part of a run of identical values that is too long
SPIKE = 8            # isolated departure from the local median (Hampel rule)
CLOCK_STEP = 16      # the device timestamp is not trustworthy for this reading
HUMIDITY = 32        # PM2.5 measured at high relative humidity (optical sensor bias)
DRIFT_CORRECTED = 64  # timestamp corrected for estimated clock drift (informational)

BAD_BITS = RANGE | STUCK | SPIKE | CLOCK_STEP
VARIABLES = ["pm25", "temp_c", "rh_pct"]


@dataclass(frozen=True)
class ClockEstimate:
    """The outcome of analysing one device's clock.

    offset_s:        fitted offset (received_at - device_time) at the first trustworthy reading, seconds
    drift_s_per_day: fitted slope of that offset, seconds per day (positive = device clock runs slow)
    step_mask:       boolean Series aligned with the inputs; True where the device time is not trustworthy
    """
    offset_s: float
    drift_s_per_day: float
    step_mask: pd.Series


@dataclass
class QCResult:
    readings: pd.DataFrame  # long format, one row per (raw row, variable)
    gaps: pd.DataFrame      # one row per detected gap
    clocks: pd.DataFrame    # one row per device
