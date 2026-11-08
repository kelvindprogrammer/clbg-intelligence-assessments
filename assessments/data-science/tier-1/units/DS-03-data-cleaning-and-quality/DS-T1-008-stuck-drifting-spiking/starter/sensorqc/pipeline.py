"""End-to-end QC and hourly aggregation (requirements R7-R8)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

from .types import QCResult


def _find_resources() -> Path:
    """Provided helper: find resources/reference in this directory or any parent."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "resources" / "reference"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("resources/reference not found. Keep resources/ next to your package.")


RESOURCES = _find_resources()
INPUT_COLUMNS = ["reading_id", "device_id", "device_time", "received_at", "pm25", "temp_c", "rh_pct"]
READING_COLUMNS = ["reading_id", "device_id", "device_time", "timestamp_utc", "variable", "value", "qc_flags", "qc_level"]
GAP_COLUMNS = ["device_id", "gap_start", "gap_end", "missing_samples"]
CLOCK_COLUMNS = ["device_id", "offset_s", "drift_s_per_day", "n_clock_step", "corrected"]
HOURLY_COLUMNS = ["device_id", "variable", "hour_utc", "n_good", "coverage", "mean", "status"]


def load_readings(path: str | Path) -> pd.DataFrame:
    """Provided helper: load the feed with every column as text and no automatic NA conversion."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)


def load_config(path: str | Path | None = None) -> dict:
    """Provided helper: read resources/reference/qc_config.json (or another config file)."""
    with open(Path(path) if path else RESOURCES / "qc_config.json", encoding="utf-8") as fh:
        return json.load(fh)


def load_devices() -> dict[str, str]:
    """Provided helper: {device_id: deployed_on} from resources/reference/devices.csv."""
    with open(RESOURCES / "devices.csv", encoding="utf-8") as fh:
        return {r["device_id"]: r["deployed_on"] for r in csv.DictReader(fh)}


def run_qc(raw: pd.DataFrame, config: dict) -> QCResult:
    """R7: apply every rule to every device and variable. Return QCResult(readings, gaps, clocks)."""
    raise NotImplementedError("R7: implement run_qc")


def hourly_means(readings: pd.DataFrame, min_coverage: float = 0.75, expected_interval_s: float = 300) -> pd.DataFrame:
    """R8: hourly means of 'good' readings per device and variable, with coverage and status."""
    raise NotImplementedError("R8: implement hourly_means")
