"""R8 and R9: reconcile the agencies and find what disagrees."""
from __future__ import annotations

import pandas as pd

KEY = ["market_id", "commodity_id", "week_start"]


def reconcile(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (market, commodity, week) with at least one valid price. Columns in README R8."""
    raise NotImplementedError("R8: reconcile")


def discrepancies(df: pd.DataFrame, tol: float = 0.15, min_sources: int = 3) -> pd.DataFrame:
    """Observations that deviate from the key's cross-source median by more than `tol`. See README R8."""
    raise NotImplementedError("R8: discrepancies")


def stale_runs(df: pd.DataFrame, min_run: int = 4) -> pd.DataFrame:
    """Runs of at least `min_run` identical consecutive valid prices within one source's series. See README R9."""
    raise NotImplementedError("R9: stale_runs")
