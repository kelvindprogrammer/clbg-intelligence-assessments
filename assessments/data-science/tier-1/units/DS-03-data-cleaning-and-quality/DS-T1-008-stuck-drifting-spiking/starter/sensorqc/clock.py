"""Clock analysis (requirement R5).

The gateway's `received_at` is trustworthy (it is NTP-synchronised). A device's own
`device_time` is not. The difference between them is the network latency plus the device's
clock error. Latency is never negative, but it is sometimes very large.
"""
from __future__ import annotations

import pandas as pd

from .types import ClockEstimate


def estimate_clock(device_time: pd.Series, received_at: pd.Series, deployed_on: str,
                   future_tolerance_s: float = 300.0) -> ClockEstimate:
    """R5: return ClockEstimate(offset_s, drift_s_per_day, step_mask) for ONE device.

    step_mask must be aligned with the inputs (same index).
    """
    raise NotImplementedError("R5: implement estimate_clock")
