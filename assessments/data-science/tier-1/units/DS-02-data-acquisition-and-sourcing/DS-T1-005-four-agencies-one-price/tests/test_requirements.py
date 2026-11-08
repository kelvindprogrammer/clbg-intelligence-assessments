"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample. Assessors run a hidden suite on a RE-GENERATED set of agency files, with the
defects in different markets and months, so rules tuned to these files will fail. Write your own
tests in tests/test_member_*.py.
"""
import datetime as dt
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from conftest import DATA, REF

import pricerecon as pr

KEY = ["source", "market_id", "commodity_id", "week_start"]


@pytest.fixture(scope="module")
def ref_():
    return pr.load_reference(REF)


@pytest.fixture(scope="module")
def all_df(ref_):
    return pr.load_all(DATA, ref_)


# ---------------------------------------------------------------- R1
@pytest.mark.parametrize("label,expected", [("DAWANAU/KANO", "KN-DAW"), ("  mile 12 market,   lagos ", "LA-M12"),
                                            ("Wuse (Abuja)", "FC-WUS"), ("KANDAW", "KN-DAW"), ("KN-DAW", "KN-DAW")])
def test_market_aliases(ref_, label, expected):
    assert ref_.market(label) == expected


def test_commodity_aliases_and_units(ref_):
    assert ref_.commodity("GUINEA CORN") == "sorghum"
    assert ref_.commodity("103") == "sorghum"
    assert ref_.kg("rice_local", "mudu") == pytest.approx(1.60)
    assert ref_.kg("maize_white", "100 kg bag") == 100


def test_unknown_label_raises(ref_):
    with pytest.raises(pr.UnmappedLabel):
        ref_.market("Oshodi")
    with pytest.raises(pr.UnmappedLabel):
        ref_.kg("maize_white", "paint bucket")


# ---------------------------------------------------------------- R2
@pytest.mark.parametrize("d,expected", [(dt.date(2025, 1, 11), dt.date(2025, 1, 6)), (dt.date(2025, 1, 6), dt.date(2025, 1, 6)),
                                        (dt.date(2025, 1, 12), dt.date(2025, 1, 6)), (dt.date(2025, 3, 1), dt.date(2025, 2, 24))])
def test_week_start(d, expected):
    assert pr.week_start(d) == expected


@pytest.mark.parametrize("label,expected", [("2025W02", dt.date(2025, 1, 6)), ("2026W01", dt.date(2025, 12, 29)),
                                            ("2020W53", dt.date(2020, 12, 28))])
def test_iso_week_monday(label, expected):
    assert pr.iso_week_monday(label) == expected


# ---------------------------------------------------------------- R3–R6
def _check_canonical(df):
    assert list(df.columns) == pr.CANONICAL_COLUMNS
    assert not df.duplicated(KEY).any(), "one row per source, market, commodity and week"
    assert set(df["flag"]) <= {"ok", "estimated", "missing"}
    weeks = pd.to_datetime(df["week_start"], format="%Y-%m-%d")
    assert (weeks.dt.dayofweek == 0).all(), "week_start must be a Monday (ISO date string)"
    assert df.loc[df["flag"] == "missing", "price_ngn_per_kg"].isna().all()
    assert df.loc[df["flag"] != "missing", "price_ngn_per_kg"].notna().all()


def test_parse_ngm(ref_):
    df = pr.parse_ngm(DATA / "ngm_prices.json", ref_)
    _check_canonical(df)
    assert len(df) == 650 and (df["source"] == "NGM").all()
    row = df[(df.market_id == "BO-MON") & (df.commodity_id == "beans_brown") & (df.week_start == "2025-01-06")]
    assert row["price_ngn_per_kg"].item() == pytest.approx(1645.68), "kobo must become naira"


def test_parse_cmb_revisions_and_separators(ref_):
    df = pr.parse_cmb(DATA / "cmb_bulletin.xml", ref_)
    _check_canonical(df)
    row = df[(df.market_id == "FC-WUS") & (df.commodity_id == "maize_white") & (df.week_start == "2025-02-03")]
    assert row["price_ngn_per_kg"].item() == pytest.approx(975.35 / 1.40, abs=0.01), "use the highest revision, per kg"
    row = df[(df.market_id == "FC-WUS") & (df.commodity_id == "beans_brown") & (df.week_start == "2025-02-10")]
    assert row["price_ngn_per_kg"].item() == pytest.approx(2301.18 / 1.50, abs=0.01)


def test_parse_apc_every_month_on_the_right_scale(ref_):
    apc = pr.parse_apc(DATA / "apc_survey.xlsx", ref_)
    lsa = pr.parse_lsa(DATA / "lsa_extract.txt", ref_)
    _check_canonical(apc)
    assert len(apc) == 1300 and (apc["source"] == "APC").all()
    both = apc.merge(lsa, on=["market_id", "commodity_id", "week_start"]).dropna(subset=["price_ngn_per_kg_x", "price_ngn_per_kg_y"])
    both["month"] = both["week_start"].str[:7]
    ratio = (both["price_ngn_per_kg_x"] / both["price_ngn_per_kg_y"]).groupby(both["month"]).median()
    assert len(ratio) == 6
    assert ratio.between(0.9, 1.1).all(), f"APC is off-scale in some months:\n{ratio}"


def test_parse_lsa(ref_):
    df = pr.parse_lsa(DATA / "lsa_extract.txt", ref_)
    _check_canonical(df)
    assert len(df) == 1300
    assert (df["flag"] == "missing").sum() == 27, "M records are missing, not zero"
    assert (df["flag"] == "estimated").sum() == 29
    assert df["price_ngn_per_kg"].min() > 100, "implied decimals: prices are naira per kg"


def test_lsa_trailer_is_enforced(ref_, tmp_path):
    lines = (DATA / "lsa_extract.txt").read_text(encoding="utf-8").splitlines()
    (tmp_path / "truncated.txt").write_text("\n".join(lines[:-40]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        pr.parse_lsa(tmp_path / "truncated.txt", ref_)
    stripped = [ln.rstrip() for ln in lines]
    (tmp_path / "stripped.txt").write_text("\n".join(stripped) + "\n", encoding="utf-8")
    assert len(pr.parse_lsa(tmp_path / "stripped.txt", ref_)) == 1300


# ---------------------------------------------------------------- R7–R9
def test_load_all(all_df):
    _check_canonical(all_df)
    assert all_df.groupby("source").size().to_dict() == {"APC": 1300, "CMB": 889, "LSA": 1300, "NGM": 650}


def test_reconcile_shape(all_df):
    r = pr.reconcile(all_df)
    assert list(r.columns[:3]) == ["market_id", "commodity_id", "week_start"]
    for col in ["n_sources", "median_price", "min_price", "max_price", "spread_ratio"]:
        assert col in r.columns
    assert len(r) == 10 * 5 * 26
    assert (r["spread_ratio"] >= 1).all()
    assert r["spread_ratio"].median() < 1.10, "after correct parsing, typical agencies agree within 10%"


def test_discrepancy_rule_on_a_small_case():
    df = pd.DataFrame([
        ("A", "M1", "c", "2025-01-06", 100.0, "ok"), ("B", "M1", "c", "2025-01-06", 102.0, "ok"),
        ("C", "M1", "c", "2025-01-06", 140.0, "ok"),
        ("A", "M1", "c", "2025-01-13", 100.0, "ok"), ("B", "M1", "c", "2025-01-13", 140.0, "ok"),
    ], columns=pr.CANONICAL_COLUMNS)
    d = pr.discrepancies(df)
    assert list(d["source"]) == ["C"], "only the outlier; and nothing when fewer than 3 sources"
    assert d["rel_dev"].item() == pytest.approx(140 / 102 - 1, abs=1e-3)


def test_discrepancies_are_rare_after_correct_parsing(all_df):
    d = pr.discrepancies(all_df)
    n_valid = all_df["price_ngn_per_kg"].notna().sum()
    assert 0 < len(d) <= 0.01 * n_valid
    assert (d["rel_dev"].abs() > 0.15).all()


def test_stale_runs_small_case():
    rows = [("A", "M1", "c", f"2025-01-{d:02d}", p, "ok") for d, p in [(6, 10.0), (13, 11.0), (20, 11.0), (27, 11.0)]]
    rows += [("A", "M1", "c", "2025-02-03", 11.0, "ok"), ("A", "M1", "c", "2025-02-10", 12.0, "ok")]
    df = pd.DataFrame(rows, columns=pr.CANONICAL_COLUMNS)
    s = pr.stale_runs(df, min_run=4)
    assert len(s) == 1 and s["run_length"].item() == 4
    assert s["first_week"].item() == "2025-01-13" and s["last_week"].item() == "2025-02-03"
    assert pr.stale_runs(df, min_run=5).empty


# ---------------------------------------------------------------- R10
def test_cli(tmp_path):
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(pr.__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
    r = subprocess.run([sys.executable, "-m", "pricerecon", str(DATA), "--reference", str(REF), "--out", str(tmp_path)],
                       env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    for name in ["canonical.csv", "reconciled.csv", "discrepancies.csv", "stale_runs.csv"]:
        assert (tmp_path / name).is_file(), name
    assert len(pd.read_csv(tmp_path / "canonical.csv")) == 4139
