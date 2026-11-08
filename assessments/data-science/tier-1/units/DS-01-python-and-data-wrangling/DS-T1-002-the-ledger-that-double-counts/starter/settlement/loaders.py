"""File loaders. These are correct and are provided as-is."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_transactions(path: str | Path) -> pd.DataFrame:
    """Load the switch feed. Every column is text except amount_ngn (float64)."""
    tx = pd.read_csv(path, dtype=str, keep_default_na=False)
    tx["amount_ngn"] = tx["amount_ngn"].astype("float64")
    return tx


def load_agents(path: str | Path) -> pd.DataFrame:
    """Load the agent tier history. valid_to is "" for the current row."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_control_totals(path: str | Path) -> pd.DataFrame:
    """Load the switch's daily control totals."""
    ctrl = pd.read_csv(path, dtype={"business_date": str})
    ctrl["successful_count"] = ctrl["successful_count"].astype("int64")
    ctrl["successful_value_ngn"] = ctrl["successful_value_ngn"].astype("float64")
    return ctrl
