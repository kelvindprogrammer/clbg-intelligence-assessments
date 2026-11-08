"""Contract tests: these pass on the unmodified starter.

They check that the data and reference tables are intact and that the public API exists.
"""
import csv
import hashlib
import inspect

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "c21b88a24fa7f8da19b0be1ce522f37c25df24b5d0966060c4cbfc5c3809e9cf"
REF = ROOT / "resources" / "reference"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, \
        "harvest_survey.csv has been modified. Restore the original file."


def test_dataset_shape_and_columns(raw):
    from yield_harmonizer.pipeline import INPUT_COLUMNS
    assert list(raw.columns) == INPUT_COLUMNS
    assert len(raw) == 2400
    assert raw["record_id"].is_unique
    assert set(raw["crop"]) == {"maize", "sorghum", "cowpea", "rice_paddy"}


def test_conversion_table_is_well_formed():
    with open(REF / "unit_conversions.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 25
    for r in rows:
        lo, mid, hi = float(r["kg_low"]), float(r["kg_per_unit"]), float(r["kg_high"])
        assert 0 < lo <= mid <= hi, r
        assert r["grade"] in {"A", "B", "C"}


def test_crop_limits_cover_every_crop():
    with open(REF / "crop_limits.csv", encoding="utf-8") as fh:
        crops = {r["crop"] for r in csv.DictReader(fh)}
    assert crops == {"maize", "sorghum", "cowpea", "rice_paddy"}


def test_public_api_signatures():
    import yield_harmonizer as yh
    for name in ["is_missing", "parse_quantity", "normalize_unit", "normalize_area_unit", "parse_area_ha",
                 "to_kg", "load_conversion_table", "mad_flags", "iqr_flags", "harmonise", "production_totals",
                 "load_survey"]:
        assert callable(getattr(yh, name)), name
    assert list(inspect.signature(yh.to_kg).parameters) == ["quantity", "unit", "crop", "table"]
    assert inspect.signature(yh.mad_flags).parameters["k"].default == 3.5
    assert inspect.signature(yh.iqr_flags).parameters["k"].default == 1.5


def test_provided_table_loader():
    import yield_harmonizer as yh
    t = yh.load_conversion_table()
    assert t[("rice_paddy", "bag_100")][0] == 75.0
    assert ("rice_paddy", "mudu") not in t
