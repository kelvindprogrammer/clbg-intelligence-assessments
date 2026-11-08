"""Public requirement tests (a sample; assessors run a larger hidden suite on re-seeded data)."""
import numpy as np
import pandas as pd
import pytest

from conftest import DATA

import agentcast as ac


@pytest.fixture(scope="module")
def df():
    return ac.load_export(DATA)


def _toy():
    return pd.DataFrame({
        "agent_id": ["X"] * 6,
        "date": ["2026-01-01", "2026-01-02", "2026-01-02", "2026-01-04", "2026-01-05", "2026-01-06"],
        "txn_count": [10, 20, 25, -1, 40, 50],
    })


def test_r1_regular_index_and_unknowns():
    s = ac.to_regular(_toy(), "X")
    assert len(s) == 6 and s.index.freqstr == "D" and s.name == "txn_count"
    assert s.loc["2026-01-02"] == 25            # last duplicate wins
    assert np.isnan(s.loc["2026-01-03"])         # missing day is unknown, not zero
    assert np.isnan(s.loc["2026-01-04"])         # sentinel -1 is unknown


def test_r1_on_real_export(df):
    s = ac.to_regular(df, "AG001")
    assert s.index.is_monotonic_increasing and s.index.is_unique and len(s) >= 190
    assert s.isna().sum() > 0 and (s.dropna() >= 0).all()


def test_r2_fill_gaps_rules():
    idx = pd.date_range("2026-01-01", periods=9)
    s = pd.Series([1, 2, np.nan, 4, 5, 9, 7, 8, np.nan], index=idx, name="txn_count", dtype=float)
    f = ac.fill_gaps(s, period=3)
    assert f.iloc[2] == 9.0   # nothing 3 earlier; original value 3 later
    assert f.iloc[8] == 9.0   # 3 earlier is observed
    assert not f.isna().any()
    assert np.isnan(s.iloc[2])  # input not mutated


def test_r2_median_fallback():
    s = pd.Series([np.nan, 4.0, 6.0], index=pd.date_range("2026-01-01", periods=3))
    assert ac.fill_gaps(s, period=7).iloc[0] == 5.0


def test_r3_seasonal_naive():
    assert list(ac.seasonal_naive(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 5, period=3)) == [8, 9, 10, 8, 9]


def test_r4_moving_average():
    assert list(ac.moving_average(np.array([1, 2, 3, 4]), 3, window=2)) == [3.5, 3.5, 3.5]


def test_r5_mae_mase():
    assert ac.mae([1, 2, 3], [2, 2, 5]) == pytest.approx(1.0)
    train = np.array([1, 3, 1, 3, 1, 3, 1, 3.0])
    assert ac.mase([2.0], [3.0], train, period=1) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        ac.mase([1.0], [2.0], np.ones(10), period=1)


def test_r6_rolling_origin():
    assert ac.rolling_origin(20, 10, 4, 3) == [(10, 14), (13, 17), (16, 20)]
    assert ac.rolling_origin(5, 10, 4, 3) == []


def test_r7_backtest_scale_uses_only_training_data():
    y = np.concatenate([np.tile([1.0, 2.0], 10), [500.0, 900.0, 500.0, 900.0]])  # a huge future shock
    score = ac.backtest(y, lambda tr, h: np.full(h, tr[-1]), h=2, initial=10, step=2, period=1)
    assert score > 50   # a scale computed on the whole series would shrink this value drastically
    with pytest.raises(ValueError):
        ac.backtest(y, ac.moving_average, h=2, initial=100, step=2)


def test_r8_choose_baseline_on_export(df):
    c = ac.choose_baseline(df)
    assert list(c) == sorted(df["agent_id"].unique())
    assert set(c.values()) <= {"seasonal_naive", "moving_average"}
    assert c["AG001"] == "seasonal_naive"   # AG001 has an obvious weekly market-day pattern
