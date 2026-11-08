"""Public requirement tests. These FAIL on the starter until you implement the package.

They're a sample. The hidden suite re-runs the same checks on data regenerated with
other seeds and on unseen interval levels. Add your own tests in tests/test_member_*.py.
"""
import numpy as np
import pandas as pd
import pytest

import uncertainty_viz as uv
from figinspect import bands, dot_xs, has_source, horizontal_segments, point_positions, texts, vertical_lines_at


# ---------------------------------------------------------------- R1
def test_wilson_textbook_value():
    lo, hi = uv.wilson_interval(81, 263, 0.95)
    assert (lo, hi) == pytest.approx((0.2553, 0.3662), abs=5e-4)


def test_wilson_zero_successes_has_positive_width():
    lo, hi = uv.wilson_interval(0, 6)
    assert lo == pytest.approx(0.0, abs=1e-12) and 0.35 < hi < 0.42


def test_wilson_all_successes_and_bounds():
    lo, hi = uv.wilson_interval(5, 5)
    assert hi == pytest.approx(1.0) and 0.5 < lo < 0.6
    for k, n in [(1, 4), (2, 4), (101, 400)]:
        lo, hi = uv.wilson_interval(k, n)
        assert 0 <= lo < k / n < hi <= 1


@pytest.mark.parametrize("k,n,level", [(3, 0, 0.95), (-1, 5, 0.95), (6, 5, 0.95), (2, 5, 1.0)])
def test_wilson_rejects_bad_input(k, n, level):
    with pytest.raises(ValueError):
        uv.wilson_interval(k, n, level)


