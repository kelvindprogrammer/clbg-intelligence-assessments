"""Loading (provided complete in the starter)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

FLAWS = ["none", "survivorship_bias", "base_rate_neglect", "log_scale_misread", "confounding", "ecological_fallacy",
         "regression_to_the_mean", "percentage_point_confusion", "multiple_comparisons", "simpsons_paradox",
         "selection_on_outcome", "unit_error", "overfitting"]
VERDICTS = ["supported", "unsupported"]
CLAIM_IDS = [f"C{i}" for i in range(1, 11)]


def load_agents(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in ["trained", "q1_bottom_120", "coached_q2"]:
        df[c] = df[c].astype(int)
    return df


def load_activity(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"agent_id": str, "month": str}, keep_default_na=False)
    for c in ["txn_count", "txn_value_ngn", "float_balance_avg_ngn", "fraud_flagged", "fraud_confirmed"]:
        df[c] = df[c].astype("int64")
    return df


def load_all(data_dir: str | Path):
    d = Path(data_dir)
    return load_agents(d / "agents.csv"), load_activity(d / "monthly_activity.csv")
