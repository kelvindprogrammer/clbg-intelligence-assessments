"""Grid-collapse detection and the answers file (R8, R9)."""
from __future__ import annotations

import pandas as pd


def grid_collapse_days(clean: pd.DataFrame, feeders: pd.DataFrame, coverage: pd.DataFrame,
                       threshold: float = 0.8) -> list[str]:
    """R8: sorted "YYYY-MM-DD" dates on which at least `threshold` of the feeders whose business
    unit was covered that day had an `upstream_grid` event overlapping the date."""
    raise NotImplementedError("R8: implement grid_collapse_days")


def build_answers(raw_events: pd.DataFrame, feeders: pd.DataFrame, coverage: pd.DataFrame,
                  n_boot: int = 2000, seed: int = 0) -> dict:
    """R9: return the answers dictionary with keys q1..q6 exactly as described in README R9."""
    raise NotImplementedError("R9: implement build_answers")
