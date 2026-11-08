"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated hierarchies)."""
import numpy as np
import pandas as pd
import pytest

from conftest import DATA

import hierfc as hf

S_TINY = np.array([[1.0, 1], [1, 0], [0, 1]])


@pytest.fixture(scope="module")
def df():
    return hf.load_export(DATA)


def test_r1_hierarchy_structure(df):
    H = hf.build_hierarchy(df)
    assert H.names[0] == "TOTAL" and len(H.names) == 16 and H.S.shape == (16, 12) and H.Y.shape == (260, 16)
    assert (H.S[0] == 1).all() and (H.S[4:] == np.eye(12)).all() and H.S[1:4].sum() == 12
    assert np.allclose(H.Y, H.Y[:, 4:] @ H.S.T)
    assert H.names[1:4] == sorted(H.names[1:4])


def test_r2_bottom_up():
    out = hf.reconcile(np.array([[10.0, 4, 5]]), S_TINY, "bottom_up")
    assert np.allclose(out, [[9, 4, 5]])


def test_r2_ols_matches_closed_form():
    b = np.array([[10.0, 4, 5], [3, 1, 1]])
    P = np.linalg.inv(S_TINY.T @ S_TINY) @ S_TINY.T
    assert np.allclose(hf.reconcile(b, S_TINY, "ols"), (S_TINY @ P @ b.T).T)


def test_r2_wls_structural_weights():
    b = np.array([[10.0, 4, 5]])
    Wi = np.diag(1 / S_TINY.sum(axis=1))
    P = np.linalg.solve(S_TINY.T @ Wi @ S_TINY, S_TINY.T @ Wi)
    assert np.allclose(hf.reconcile(b, S_TINY, "wls_struct"), (S_TINY @ P @ b.T).T)


def test_r2_top_down_uses_average_proportions_and_window():
    Y = np.array([[10.0, 6, 4], [10, 5, 5], [20, 4, 16]])   # shares of bottom 1: 0.6, 0.5, 0.2
    b = np.array([[100.0, 0, 0]])
    full = hf.reconcile(b, S_TINY, "top_down", Y=Y)
    assert np.allclose(full[0], [100, 100 * np.mean([.6, .5, .2]), 100 * np.mean([.4, .5, .8])])
    last2 = hf.reconcile(b, S_TINY, "top_down", Y=Y, prop_window=2)
    assert np.allclose(last2[0, 1], 100 * np.mean([.5, .2]))


@pytest.mark.parametrize("method", ["ols", "wls_struct", "mint_shrink"])
def test_r2_coherent_input_is_unchanged_and_output_is_coherent(df, method):
    H = hf.build_hierarchy(df)
    rng = np.random.RandomState(0)
    bottom = rng.rand(5, 12) * 50 + 10
    coherent = bottom @ H.S.T
    resid = rng.randn(120, 16) * 3
    assert np.allclose(hf.reconcile(coherent, H.S, method, resid=resid), coherent)
    noisy = coherent + rng.randn(5, 16)
    out = hf.reconcile(noisy, H.S, method, resid=resid)
    assert np.allclose(out, out[:, 4:] @ H.S.T)


def test_r2_mint_shrink_differs_from_ols_when_variances_differ(df):
    H = hf.build_hierarchy(df)
    rng = np.random.RandomState(1)
    resid = rng.randn(150, 16) * np.linspace(1, 20, 16)
    b = rng.rand(3, 16) * 100
    assert not np.allclose(hf.reconcile(b, H.S, "mint_shrink", resid=resid), hf.reconcile(b, H.S, "ols"))
    with pytest.raises(ValueError):
        hf.reconcile(b, H.S, "magic")


def test_r3_evaluation_table(df):
    r = hf.run_evaluation(df)
    assert list(r.columns) == ["method", "level", "rmsse"] and len(r) == 6 * 4
    assert set(r["method"]) == {"base", *hf.METHODS} and set(r["level"]) == {"total", "zone", "clinic", "all"}
    assert r["rmsse"].between(0.3, 3).all()
    base_total = r[(r.method == "base") & (r.level == "total")].rmsse.item()
    bu_total = r[(r.method == "bottom_up") & (r.level == "total")].rmsse.item()
    assert base_total != bu_total


def test_r3_uses_only_the_past(df):
    h, initial, step = 8, 156, 13
    cut = initial + step * 2 + h                 # last origin ends exactly at `cut`
    a = hf.run_evaluation(df[df["week"] <= sorted(df["week"].unique())[cut - 1]], h, initial, step)
    d2 = df.copy()
    d2.loc[d2["week"] > sorted(df["week"].unique())[cut - 1], "visits"] = 99999
    b = hf.run_evaluation(d2[d2["week"] <= sorted(df["week"].unique())[cut - 1]], h, initial, step)
    assert np.allclose(a["rmsse"], b["rmsse"])


def _planted(seed=0):
    rng = np.random.RandomState(seed)
    weeks = pd.date_range("2021-01-04", periods=150, freq="W-MON").strftime("%Y-%m-%d")
    rows = []
    for cid, level, new in [("Z-01", 100, 40), ("Z-02", 100, 160), ("Z-03", 100, 100), ("Z-04", 100, 100)]:
        mu = np.where(np.arange(150) < 90, level, new)
        for w, y in zip(weeks, rng.poisson(mu)):
            rows.append({"zone": "Z", "clinic_id": cid, "week": w, "visits": int(y)})
    return pd.DataFrame(rows)


def test_r4_detects_a_planted_shift_and_not_noise():
    out = hf.detect_transfers(_planted())
    ids = {d["clinic_id"]: d for d in out}
    assert "Z-01" in ids and ids["Z-01"]["direction"] == "down" and abs(ids["Z-01"]["week_index"] - 90) <= 6
    assert "Z-03" not in ids and "Z-04" not in ids


def test_r4_output_format_on_the_export(df):
    out = hf.detect_transfers(df)
    assert isinstance(out, list) and len(out) <= 3
    for d in out:
        assert set(d) == {"clinic_id", "week_index", "direction"} and d["direction"] in {"up", "down"}
