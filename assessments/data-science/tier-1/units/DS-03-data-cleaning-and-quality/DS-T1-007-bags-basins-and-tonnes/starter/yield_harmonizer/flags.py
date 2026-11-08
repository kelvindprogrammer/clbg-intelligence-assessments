"""Robust plausibility rules (requirement R6).

Both functions take a Series of values (yields in kg/ha) and return a boolean Series with
the SAME index. Only strictly positive values take part in the computation or can be
flagged; zeros, negatives and NaN always get False. The exact definitions are in README R6.
"""
from __future__ import annotations

import pandas as pd


def mad_flags(values: pd.Series, k: float = 3.5) -> pd.Series:
    """R6: modified z-score rule on log(values). Flag |z| > k."""
    raise NotImplementedError("R6: implement mad_flags")


def iqr_flags(values: pd.Series, k: float = 1.5) -> pd.Series:
    """R6: Tukey fences on log(values). Flag values outside [Q1 - k*IQR, Q3 + k*IQR]."""
    raise NotImplementedError("R6: implement iqr_flags")
