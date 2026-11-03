"""End-to-end pipeline (requirements R9, R11, R12)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .types import CleanResult

INPUT_COLUMNS = ["record_id", "matric_no", "full_name", "date_of_birth", "state_of_origin", "phone",
                 "email", "jamb_score", "admission_date", "department", "level", "cgpa"]
OUTPUT_COLUMNS = ["student_id", "source_record_ids", "matric_no", "first_name", "last_name", "date_of_birth",
                  "dob_status", "state_of_origin", "phone_e164", "email", "jamb_score", "admission_date",
                  "department", "level", "cgpa_5pt", "cgpa_rescaled"]
ISSUE_COLUMNS = ["record_id", "column", "issue_type", "original_value", "action"]


def load_export(path: str | Path) -> pd.DataFrame:
    """Provided helper: load the export with EVERY column as text and no automatic NA conversion.

    pandas would otherwise turn 'NA', 'null' and '' into NaN, destroying the evidence
    you need in order to tell different kinds of missingness apart.
    """
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)


def clean_registry(raw: pd.DataFrame) -> CleanResult:
    """R9: return CleanResult(clean, issues) with exactly OUTPUT_COLUMNS / ISSUE_COLUMNS."""
    raise NotImplementedError("R9: implement clean_registry")
