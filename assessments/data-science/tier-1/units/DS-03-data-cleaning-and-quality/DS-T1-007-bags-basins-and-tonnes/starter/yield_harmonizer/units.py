"""Value-level parsing and unit conversion (requirements R1-R5).

Every parser takes ONE raw string from the survey and returns a canonical value or None.
None means "missing or not confidently recoverable". Never guess a unit, and never invent
a conversion factor that is not in resources/reference/unit_conversions.csv.

Write your rules from evidence you gathered while profiling, and pin each one with a
test in tests/test_member_*.py.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from .types import Conversion


def _find_resources() -> Path:
    """Provided helper: find resources/reference in this directory or any parent."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "resources" / "reference"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("resources/reference not found. Keep resources/ next to your package.")


RESOURCES = _find_resources()
CANONICAL_UNITS = ["kg", "tonne", "bag_100", "bag_50", "basin", "mudu", "paint_bucket"]
CANONICAL_AREA_UNITS = ["ha", "acre", "m2"]


def load_conversion_table(path: str | Path | None = None) -> dict:
    """Provided helper: read unit_conversions.csv.

    Returns {(crop, unit): (kg_per_unit, kg_low, kg_high, grade)}.
    """
    path = Path(path) if path else RESOURCES / "unit_conversions.csv"
    out = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[(r["crop"], r["unit"])] = (float(r["kg_per_unit"]), float(r["kg_low"]), float(r["kg_high"]), r["grade"])
    return out


def is_missing(value: object) -> bool:
    """R1: True for None/NaN and for the survey's missing-value tokens. "0" is NOT missing."""
    raise NotImplementedError("R1: implement is_missing")


def parse_quantity(value: object) -> Optional[float]:
    """R2: parse a raw quantity (harvest or area) into a non-negative float, or None."""
    raise NotImplementedError("R2: implement parse_quantity")


def normalize_unit(value: object) -> Optional[str]:
    """R3: map a raw harvest-unit string to one of CANONICAL_UNITS, or None if unrecognised."""
    raise NotImplementedError("R3: implement normalize_unit")


def normalize_area_unit(value: object) -> Optional[str]:
    """R4: map a raw area-unit string to one of CANONICAL_AREA_UNITS, or None."""
    raise NotImplementedError("R4: implement normalize_area_unit")


def parse_area_ha(value: object, unit: object) -> Optional[float]:
    """R4: return the plot area in hectares, or None if missing, non-positive or in an unknown unit."""
    raise NotImplementedError("R4: implement parse_area_ha")


def to_kg(quantity: Optional[float], unit: Optional[str], crop: str, table: dict | None = None) -> Optional[Conversion]:
    """R5: convert a parsed quantity in a canonical unit to kg using the conversion table.

    `table` defaults to load_conversion_table(). Return None when the quantity or unit is None,
    or when the table has no factor for this (crop, unit) pair.
    """
    raise NotImplementedError("R5: implement to_kg")
