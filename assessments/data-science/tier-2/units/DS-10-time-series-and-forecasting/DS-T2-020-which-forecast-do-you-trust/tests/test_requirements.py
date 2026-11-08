"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated feeders)."""
import numpy as np
import pandas as pd
import pytest

from conftest import DATA

import fcbench as fb


@pytest.fixture(scope="module")
def df():
    return fb.load_export(DATA)


def _toy(n=60):
    return pd.Series(np.tile([10.0, 11, 12, 13, 14, 8, 7], n // 7 + 1)[:n] + np.arange(n) * 0.01,
                     index=pd.date_range("2025-01-01", periods=n, freq="D"))


def test_r1_flags_obvious_outage_only():
    s = _toy(60).copy()
    s.iloc[30] = 0.4
    f = fb.flag_outages(s)
    assert f.dtype == bool and f.index.equals(s.index)
    assert f.iloc[30] and f.sum() == 1


def test_r1_on_export_flags_a_small_share(df):
    share = np.mean([fb.flag_outages(fb.series_of(df, i)).mean() for i in sorted(df["feeder_id"].unique())])
    assert 0.003 < share < 0.04


def test_r2_seasonal_naive_mean_and_interval():
    s = _toy(70)
    fc = fb.seasonal_naive_forecast(s, 9, level=0.8)
    y = s.to_numpy()
    assert np.allclose(fc.mean, [y[-7 + (i % 7)] for i in range(9)])
    d = y[7:] - y[:-7]
    lo, hi = np.quantile(d, [0.1, 0.9])
    assert np.allclose(fc.lower, fc.mean + lo) and np.allclose(fc.upper, fc.mean + hi)


def test_r3_my_forecaster_contract(df):
    s = fb.series_of(df, "FDR03").iloc[:450]
    fc = fb.my_forecaster(s, 14, 0.8)
    for a in (fc.mean, fc.lower, fc.upper):
        assert np.asarray(a).shape == (14,) and np.isfinite(a).all()
    assert (np.asarray(fc.lower) <= np.asarray(fc.upper)).all()


def test_r4_interval_score():
    assert fb.interval_score([5.0], [4.0], [6.0], 0.8) == pytest.approx(2.0)
    assert fb.interval_score([7.0], [4.0], [6.0], 0.8) == pytest.approx(2.0 + 10 * 1.0)
    assert fb.interval_score([3.0, 5.0], [4.0, 4.0], [6.0, 6.0], 0.9) == pytest.approx((2 + 20 + 2) / 2)


def test_r5_backtest_origins_and_no_peeking(df):
    y = fb.series_of(df, "FDR02")
    seen = []

    def spy(train, h, level):
        seen.append(len(train))
        return fb.seasonal_naive_forecast(train, h, level)

    res = fb.backtest_forecasts(y, spy, h=14, initial=400, step=28)
    assert [r["origin"] for r in res] == list(range(400, 700 - 14 + 1, 28)) and seen == [r["origin"] for r in res]
    assert np.allclose(res[0]["actual"], y.iloc[400:414].to_numpy())


def test_r5_rejects_bad_forecasts(df):
    y = fb.series_of(df, "FDR02")
    bad = lambda tr, h, lv: fb.Forecast(np.zeros(h), np.ones(h), np.zeros(h))  # lower > upper
    with pytest.raises(ValueError):
        fb.backtest_forecasts(y, bad, 14, 600, 28)


def test_r6_run_benchmark_shape_and_causality(df):
    fcs = {"snaive": fb.seasonal_naive_forecast}
    r = fb.run_benchmark(df, fcs)
    assert list(r.columns) == ["feeder_id", "method", "mase", "coverage", "interval_score"] and len(r) == 8
    assert r["feeder_id"].is_monotonic_increasing and r["mase"].between(0.2, 3).all()
    df2 = df.copy()
    df2.loc[(df2["feeder_id"] == "FDR01") & (df2["date"] > "2025-11-24"), "peak_mw"] = 999.0   # after the last test window
    r2 = fb.run_benchmark(df2, fcs)
    assert r2.loc[0, "mase"] == pytest.approx(r.loc[0, "mase"])


def test_ac_your_method_beats_the_baseline_on_the_export(df):
    r = fb.run_benchmark(df, {"snaive": fb.seasonal_naive_forecast, "mine": fb.my_forecaster})
    p = r.pivot(index="feeder_id", columns="method")
    assert (p["mase"]["mine"] / p["mase"]["snaive"]).median() <= 0.90
    assert 0.70 <= p["coverage"]["mine"].mean() <= 0.90
