"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample of the requirements, not the full set. Assessors run a larger hidden
suite on freshly generated bulletins with different layouts, so code that only
satisfies these examples will not pass. Write your own tests in tests/test_member_*.py.
"""
import math
import os
import subprocess
import sys

import pandas as pd
import pytest

from conftest import DATA

import price_watch as pw


# ---------------------------------------------------------------- R1
@pytest.mark.parametrize("cell,expected", [
    ("1,234.50", (1234.5, "ok")), ("1234.50", (1234.5, "ok")), (" 535.70 ", (535.7, "ok")),
    ("560.85*", (560.85, "revised")), ("1,046.56p", (1046.56, "provisional")),
    (" 954.78p ", (954.78, "provisional")), ("72,000", (72000.0, "ok")),
])
def test_parse_price_values(cell, expected):
    assert pw.parse_price(cell) == expected


@pytest.mark.parametrize("cell,status", [("-", "not_collected"), (" - ", "not_collected"), ("..", "not_available")])
def test_parse_price_missing(cell, status):
    value, st = pw.parse_price(cell)
    assert math.isnan(value) and st == status


@pytest.mark.parametrize("cell", ["", "n/a", "1,23.4", "-5", "12a"])
def test_parse_price_rejects_garbage(cell):
    with pytest.raises(ValueError):
        pw.parse_price(cell)


# ---------------------------------------------------------------- R2
def test_parse_periods_forward_fills_year():
    years = ["State", "Zone", "2024", "", "", "2025", ""]
    months = ["", "", "Nov", "Dec", "Sept", "Jan", "February"]
    # A September after December is odd but legal: the year cell, not the month order, decides.
    assert pw.parse_periods(years, months) == [None, None, "2024-11", "2024-12", "2024-09", "2025-01", "2025-02"]


def test_parse_periods_rejects_unknown_month():
    with pytest.raises(ValueError):
        pw.parse_periods(["State", "2024"], ["", "Smarch"])


# ---------------------------------------------------------------- R3 / R4
@pytest.mark.parametrize("label,expected", [
    ("Kano", ("state", "Kano")), ("Kano (a)", ("state", "Kano")), ("FCT, Abuja", ("state", "FCT")),
    ("Akwa Ibom", ("state", "Akwa Ibom")), ("South South average", ("zone_average", "South South")),
    ("National average", ("national_average", "National")),
])
def test_classify_label(label, expected):
    assert pw.classify_label(label) == expected


def test_classify_label_refuses_unknown():
    with pytest.raises(ValueError):
        pw.classify_label("Kanos")


@pytest.mark.parametrize("unit,expected", [
    ("1 kg", (1.0, "kg")), ("50 kg bag", (50.0, "kg")), ("500 g", (0.5, "kg")),
    ("1 litre", (1.0, "litre")), ("crate of 30", (30.0, "piece")),
])
def test_parse_unit(unit, expected):
    assert pw.parse_unit(unit) == expected


# ---------------------------------------------------------------- R5
def test_split_tables_merges_continuations(raw):
    tables = pw.split_tables(raw)
    assert [t.number for t in tables] == [1, 2, 3, 4, 5, 6]
    for t in tables:
        assert list(t.body.columns) == ["label", "zone"] + t.periods
        # 37 states + 6 zone averages + 1 national average, whatever the page breaks
        assert len(t.body) == 44, (t.number, len(t.body))


# ---------------------------------------------------------------- R6
@pytest.fixture(scope="module")
def tidy(raw):
    return pw.tidy_bulletin(raw)


def test_tidy_shape_and_schema(tidy, raw):
    assert list(tidy.columns) == pw.TIDY_COLUMNS
    expected_rows = sum(37 * len(t.periods) for t in pw.split_tables(raw))
    assert len(tidy) == expected_rows
    assert not tidy.duplicated(["item", "state", "period"]).any()
    assert set(tidy["status"]) <= pw.STATUSES
    assert tidy["price"].dtype == "float64"
    assert list(tidy.index) == list(range(len(tidy)))


def test_tidy_keeps_missing_rows_explicit(tidy):
    missing = tidy["status"].isin(["not_collected", "not_available"])
    assert missing.sum() > 0
    assert tidy.loc[missing, "price"].isna().all()
    assert tidy.loc[~missing, "price"].notna().all()


def test_tidy_known_cells(tidy):
    row = tidy[(tidy["item"] == "Tomatoes (fresh)") & (tidy["state"] == "Benue") & (tidy["period"] == "2024-05")]
    assert len(row) == 1
    assert row["price"].iloc[0] == pytest.approx(560.85) and row["status"].iloc[0] == "revised"
    assert row["zone"].iloc[0] == "North Central"
    rice = tidy[tidy["item"] == "Rice (imported, bagged)"]
    assert (rice["unit_qty"] == 50).all()
    assert (rice["price_per_base"] - rice["price"] / 50).abs().max() < 1e-9


# ---------------------------------------------------------------- R7 / R8
def test_reconciliation_finds_how_the_national_average_is_built(raw, tidy):
    pub = pw.published_averages(raw)
    assert list(pub.columns) == pw.PUBLISHED_COLUMNS
    rec = pw.reconcile_averages(tidy, pub)
    assert list(rec.columns) == pw.RECONCILE_COLUMNS and len(rec) == len(pub)
    zones = rec[rec["area"] != "National"]
    assert (zones["match"] == "state_mean").mean() > 0.95
    assert zones["mean_of_zone_means"].isna().all()
    nat = rec[rec["area"] == "National"]
    assert (nat["match"] == "mean_of_zone_means").mean() > 0.9


# ---------------------------------------------------------------- R9
def test_month_on_month_uses_calendar_months(tidy):
    small = pd.DataFrame({
        "item": ["X"] * 4 + ["Y"], "unit": ["1 kg"] * 5, "state": ["Kano"] * 5, "zone": ["North West"] * 5,
        "period": ["2024-01", "2024-02", "2024-04", "2024-05", "2024-03"],
        "price": [100.0, 110.0, 200.0, float("nan"), 50.0], "status": ["ok", "ok", "ok", "not_collected", "ok"],
        "unit_qty": [1.0] * 5, "unit_base": ["kg"] * 5, "price_per_base": [100.0, 110.0, 200.0, float("nan"), 50.0],
    })
    out = pw.month_on_month(small)
    assert list(out.columns) == pw.TIDY_COLUMNS + ["mom_pct"]
    got = out["mom_pct"].tolist()
    assert math.isnan(got[0])                 # no previous month
    assert got[1] == pytest.approx(10.0)
    assert math.isnan(got[2])                 # March is missing for X: do NOT compare with February
    assert math.isnan(got[3])                 # current price missing
    assert math.isnan(got[4])                 # Y has no February; X's prices must not leak into Y
    assert "mom_pct" not in small.columns     # input not modified


# ---------------------------------------------------------------- R10
def test_cli_runs(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "price_watch", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=120,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    for name in ["tidy_prices.csv", "published_averages.csv", "reconciliation.csv"]:
        assert (tmp_path / name).exists(), name
