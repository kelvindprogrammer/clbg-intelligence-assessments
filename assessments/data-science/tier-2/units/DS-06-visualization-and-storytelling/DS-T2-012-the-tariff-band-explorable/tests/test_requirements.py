"""Public requirement tests. These FAIL on the starter until you build the submission.

They check the parts of an open-ended project that can be checked mechanically: the model's
behaviour, the provenance of the tariffs, the view specs, the usability data's privacy and
analysis, and the explorable's portability. The explorable's quality is judged by people.
"""
import itertools
import json
import re

import numpy as np
import pandas as pd
import pytest
from jsonschema import Draft202012Validator

from conftest import SCHEMA

from model import tariff_model as tm
from usability import analysis

BANDS = ["A", "B", "C", "D", "E"]
SESSION_COLS = ["participant_code", "session_date", "device", "task_id", "completed", "time_s", "errors",
                "comprehension_pre", "comprehension_post", "consent_recorded"]


@pytest.fixture(scope="module")
def tariffs(sub):
    return tm.load_tariffs(sub / "data" / "tariffs.csv")


def scen(tariffs, backup=450.0, share=1.0):
    return {"tariffs": tariffs, "backup_ngn_per_kwh": backup, "backup_share": share}


# ---------------------------------------------------------------- R1 tariffs and provenance
def test_tariff_table_has_provenance(sub, tariffs):
    df = pd.read_csv(sub / "data" / "tariffs.csv")
    assert sorted(df["band"].str.upper()) == BANDS
    assert {"band", "ngn_per_kwh", "source_url", "accessed"} <= set(df.columns)
    assert df["source_url"].str.match(r"^https?://").all()
    assert df["accessed"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$").all()
    assert all(v >= 0 for v in tariffs.values())


# ---------------------------------------------------------------- R2 model behaviour
def test_return_keys_and_zero_demand(tariffs):
    out = tm.monthly_cost({"demand_kwh": 0, "band": "A", "supply_hours": 20}, scen(tariffs))
    assert tuple(out) == tm.RETURN_KEYS or set(out) == set(tm.RETURN_KEYS)
    assert out["total_cost_ngn"] == pytest.approx(0.0)


def test_cost_rises_with_demand(tariffs):
    for band in BANDS:
        costs = [tm.monthly_cost({"demand_kwh": d, "band": band, "supply_hours": 14}, scen(tariffs))["total_cost_ngn"]
                 for d in (50, 100, 200, 400)]
        assert all(a <= b + 1e-9 for a, b in zip(costs, costs[1:])), band


def test_more_supply_is_cheaper_when_backup_is_dearer(tariffs):
    for band in BANDS:
        assert tariffs[band] < 450
        costs = [tm.monthly_cost({"demand_kwh": 250, "band": band, "supply_hours": h}, scen(tariffs, 450, 1.0))["total_cost_ngn"]
                 for h in (4, 8, 12, 16, 20, 24)]
        assert all(a >= b - 1e-9 for a, b in zip(costs, costs[1:])), band


def test_energy_balance(tariffs):
    for band, h, share in itertools.product(BANDS, (0, 6, 24), (0.0, 0.5, 1.0)):
        o = tm.monthly_cost({"demand_kwh": 300, "band": band, "supply_hours": h}, scen(tariffs, 400, share))
        assert o["grid_kwh"] + o["backup_kwh"] + o["unserved_kwh"] == pytest.approx(300)
        assert o["total_cost_ngn"] == pytest.approx(o["grid_cost_ngn"] + o["backup_cost_ngn"])


@pytest.mark.parametrize("household", [
    {"demand_kwh": 100, "band": "Z", "supply_hours": 10},
    {"demand_kwh": 100, "band": "A", "supply_hours": 25},
    {"demand_kwh": -5, "band": "A", "supply_hours": 10},
])
def test_invalid_inputs(tariffs, household):
    with pytest.raises(ValueError):
        tm.monthly_cost(household, scen(tariffs))


# ---------------------------------------------------------------- R3 view specs
def test_view_specs_validate(sub):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    files = sorted((sub / "specs").glob("*.json"))
    assert len(files) >= 3, "at least three views, each with a spec"
    ids = set()
    for f in files:
        spec = json.loads(f.read_text(encoding="utf-8"))
        errs = sorted(e.message for e in v.iter_errors(spec))
        assert not errs, f"{f.name}: {errs[:3]}"
        ids.add(spec["id"])
    assert len(ids) == len(files)


# ---------------------------------------------------------------- R4 explorable portability
def test_explorable_is_portable(sub):
    html_path = sub / "explorable" / "index.html"
    html = html_path.read_text(encoding="utf-8")
    assert html_path.stat().st_size < 2_000_000
    assert re.search(r"<title>[^<]{4,}</title>", html)
    assert 'name="viewport"' in html, "must work on a phone"
    for src in re.findall(r'<script[^>]+src="([^"]+)"', html):
        if src.startswith("http"):
            assert re.search(r"@\d+\.\d+\.\d+", src), f"pin external scripts to an exact version: {src}"


# ---------------------------------------------------------------- R5/R6 usability data and analysis
def test_usability_data_is_pseudonymous_and_consented(sub):
    s = pd.read_csv(sub / "usability" / "sessions.csv")
    assert list(s.columns) == SESSION_COLS, "only the documented columns are allowed"
    assert s["participant_code"].astype(str).str.fullmatch(r"P\d+").all()
    assert 3 <= s["participant_code"].nunique() <= 8
    assert s["consent_recorded"].astype(str).str.lower().eq("true").all()
    assert s["comprehension_pre"].between(0, 5).all() and s["comprehension_post"].between(0, 5).all()
    sus = pd.read_csv(sub / "usability" / "sus.csv")
    assert list(sus.columns) == ["participant_code"] + [f"q{i}" for i in range(1, 11)]
    assert set(sus["participant_code"]) == set(s["participant_code"])


def test_sus_score():
    assert analysis.sus_score([3] * 10) == pytest.approx(50.0)
    assert analysis.sus_score([5, 1] * 5) == pytest.approx(100.0)
    assert analysis.sus_score([1, 5] * 5) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        analysis.sus_score([3] * 9)
    with pytest.raises(ValueError):
        analysis.sus_score([3] * 9 + [6])


def test_summarise_sessions():
    s = pd.DataFrame({"participant_code": ["P1", "P1", "P2", "P2"], "completed": ["true", "false", "true", "true"],
                      "time_s": [10, 30, 20, 40], "comprehension_pre": [1, 1, 2, 2], "comprehension_post": [3, 3, 5, 5]})
    out = analysis.summarise_sessions(s)
    assert out["n_participants"] == 2 and out["completion_rate"] == pytest.approx(0.75)
    assert out["median_time_s"] == pytest.approx(25.0) and out["mean_comprehension_gain"] == pytest.approx(2.5)
    assert np.isfinite(list(out.values())).all()
