"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, a third regime and a smaller training set."""
import numpy as np
import pytest

import datagen
import scamguard as sg


def test_r1_subgroup_report_by_hand():
    y = np.array([1, 1, 0, 0, 1, 0, 0, 1])
    p = np.array([1, 0, 0, 1, 1, 0, 0, 1])
    g = np.array(["a", "a", "a", "a", "b", "b", "b", "b"])
    r = sg.subgroup_report(y, p, g)
    assert set(r) == {"a", "b"} and r["a"]["n"] == 4
    assert r["a"]["recall"] == 0.5 and r["a"]["fpr"] == 0.5 and r["a"]["precision"] == 0.5
    assert r["b"]["recall"] == 1.0 and r["b"]["fpr"] == 0.0 and r["b"]["precision"] == 1.0


def test_r1_subgroup_report_group_without_positives():
    r = sg.subgroup_report(np.array([0, 0, 1]), np.array([1, 0, 1]), np.array(["x", "x", "y"]))
    assert np.isnan(r["x"]["recall"]) and r["x"]["fpr"] == 0.5 and r["y"]["precision"] == 1.0


def test_r2_bootstrap_ci_properties():
    x = (np.random.default_rng(0).random(200) < 0.7).astype(float)
    m, lo, hi = sg.bootstrap_ci(x, n_boot=800, seed=1)
    assert m == pytest.approx(x.mean()) and lo < m < hi and (hi - lo) < 0.2
    assert sg.bootstrap_ci(x, 800, seed=1) == (m, lo, hi)
    big = np.tile(x, 10)
    assert (sg.bootstrap_ci(big, 800, 1)[2] - sg.bootstrap_ci(big, 800, 1)[1]) < (hi - lo)
    assert sg.bootstrap_ci(np.ones(30)) == (1.0, 1.0, 1.0)
    _, lo90, hi90 = sg.bootstrap_ci(x, 800, 1, alpha=0.5)
    assert (hi90 - lo90) < (hi - lo)


def test_r3_flip_rate_by_hand():
    predict = lambda ts: np.array([len(t) > 3 for t in ts])
    texts = ["abcd", "ab", "abcde", "a"]
    assert sg.flip_rate(predict, texts, lambda ts: [t + "xxx" for t in ts]) == 0.5       # "ab" and "a" cross the length cut-off
    assert sg.flip_rate(predict, texts, lambda ts: ts) == 0.0


def test_r4_operating_threshold_by_hand():
    s = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
    y = np.array([1, 0, 1, 0, 0, 1, 0, 0, 0, 0])        # negatives: 0.8 0.6 0.5 0.3 0.2 0.1 0.05
    t = sg.operating_threshold(s, y, 2 / 7)
    assert t == pytest.approx(0.6) and np.mean(s[y == 0] >= t) == pytest.approx(2 / 7)
    assert sg.operating_threshold(s, y, 0.0) > 0.8
    tie = sg.operating_threshold(np.array([0.5, 0.5, 0.5, 0.1]), np.array([0, 0, 1, 0]), 0.4)
    assert tie > 0.5                                    # 0.5 would flag 2 of 3 negatives


@pytest.fixture(scope="module")
def world():
    Xt, yt, gt = datagen.make_sms(300, 1, "train")
    Xd, yd, gd = datagen.make_sms(600, 2, "train")
    Xs, ys, gs = datagen.make_sms(1500, 3, "shift")
    m = sg.fit_detector(Xt, yt, gt, seed=0)
    t = sg.operating_threshold(m.score(Xd), yd, 0.02)
    return m, t, Xs, ys, gs


def test_r5_interface(world):
    m, t, Xs, ys, gs = world
    s = m.score(Xs[:20])
    assert s.shape == (20,) and np.all((s >= 0) & (s <= 1))
    assert m.chosen_ in m.report_ and len(m.report_) >= 3 and any("baseline" in k for k in m.report_)


def test_r5_operating_point_survives_the_shift(world):
    m, t, Xs, ys, gs = world
    pred = m.score(Xs) >= t
    assert pred[ys == 0].mean() <= 0.06
    rep = sg.subgroup_report(ys, pred, gs)
    assert min(v["recall"] for v in rep.values()) >= 0.90


def test_r5_style_is_not_evidence(world):
    m, t, Xs, ys, gs = world
    rng = np.random.default_rng(0)
    legit = [x for x, y in zip(Xs, ys) if y == 0]
    scams = [x for x, y in zip(Xs, ys) if y == 1]
    flag = lambda ts: m.score(ts) >= t
    assert sg.flip_rate(flag, legit, lambda ts: [datagen.add_style(x, rng) for x in ts]) <= 0.03
    assert sg.flip_rate(flag, scams, lambda ts: [datagen.strip_style(x) for x in ts]) <= 0.03


def test_r5_scores_are_per_message(world):
    m, t, Xs, ys, gs = world
    a = m.score(Xs[:30])
    assert np.allclose(a[:10], m.score(Xs[:10])) and np.allclose(a[::-1], m.score(Xs[:30][::-1]))
