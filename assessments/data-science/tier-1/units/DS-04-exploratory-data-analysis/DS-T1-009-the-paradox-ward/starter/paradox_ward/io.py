"""Loading (provided complete in the starter)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

INPUT_COLUMNS = ["admission_id", "hospital", "admission_month", "age_band", "sex", "triage_category",
                 "referral_source", "procedure_group", "los_days", "died_30d"]
CANDIDATE_STRATIFIERS = ["age_band", "sex", "triage_category", "referral_source"]


def load_admissions(path: str | Path) -> pd.DataFrame:
    """Read admissions.csv with explicit types. triage_category, los_days and died_30d are integers."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in ["triage_category", "los_days", "died_30d"]:
        df[c] = df[c].astype(int)
    return df[INPUT_COLUMNS]
