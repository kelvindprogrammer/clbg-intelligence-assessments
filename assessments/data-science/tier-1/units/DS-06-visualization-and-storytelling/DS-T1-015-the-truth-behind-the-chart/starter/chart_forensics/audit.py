"""R1-R4: what the chart shows, and what is wrong with it.

CODES and WINDOW_COVERAGE_MAX are part of the specification. Do not change them.
"""
from __future__ import annotations

import pandas as pd

CODES = ("TRUNCATED_AXIS", "DUAL_AXIS", "CHERRY_PICKED_WINDOW", "AREA_DISTORTION",
         "MISLEADING_COLORMAP", "INVERTED_AXIS", "MISSING_SOURCE")
WINDOW_COVERAGE_MAX = 0.5


def displayed_rows(spec: dict, df: pd.DataFrame) -> pd.DataFrame:
    """R1: the rows the published chart actually shows, with a fresh 0..n-1 index.

    No filter means every row. A filter keeps the rows from the first row whose
    filter field equals `from` to the first row whose field equals `to`, inclusive,
    comparing values as strings. Unknown or reversed bounds raise ValueError.
    """
    raise NotImplementedError("R1: implement displayed_rows")


def trend_slope(values) -> float:
    """R2: ordinary least-squares slope of `values` against positions 0..n-1.

    Fewer than two values raise ValueError.
    """
    raise NotImplementedError("R2: implement trend_slope")


def lie_factor(spec: dict, df: pd.DataFrame) -> float:
    """R3: Tufte's lie factor between the first and last displayed rows.

    Defined only for marks "bar", "area" and "bubble"; other marks raise ValueError,
    as does an undefined data effect. README section D.1 (R3) defines the graphic size.
    """
    raise NotImplementedError("R3: implement lie_factor")


def audit(spec: dict, df: pd.DataFrame) -> set[str]:
    """R4: the set of defect codes from CODES that apply to this chart (empty if honest)."""
    raise NotImplementedError("R4: implement audit")
