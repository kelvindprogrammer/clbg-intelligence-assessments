"""Value-sequence rules (requirements R1-R4 and R6).

Every rule takes a Series and returns a boolean Series with the SAME index. Sequence rules
(stuck, spike) treat the Series as already being in measurement order: putting it in that
order is the pipeline's job, not the rule's. The exact definitions are in README section D.
"""
from __future__ import annotations

import pandas as pd


def range_flags(values: pd.Series, lo: float, hi: float) -> pd.Series:
    """R1: True where a value is present and lies outside [lo, hi]. NaN is never flagged."""
    raise NotImplementedError("R1: implement range_flags")


def stuck_flags(values: pd.Series, min_run: int) -> pd.Series:
    """R2: True for every element of a run of >= min_run consecutive identical non-NaN values."""
    raise NotImplementedError("R2: implement stuck_flags")


def spike_flags(values: pd.Series, half_window: int, k: float, min_abs: float) -> pd.Series:
    """R3: Hampel rule. True where |x - local median| > max(k * 1.4826 * local MAD, min_abs)."""
    raise NotImplementedError("R3: implement spike_flags")


def find_gaps(times: pd.Series, expected_interval_s: float) -> pd.DataFrame:
    """R4: one row per gap with columns gap_start, gap_end, missing_samples."""
    raise NotImplementedError("R4: implement find_gaps")


def qc_level(flags: int) -> str:
    """R6: map a flag bitmask to 'missing', 'bad', 'suspect' or 'good'."""
    raise NotImplementedError("R6: implement qc_level")
