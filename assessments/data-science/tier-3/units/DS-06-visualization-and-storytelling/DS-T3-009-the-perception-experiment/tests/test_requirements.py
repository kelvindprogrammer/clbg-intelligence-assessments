"""Requirement tests. They fail on the starter and pass on a correct implementation."""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import perception_lab as pl


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def test_bar_common_has_common_baseline():
    ax = pl.render_stimulus("bar_common", 70, 35).axes[0]
    assert [p.get_height() for p in ax.patches] == [70, 35]
    assert {p.get_y() for p in ax.patches} == {0.0}


def test_bar_unaligned_has_different_baselines():
    ax = pl.render_stimulus("bar_unaligned", 70, 35).axes[0]
    assert [p.get_height() for p in ax.patches] == [70, 35]
    assert len({p.get_y() for p in ax.patches}) == 2


def test_pie_angle_proportional_to_value():
    ws = pl.render_stimulus("pie_angle", 80, 20).axes[0].patches
    angles = [w.theta2 - w.theta1 for w in ws]
    assert angles[0] / angles[1] == pytest.approx(4.0)
    assert 0 < max(angles) <= 360


def test_circle_area_is_proportional_when_honest():
    cs = pl.render_stimulus("circle_area", 90, 30).axes[0].patches
    areas = [math.pi * c.get_radius() ** 2 for c in cs]
    assert areas[0] / areas[1] == pytest.approx(3.0, rel=1e-6)


@pytest.mark.parametrize("enc", pl.ENCODINGS)
def test_lie_factor_honest_is_one(enc):
    assert pl.lie_factor(enc, 60, 30) == pytest.approx(1.0, abs=1e-6)


def test_lie_factor_detects_radius_scaling():
    # radius proportional to value gives an area ratio of (30/60)^2 = 0.25 for a data ratio of 0.5
    assert pl.lie_factor("circle_area", 60, 30, honest=False) == pytest.approx(0.5, abs=1e-6)
    with pytest.raises(ValueError):
        pl.render_stimulus("hologram", 1, 2)


def test_design_is_balanced_and_truthful():
    d = pl.make_design(6, (0.3, 0.6, 0.9), 4, seed=1)
    assert list(d.columns) == ["participant", "trial", "encoding", "ratio", "a", "b", "larger_side", "true_pct"]
    assert len(d) == 6 * 4 * 3 * 4
    assert (d.groupby(["participant", "encoding", "ratio"]).size() == 4).all()
    side = d.assign(left=d["larger_side"] == "left").groupby(["participant", "encoding", "ratio"])["left"].sum()
    assert side.between(1, 3).all()
    assert np.allclose(d["true_pct"], 100 * np.minimum(d["a"], d["b"]) / np.maximum(d["a"], d["b"]))
    assert ((d["a"] > 0) & (d["b"] > 0)).all()


def test_design_is_seeded_and_randomised():
    d1, d2, d3 = (pl.make_design(5, (0.4, 0.8), 3, seed=s) for s in (1, 1, 2))
    pd.testing.assert_frame_equal(d1, d2)
    assert not d1["a"].equals(d3["a"])
    switches = []
    for _, g in d1.sort_values(["participant", "trial"]).groupby("participant"):
        e = g["encoding"].to_numpy()
        switches.append(np.mean(e[1:] != e[:-1]))
    assert np.mean(switches) > 0.5  # shuffled, not blocked by encoding


def test_log_abs_error_values():
    assert pl.log_abs_error(50, 50) == pytest.approx(-3.0)
    assert pl.log_abs_error([60, 40], [50, 50]) == pytest.approx([math.log2(10.125)] * 2)


def test_analyze_ranks_and_reports_intervals():
    res = pl.simulate_responses(pl.make_design(20, (0.3, 0.5, 0.7, 0.9), 3, seed=3), seed=4)
    a = pl.analyze(res, B=500, seed=1)
    assert list(a["encoding"]) == ["bar_common", "bar_unaligned", "pie_angle", "circle_area"]
    assert list(a["rank"]) == [1, 2, 3, 4]
    assert ((a["ci_low"] < a["mean_log_error"]) & (a["mean_log_error"] < a["ci_high"])).all()
    pd.testing.assert_frame_equal(a, pl.analyze(res, B=500, seed=1))
    assert a.set_index("encoding").loc["circle_area", "mean_signed_error"] > 3  # area ratios are overestimated (compressed)


def test_analyze_unit_of_analysis_is_the_participant():
    res = pl.simulate_responses(pl.make_design(20, (0.3, 0.5, 0.7, 0.9), 3, seed=3), seed=4)
    a = pl.analyze(res, B=2000, seed=1).set_index("encoding")
    err = res.assign(e=pl.log_abs_error(res["judged_pct"], res["true_pct"])).groupby(["participant", "encoding"])["e"].mean().unstack()
    expected_halfwidth = 1.96 * err["pie_angle"].std(ddof=1) / np.sqrt(len(err))
    got = (a.loc["pie_angle", "ci_high"] - a.loc["pie_angle", "ci_low"]) / 2
    assert got == pytest.approx(expected_halfwidth, rel=0.25)


def test_ranking_recovery_rate_rises_with_sample_size():
    big = pl.ranking_recovery_rate(24, 6, reps=30, seed=5)
    small = pl.ranking_recovery_rate(2, 1, reps=30, seed=5)
    assert big >= 0.9      # reference 1.0: at 24 participants the best-to-worst gaps are many standard errors wide
    assert small <= 0.8    # reference about 0.45: two participants cannot reliably separate pie from bar
    assert big > small
