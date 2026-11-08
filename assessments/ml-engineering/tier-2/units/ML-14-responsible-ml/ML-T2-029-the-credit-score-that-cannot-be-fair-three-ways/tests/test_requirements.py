"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and criteria."""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import fairlend as fl
import lendgen


def split(seed):
    X, y, g, _ = lendgen.make_lending(seed=seed)
    return [(X[a:b], y[a:b], g[a:b]) for a, b in ((0, 3000), (3000, 4500), (4500, 6000))]


def test_r1_hand_example():
    y = np.array([1, 1, 0, 0, 1, 1, 0, 0])
    p = np.array([1, 0, 1, 0, 1, 1, 1, 0])
    g = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    r = fl.fairness_report(y, p, g)
    assert r["rates"][0]["tpr"] == 0.5 and r["rates"][1]["tpr"] == 1.0 and r["rates"][1]["fpr"] == 0.5
    assert r["equal_opportunity_diff"] == 0.5 and r["fpr_diff"] == 0.0 and r["equalized_odds_gap"] == 0.5
    assert r["demographic_parity_diff"] == 0.75 - 0.5
    assert r["predictive_parity_diff"] == pytest.approx(2 / 3 - 0.5)


def test_r2_reweighing_makes_group_and_label_independent():
    X, y, g, _ = lendgen.make_lending(seed=2)
    w_ = fl.reweighing_weights(y, g)
    assert w_.sum() == pytest.approx(len(y)) and (w_ > 0).all()
    for gv in (0, 1):
        for yv in (0, 1):
            m = (g == gv) & (y == yv)
            assert w_[m].sum() / len(y) == pytest.approx(np.mean(g == gv) * np.mean(y == yv), rel=1e-9)
    assert fl.reweighing_weights([1, 0, 1, 0], [0, 0, 1, 1]).tolist() == [1.0, 1.0, 1.0, 1.0]


def _brute(score, y, g, crit, tol, gain, loss, grid):
    cs = [np.unique(np.quantile(score[g == k], np.linspace(0, 1, grid))) for k in (0, 1)]
    best = None
    for t0 in cs[0]:
        for t1 in cs[1]:
            p = np.where(g == 1, score >= t1, score >= t0)
            rate = lambda k, a: np.mean(p[(g == k) & (y == a)]) if a is not None else np.mean(p[g == k])
            gap = abs(rate(1, 1) - rate(0, 1)) if crit == "equal_opportunity" else abs(rate(1, None) - rate(0, None))
            if gap <= tol:
                pr = gain * np.sum(p & (y == 1)) - loss * np.sum(p & (y == 0))
                if best is None or pr > best[0]:
                    best = (pr, t0, t1)
    return best


def test_r3_thresholds_match_exhaustive_search():
    (X, y, g), s = split(4)[1], None
    s = LogisticRegression(max_iter=500).fit(StandardScaler().fit_transform(X), y)
    sc = s.predict_proba(StandardScaler().fit(X).transform(X))[:, 1]
    for crit in ("equal_opportunity", "demographic_parity"):
        t0, t1, info = fl.group_thresholds(sc, y, g, crit, 0.03, grid=21)
        pr, b0, b1 = _brute(sc, y, g, crit, 0.03, 1.0, 4.0, 21)
        assert (t0, t1) == (b0, b1) and info["profit"] == pytest.approx(pr) and info["gap"] <= 0.03 + 1e-12


def test_r3_infeasible_raises():
    sc = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    with pytest.raises(ValueError):
        fl.group_thresholds(sc, np.array([1, 0, 1, 1, 1, 1]), np.array([0, 0, 0, 1, 1, 1]), "equal_opportunity", -0.1, grid=5)


def test_r4_tradeoff_curve_is_monotone():
    (X, y, g), sc = split(5)[1], None
    sc = LogisticRegression(max_iter=500).fit(StandardScaler().fit_transform(X), y).predict_proba(StandardScaler().fit(X).transform(X))[:, 1]
    rows = fl.tradeoff_curve(sc, y, g, "equal_opportunity", [0.2, 0.1, 0.05, 0.02], grid=21)
    assert [r["tol"] for r in rows] == sorted((r["tol"] for r in rows), reverse=True)
    assert all(r["gap"] <= r["tol"] + 1e-12 for r in rows)
    pr = [r["profit"] for r in rows]
    assert all(a >= b - 1e-9 for a, b in zip(pr, pr[1:]))


def test_r5_interface_and_reports():
    (a, b, c) = split(1)
    m = fl.select_and_mitigate(*a, *b)
    assert isinstance(m.chosen_, str) and set(m.report_) >= {"baseline", "mitigated"} and len(m.thresholds_) == 2
    pr = m.predict(c[0], c[2])
    assert set(np.unique(pr)) <= {0, 1} and pr.shape == c[1].shape
    for k in ("baseline", "mitigated"):
        assert "profit" in m.report_[k] and "equal_opportunity_diff" in m.report_[k]
    assert abs(m.report_["mitigated"]["equal_opportunity_diff"]) <= 0.03 + 1e-9


def test_r5_acceptance_on_held_out_test():
    (a, b, c) = split(1)
    m = fl.select_and_mitigate(*a, *b)
    sc = StandardScaler().fit(a[0])
    clf = LogisticRegression(max_iter=500).fit(sc.transform(a[0]), a[1])
    sv = clf.predict_proba(sc.transform(b[0]))[:, 1]
    pf = lambda p, y: np.sum((y == 1) & (p == 1)) - 4 * np.sum((y == 0) & (p == 1))
    tb = max(np.unique(np.quantile(sv, np.linspace(0, 1, 101))), key=lambda t: pf((sv >= t).astype(int), b[1]))
    base = (clf.predict_proba(sc.transform(c[0]))[:, 1] >= tb).astype(int)
    rb = fl.fairness_report(c[1], base, c[2])
    rm = fl.fairness_report(c[1], m.predict(c[0], c[2]), c[2])
    assert abs(rb["equal_opportunity_diff"]) >= 0.12
    assert abs(rm["equal_opportunity_diff"]) <= 0.10
    assert pf(m.predict(c[0], c[2]), c[1]) >= 0.85 * pf(base, c[1])
