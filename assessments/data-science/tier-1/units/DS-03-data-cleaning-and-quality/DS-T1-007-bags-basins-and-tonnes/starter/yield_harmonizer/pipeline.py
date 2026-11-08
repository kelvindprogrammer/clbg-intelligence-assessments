"""End-to-end harmonisation and production totals (requirements R7-R8)."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from .types import HarmoniseResult
from .units import RESOURCES

INPUT_COLUMNS = ["record_id", "state", "lga", "enumerator_id", "interview_date", "crop",
                 "harvest_qty", "harvest_unit", "plot_area", "area_unit"]
RECORD_COLUMNS = ["record_id", "crop", "quantity", "unit", "kg", "kg_low", "kg_high", "conversion_grade",
                  "area_ha", "yield_kg_ha", "flags", "usable"]
ISSUE_COLUMNS = ["record_id", "column", "issue_type", "original_value", "action"]
TOTALS_COLUMNS = ["crop", "scenario", "n_records", "total_kg", "total_kg_low", "total_kg_high"]
SCENARIOS = ["unit_blind", "all_converted", "usable_only", "imputed"]
MAX_AREA_HA = 50.0  # README known fact: the sampling frame only covers holdings under 50 ha


def load_survey(path: str | Path) -> pd.DataFrame:
    """Provided helper: load the survey with EVERY column as text and no automatic NA conversion."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)


def load_crop_limits() -> dict[str, float]:
    """Provided helper: {crop: max_plausible_kg_ha} from resources/reference/crop_limits.csv."""
    with open(RESOURCES / "crop_limits.csv", encoding="utf-8") as fh:
        return {r["crop"]: float(r["max_plausible_kg_ha"]) for r in csv.DictReader(fh)}


def harmonise(raw: pd.DataFrame) -> HarmoniseResult:
    """R7: return HarmoniseResult(records, issues) with exactly RECORD_COLUMNS / ISSUE_COLUMNS."""
    raise NotImplementedError("R7: implement harmonise")


def production_totals(records: pd.DataFrame) -> pd.DataFrame:
    """R8: production totals per crop (and 'ALL') under each of SCENARIOS, with TOTALS_COLUMNS."""
    raise NotImplementedError("R8: implement production_totals")
