"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample of the rules, not the full set. Assessors run a larger hidden suite,
including on a re-generated survey in which a different enumerator and different records
carry the defects, so code that only satisfies these examples will not pass.
Write your own tests in tests/test_member_*.py.
"""
import math
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from conftest import DATA

import yield_harmonizer as yh


# ---------------------------------------------------------------- R1
@pytest.mark.parametrize("token", ["", "  ", "NA", "n/a", "-", "nil", "NULL"])
def test_missing_tokens(token):
    assert yh.is_missing(token)


@pytest.mark.parametrize("value", ["0", "0.0", "kg", "none of it"])
def test_not_missing(value):
    assert not yh.is_missing(value)


# ---------------------------------------------------------------- R2
@pytest.mark.parametrize("raw,expected", [
    ("12", 12.0), (" 3.5 ", 3.5), ("1,200", 1200.0), ("12,345.5", 12345.5), ("2 1/2", 2.5), ("2½", 2.5),
    ("1/2", 0.5), ("0", 0.0), ("-4", None), ("3,5", None), ("about 10", None), ("N/A", None),
])
def test_parse_quantity(raw, expected):
    assert yh.parse_quantity(raw) == expected


# ---------------------------------------------------------------- R3
@pytest.mark.parametrize("raw,expected", [
    ("kg", "kg"), ("Kilograms", "kg"), ("kg.", "kg"), ("MT", "tonne"), ("t", "tonne"),
    ("bag", "bag_100"), ("100 kg bag", "bag_100"), ("bag (100kg)", "bag_100"),
    ("half bag", "bag_50"), ("50kg bags", "bag_50"), ("kwano", "basin"), ("modu", "mudu"),
    ("Paint Bucket", "paint_bucket"), ("cart", None), ("heap", None), ("", None),
])
def test_normalize_unit(raw, expected):
    assert yh.normalize_unit(raw) == expected


# ---------------------------------------------------------------- R4
def test_area_units():
    assert yh.normalize_area_unit("Hectares") == "ha"
    assert yh.normalize_area_unit("ac") == "acre"
    assert yh.normalize_area_unit("sq m") == "m2"
    assert yh.normalize_area_unit("plots") is None
    assert yh.parse_area_ha("2", "acres") == pytest.approx(0.80937, rel=1e-4)
    assert yh.parse_area_ha("4,500", "square metres") == pytest.approx(0.45)
    assert yh.parse_area_ha("0", "ha") is None
    assert yh.parse_area_ha("NA", "ha") is None


# ---------------------------------------------------------------- R5
def test_to_kg_uses_crop_specific_factor():
    maize = yh.to_kg(10.0, "bag_100", "maize")
    paddy = yh.to_kg(10.0, "bag_100", "rice_paddy")
    assert maize.kg == pytest.approx(1000.0) and maize.grade == "B"
    assert paddy.kg == pytest.approx(750.0)
    assert (maize.kg_low, maize.kg_high) == (pytest.approx(920.0), pytest.approx(1040.0))


def test_to_kg_refuses_missing_factor():
    assert yh.to_kg(5.0, "mudu", "rice_paddy") is None
    assert yh.to_kg(None, "kg", "maize") is None
    assert yh.to_kg(5.0, None, "maize") is None


# ---------------------------------------------------------------- R6
def test_mad_flags_definition():
    v = pd.Series([100, 110, 120, 130, 140, 150, 160, 5000, 0, np.nan], index=list("abcdefghij"))
    f = yh.mad_flags(v)
    assert list(f.index) == list(v.index)
    assert f.dtype == bool
    assert f["h"] and not f[["a", "b", "c", "d", "e", "f", "g", "i", "j"]].any()


def test_mad_flags_low_side_and_k():
    v = pd.Series([1000.0, 1100, 1200, 1300, 1400, 1500, 1600, 12])
    assert yh.mad_flags(v).iloc[-1]
    assert not yh.mad_flags(v, k=1000).any()


def test_iqr_flags_definition():
    v = pd.Series([10.0, 11, 12, 13, 14, 15, 16, 400])
    f = yh.iqr_flags(v)
    x = np.log(v)
    q1, q3 = np.percentile(x, [25, 75])
    expected = (x < q1 - 1.5 * (q3 - q1)) | (x > q3 + 1.5 * (q3 - q1))
    assert f.tolist() == expected.tolist()


# ---------------------------------------------------------------- R7-R9 (end-to-end)
@pytest.fixture(scope="module")
def result(raw):
    return yh.harmonise(raw)


def _num(s):
    return pd.to_numeric(s.astype(str).replace("", np.nan), errors="coerce")


def test_one_row_per_record(result, raw):
    from yield_harmonizer.pipeline import ISSUE_COLUMNS, RECORD_COLUMNS
    assert list(result.records.columns) == RECORD_COLUMNS
    assert list(result.issues.columns) == ISSUE_COLUMNS
    assert sorted(result.records["record_id"]) == sorted(raw["record_id"]), "no record may be dropped"


def test_yield_is_kg_over_area(result):
    r = result.records
    kg, area, y = _num(r["kg"]), _num(r["area_ha"]), _num(r["yield_kg_ha"])
    both = kg.notna() & area.notna()
    assert np.allclose(y[both], kg[both] / area[both], rtol=1e-3, atol=0.1)
    assert y[~both].isna().all()


def test_unknown_units_are_not_converted(result, raw):
    m = raw["harvest_unit"].str.strip().str.lower().isin(["cart", "heap", "pickup", "wheelbarrow", "jerrycan"])
    rec = result.records.set_index("record_id").loc[raw.loc[m, "record_id"]]
    assert m.sum() > 0
    assert (rec["kg"].astype(str) == "").all()
    assert rec["flags"].str.contains("unknown_unit").all()


def test_zero_harvests_are_kept_and_usable(result, raw):
    m = raw["harvest_qty"].str.strip() == "0"
    rec = result.records.set_index("record_id").loc[raw.loc[m, "record_id"]]
    assert m.sum() > 0
    assert rec["flags"].str.contains("zero_harvest").all()
    assert (rec.loc[rec["area_ha"].astype(str) != "", "usable"].astype(str) == "True").all()


def test_flags_vocabulary_and_usable_rule(result):
    vocab = {"missing_quantity", "invalid_quantity", "unknown_unit", "no_conversion_factor", "missing_area",
             "invalid_area", "domain_high", "robust_outlier", "zero_harvest"}
    r = result.records
    sets = r["flags"].astype(str).map(lambda s: set(filter(None, s.split(";"))))
    assert set().union(*sets) <= vocab
    expected_usable = sets.map(lambda s: s <= {"zero_harvest"}) & (r["kg"].astype(str) != "") & (r["area_ha"].astype(str) != "")
    assert (r["usable"].astype(str) == expected_usable.map(str)).all()


def test_domain_ceiling_is_applied(result):
    from yield_harmonizer.pipeline import load_crop_limits
    lim = load_crop_limits()
    r = result.records
    y = _num(r["yield_kg_ha"])
    over = y > r["crop"].map(lim)
    assert over.sum() > 0
    assert r.loc[over, "flags"].str.contains("domain_high").all()
    assert not r.loc[~over, "flags"].astype(str).str.contains("domain_high").any()


def test_totals_structure_and_ordering(result):
    from yield_harmonizer.pipeline import TOTALS_COLUMNS
    t = yh.production_totals(result.records)
    assert list(t.columns) == TOTALS_COLUMNS
    assert set(t["crop"]) == {"maize", "sorghum", "cowpea", "rice_paddy", "ALL"}
    assert set(t["scenario"]) == {"unit_blind", "all_converted", "usable_only", "imputed"}
    for _, g in t.groupby("crop"):
        s = g.set_index("scenario")
        assert s.loc["usable_only", "total_kg"] <= s.loc["imputed", "total_kg"]
        for sc in ["all_converted", "usable_only", "imputed"]:
            assert s.loc[sc, "total_kg_low"] <= s.loc[sc, "total_kg"] <= s.loc[sc, "total_kg_high"]
    by = t[t["crop"] != "ALL"].groupby("scenario")["total_kg"].sum()
    al = t[t["crop"] == "ALL"].set_index("scenario")["total_kg"]
    assert np.allclose(by.sort_index(), al.sort_index(), rtol=1e-6)


def test_flagged_records_dominate_naive_total(result):
    """The headline finding: a handful of flagged records inflate the naive total enormously."""
    t = yh.production_totals(result.records).set_index(["crop", "scenario"])["total_kg"]
    assert t[("ALL", "all_converted")] > 3 * t[("ALL", "usable_only")]


def test_cli_runs(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "yield_harmonizer", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=120,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    for name in ["harmonised.csv", "issues.csv", "totals.csv"]:
        assert (tmp_path / name).exists(), name
