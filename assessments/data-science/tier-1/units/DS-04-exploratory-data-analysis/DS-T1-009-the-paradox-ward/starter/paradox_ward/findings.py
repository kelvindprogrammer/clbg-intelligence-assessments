"""Machine-readable findings (R8)."""
from __future__ import annotations

import pandas as pd


def build_findings(df: pd.DataFrame, group_col: str = "hospital", outcome: str = "died_30d") -> dict:
    """R8: return the findings dictionary whose keys are listed in README R8.

    Every value must be computed from `df`. Nothing may be hard-coded, because the hidden
    tests run this on a differently generated dataset.
    """
    raise NotImplementedError("R8: implement build_findings")
