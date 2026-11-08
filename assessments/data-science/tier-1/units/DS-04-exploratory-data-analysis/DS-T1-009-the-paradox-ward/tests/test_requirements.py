"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample, not the full set. Assessors run a hidden suite on a dataset generated with
a different seed and a different referral hospital, so hard-coded answers will fail.
Add your own tests in tests/test_member_*.py.
"""
import json
import math
import os
import subprocess
import sys

import pandas as pd
import pytest

from conftest import DATA

import paradox_ward as pw


def _stones():
    """The classic kidney-stone treatment data (Charig et al., 1986), as individual rows.

    outcome = 1 means the treatment SUCCEEDED (not death).
    """
    cells = [("A", "small", 81, 87), ("A", "large", 192, 263), ("B", "small", 234, 270), ("B", "large", 55, 80)]
    rows = []
    for g, s, k, n in cells:
        rows += [{"treatment": g, "stone": s, "success": 1}] * k + [{"treatment": g, "stone": s, "success": 0}] * (n - k)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- R1 / R2
def test_wilson_known_values():
    lo, hi = pw.wilson_interval(81, 87)
    assert lo == pytest.approx(0.8576, abs=5e-4) and hi == pytest.approx(0.9680, abs=5e-4)
    lo, hi = pw.wilson_interval(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.2775, abs=5e-4)


def test_wilson_rejects_bad_input():
    with pytest.raises(ValueError):
        pw.wilson_interval(5, 0)
    with pytest.raises(ValueError):
        pw.wilson_interval(11, 10)


def test_rate_table_columns_and_values():
    t = pw.rate_table(_stones(), ["treatment", "stone"], outcome="success")
    assert list(t.columns) == ["treatment", "stone", "n", "events", "rate", "ci_low", "ci_high"]
    row = t[(t.treatment == "A") & (t.stone == "large")].iloc[0]
    assert (row.n, row.events) == (263, 192)
    assert row.rate == pytest.approx(192 / 263)
    assert (t.ci_low <= t.rate).all() and (t.rate <= t.ci_high).all()


# ---------------------------------------------------------------- R3-R6 on the classic example
def test_mix_rows_sum_to_one():
    m = pw.mix_table(_stones(), "treatment", "stone")
    assert m.sum(axis=1).round(12).eq(1).all()
    assert m.loc["A", "large"] == pytest.approx(263 / 350)


def test_kidney_stone_reversal_detected():
    r = pw.find_reversals(_stones(), "treatment", "stone", outcome="success")
    assert len(r) == 1
    row = r.iloc[0]
    assert (row.group_a, row.group_b) == ("A", "B")
    assert row.crude_diff == pytest.approx(273 / 350 - 289 / 350)
    assert row.n_strata_compared == 2 and row.n_strata_opposite == 2 and bool(row.reversal)


def test_min_n_excludes_small_strata():
    r = pw.find_reversals(_stones(), "treatment", "stone", outcome="success", min_n=85)
    row = r.iloc[0]
    assert row.n_strata_compared == 1 and not bool(row.reversal), "a single stratum cannot establish a reversal"


def test_standardisation_flips_ranking():
    s = pw.direct_standardise(_stones(), "treatment", "stone", outcome="success").set_index("treatment")
    assert s.loc["A", "crude_rate"] < s.loc["B", "crude_rate"]
    assert s.loc["A", "standardised_rate"] > s.loc["B", "standardised_rate"]


def test_decomposition_adds_up():
    d = pw.decompose_gap(_stones(), "A", "B", "treatment", "stone", outcome="success")
    assert d["crude_gap"] == pytest.approx(d["composition_effect"] + d["rate_effect"], abs=1e-12)
    assert d["rate_effect"] > 0 > d["composition_effect"]


# ---------------------------------------------------------------- R7 / R8 on the admissions data
def test_screen_structure(admissions):
    s = pw.screen_stratifiers(admissions, "hospital", pw.CANDIDATE_STRATIFIERS)
    assert list(s.columns) == ["candidate", "max_shift", "n_reversal_pairs"]
    assert sorted(s["candidate"]) == sorted(pw.CANDIDATE_STRATIFIERS)
    assert s["max_shift"].is_monotonic_decreasing


def test_findings_internally_consistent(admissions):
    f = pw.build_findings(admissions)
    for k in ["crude_rates", "standardised_rates", "highest_crude", "lowest_crude", "highest_standardised",
              "lowest_standardised", "primary_confounder", "stratifier_screen", "reversal_pairs", "gap_decomposition"]:
        assert k in f, k
    assert set(f["crude_rates"]) == set(admissions["hospital"])
    crude = admissions.groupby("hospital")["died_30d"].mean()
    for h, v in f["crude_rates"].items():
        assert v == pytest.approx(crude[h])
    assert f["highest_crude"] == crude.idxmax()
    g = f["gap_decomposition"]
    assert g["crude_gap"] == pytest.approx(g["composition_effect"] + g["rate_effect"], abs=1e-12)
    assert f["primary_confounder"] == f["stratifier_screen"][0]["candidate"]
    json.dumps(f)  # must be JSON-serialisable


def test_cli_writes_findings(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "paradox_ward", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=120,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    f = json.loads((tmp_path / "findings.json").read_text(encoding="utf-8"))
    assert not math.isnan(f["gap_decomposition"]["crude_gap"])