def test_wilson_narrows_with_n():
    w = [np.diff(uv.wilson_interval(n // 4, n))[0] for n in (8, 40, 400)]
    assert w[0] > w[1] > w[2]


# ---------------------------------------------------------------- R2 / R3 / R4
def test_quantile_dots_probabilities():
    s = np.arange(1, 101, dtype=float)
    np.testing.assert_allclose(uv.quantile_dots(s, 4), np.quantile(s, [0.125, 0.375, 0.625, 0.875]))
    assert len(uv.quantile_dots(s)) == 20


def test_quantile_dots_rejects_nan():
    with pytest.raises(ValueError):
        uv.quantile_dots([1.0, np.nan, 3.0], 2)


def test_stack_dots():
    x, y = uv.stack_dots([0.1, 0.4, 1.2, 0.9, 1.6], 1.0)
    np.testing.assert_allclose(x, [0.5, 0.5, 0.5, 1.5, 1.5])
    np.testing.assert_allclose(y, [0, 1, 2, 0, 1])


def test_stack_dots_origin_moves_bin_edges():
    x, _ = uv.stack_dots([9.9, 10.1], 1.0, origin=10.0)
    assert x[0] < 10.0 < x[1]


def test_prob_exceed_is_strict():
    assert uv.prob_exceed([1, 2, 3, 4], 2) == pytest.approx(0.5)


# ---------------------------------------------------------------- R5
def test_check_and_repair_quantiles(data):
    f = data["maize_price_forecast"]
    bad = uv.check_quantiles(f)
    assert bad and all(f.iloc[i]["market"] == "Bodija (Ibadan)" for i in bad)
    fixed = uv.repair_quantiles(f)
    assert uv.check_quantiles(fixed) == []
    assert uv.check_quantiles(f) == bad, "repair_quantiles must not modify its input"
    pd.testing.assert_series_equal(fixed["market"], f["market"])


# ---------------------------------------------------------------- R6
def test_interval_plot(data):
    s = data["seed_adoption_survey"]
    fig = uv.interval_plot(s, source="CLBG synthetic survey")
    ax = fig.axes[0]
    assert ax.get_xlim() == pytest.approx((0.0, 1.0))
    assert ax.get_xlabel().strip() and has_source(fig)
    segs = horizontal_segments(ax)
    for k, n in zip(s["adopted"], s["farmers_surveyed"]):
        lo, hi = uv.wilson_interval(int(k), int(n))
        assert any(np.isclose(a, lo, atol=1e-6) and np.isclose(b, hi, atol=1e-6) for a, b, _ in segs), (k, n)
    pts = point_positions(ax)
    for k, n in zip(s["adopted"], s["farmers_surveyed"]):
        assert any(np.isclose(px, k / n, atol=1e-9) for px, _ in pts)
    # rows ordered by estimate, largest at the top, with sample sizes shown
    ticks = sorted(zip(ax.get_yticks(), [t.get_text() for t in ax.get_yticklabels()]), reverse=True)
    order = (s.assign(p=s.adopted / s.farmers_surveyed).sort_values(["p", "state"], ascending=[False, True]))
    assert [t.split(" (")[0] for _, t in ticks] == list(order["state"])
    assert all("n=" in t for _, t in ticks)


# ---------------------------------------------------------------- R7
def test_quantile_dotplot_threshold_alignment(data):
    smp = data["march_price_samples"]
    s = smp.loc[smp.market == "Dawanau (Kano)", "price_ngn_per_100kg"].to_numpy(float)
    thr = 41_800.0
    fig = uv.quantile_dotplot(s, 20, threshold=thr, xlabel="March price (NGN per 100 kg)", source="CLBG synthetic")
    ax = fig.axes[0]
    xs = dot_xs(ax)
    dots = np.sort(uv.quantile_dots(s, 20))
    assert len(xs) == 20
    k = int((dots > thr).sum())
    assert (xs > thr).sum() == k, "every dot above the threshold must be drawn right of it, and only those"
    assert vertical_lines_at(ax, thr)
    assert any(f"{k} in 20" in t for t in texts(fig)), "state the exceedance as a frequency, e.g. '4 in 20'"
    assert has_source(fig) and ax.get_xlabel().strip()


# ---------------------------------------------------------------- R8
def test_fan_chart_bands_nested_and_lighter_outside(data):
    h, f = data["maize_price_history"], data["maize_price_forecast"]
    m = "Dawanau (Kano)"
    hist, fc = h[h.market == m], f[f.market == m]
    fig = uv.fan_chart(hist, fc, ylabel="NGN per 100 kg", source="CLBG synthetic")
    ax = fig.axes[0]
    bs = bands(ax)
    assert len(bs) == 3
    found = {}
    for lv in (0.5, 0.8, 0.95):
        lo_c, hi_c = uv.level_columns(lv)
        for lo, hi, lum, _ in bs:
            if np.allclose(lo, fc[lo_c].to_numpy(float)) and np.allclose(hi, fc[hi_c].to_numpy(float)):
                found[lv] = lum
    assert set(found) == {0.5, 0.8, 0.95}, "each band must span exactly its quantiles"
    assert found[0.95] > found[0.8] > found[0.5], "wider intervals must be drawn lighter"
    lines = [np.asarray(ln.get_ydata(), float) for ln in ax.get_lines()]
    assert any(np.allclose(y, hist["price_ngn_per_100kg"].to_numpy(float)) for y in lines if len(y) == len(hist))
    assert any(np.allclose(y, fc["q0.5"].to_numpy(float)) for y in lines if len(y) == len(fc))
    assert any("95%" in t for t in texts(fig)) and any("50%" in t for t in texts(fig))
    assert has_source(fig)


def test_fan_chart_refuses_crossing_quantiles(data):
    h, f = data["maize_price_history"], data["maize_price_forecast"]
    m = "Bodija (Ibadan)"
    with pytest.raises(uv.QuantileCrossingError):
        uv.fan_chart(h[h.market == m], f[f.market == m])


def test_fan_chart_missing_quantiles(data):
    h, f = data["maize_price_history"], data["maize_price_forecast"]
    m = "Dawanau (Kano)"
    with pytest.raises(ValueError):
        uv.fan_chart(h[h.market == m], f[f.market == m], levels=(0.6,))
