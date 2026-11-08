"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and group labels."""
import numpy as np
import pytest

import auditkit as ak
import referralgen


@pytest.fixture(scope="module")
def data():
    return referralgen.make_audit_data(seed=5)


def test_r1_hand_example():
    y = [1, 1, 0, 0, 1, 0, 0, 0]
    p = [1, 0, 1, 0, 1, 0, 0, 0]
    g = ["a", "a", "a", "a", "b", "b", "b", "b"]
    m = ak.group_metrics(y, p, g)
    assert list(m) == ["a", "b"]
    assert m["a"] == {"n": 4, "positives": 2, "selection_rate": 0.5, "tpr": 0.5, "fpr": 0.5, "ppv": 0.5}
    assert m["b"]["tpr"] == 1.0 and m["b"]["fpr"] == 0.0 and m["b"]["ppv"] == 1.0 and m["b"]["selection_rate"] == 0.25


def test_r1_undefined_rates_are_none():
    m = ak.group_metrics([0, 0, 0], [0, 0, 0], ["z", "z", "z"])["z"]
    assert m["tpr"] is None and m["ppv"] is None and m["fpr"] == 0.0 and m["selection_rate"] == 0.0


def test_r1_matches_independent_computation(data):
    y, p, s, g = data
    m = ak.group_metrics(y, p, g)
    for z in np.unique(g):
        yy, pp = y[g == z], p[g == z]
        assert m[z]["n"] == len(yy)
        if (yy == 1).any():
            assert m[z]["tpr"] == pytest.approx(np.mean(pp[yy == 1]))
        if (pp == 1).any():
            assert m[z]["ppv"] == pytest.approx(np.mean(yy[pp == 1]))
        assert m[z]["selection_rate"] == pytest.approx(np.mean(pp))


def test_r2_disparity_reference_and_guard(data):
    y, p, s, g = data
    m = ak.group_metrics(y, p, g)
    dis = ak.disparity(m, "tpr")
    big = max(m, key=lambda z: m[z]["n"])
    assert dis[big] == {"diff": 0.0, "ratio": 1.0, "reportable": True}
    small = min(m, key=lambda z: m[z]["n"])
    assert m[small]["n"] < 30 and dis[small] == {"diff": None, "ratio": None, "reportable": False}
    other = [z for z in m if z not in (big, small)][0]
    assert dis[other]["diff"] == pytest.approx(m[other]["tpr"] - m[big]["tpr"])
    assert dis[other]["ratio"] == pytest.approx(m[other]["tpr"] / m[big]["tpr"])
    assert ak.disparity(m, "tpr", ref=other, min_n=1)[big]["diff"] == pytest.approx(m[big]["tpr"] - m[other]["tpr"])


def test_r2_zero_reference_and_ties():
    m = {"a": {"n": 50, "tpr": 0.0}, "b": {"n": 50, "tpr": 0.4}}
    d = ak.disparity(m, "tpr")  # tie on n: alphabetically first group is the reference
    assert d["a"]["diff"] == 0.0 and d["b"]["diff"] == pytest.approx(0.4) and d["b"]["ratio"] is None


def _boot(y, p, g, g1, g2, metric, n_boot, seed, alpha):
    y, p, g = map(np.asarray, (y, p, g))
    i1, i2 = np.where(g == g1)[0], np.where(g == g2)[0]
    rate = lambda idx: (np.mean(p[idx][y[idx] == 1]) if metric == "tpr" else np.mean(p[idx][y[idx] == 0]))
    rng = np.random.default_rng(seed)
    gaps = []
    for _ in range(n_boot):
        b1, b2 = i1[rng.integers(0, len(i1), len(i1))], i2[rng.integers(0, len(i2), len(i2))]
        if (y[b1] == 1).any() and (y[b2] == 1).any() and metric == "tpr":
            gaps.append(rate(b1) - rate(b2))
    return rate(i1) - rate(i2), *np.percentile(gaps, [100 * alpha / 2, 100 * (1 - alpha / 2)])


def test_r3_bootstrap_matches_specified_procedure(data):
    y, p, s, g = data
    got = ak.bootstrap_gap_ci(y, p, g, "NE", "NC", "tpr", n_boot=200, seed=4)
    want = _boot(y, p, g, "NE", "NC", "tpr", 200, 4, 0.05)
    assert got == pytest.approx(tuple(float(v) for v in want), abs=1e-12)
    assert got == ak.bootstrap_gap_ci(y, p, g, "NE", "NC", "tpr", n_boot=200, seed=4)
    assert got != ak.bootstrap_gap_ci(y, p, g, "NE", "NC", "tpr", n_boot=200, seed=5)


def test_r3_bootstrap_other_metric_and_alpha(data):
    y, p, s, g = data
    gap, lo, hi = ak.bootstrap_gap_ci(y, p, g, "NW", "NC", "fpr", n_boot=300, seed=1, alpha=0.2)
    gap2, lo2, hi2 = ak.bootstrap_gap_ci(y, p, g, "NW", "NC", "fpr", n_boot=300, seed=1, alpha=0.05)
    assert lo <= gap <= hi + 1e-12 and (hi - lo) <= (hi2 - lo2) and gap == gap2


def test_r3_skips_undefined_resamples():
    y = np.array([1, 0, 0, 0, 0, 1, 1, 0, 0, 0])
    p = np.array([1, 0, 0, 0, 0, 1, 0, 0, 1, 0])
    g = np.array(["s"] * 5 + ["t"] * 5)
    gap, lo, hi = ak.bootstrap_gap_ci(y, p, g, "s", "t", "tpr", n_boot=100, seed=0)
    assert np.isfinite([gap, lo, hi]).all() and lo <= hi


def test_r4_calibration_hand_example():
    y = [0, 1, 1, 1, 0, 0]
    s = [0.1, 0.15, 0.9, 1.0, 0.5, 0.45]
    g = ["a", "a", "a", "a", "b", "b"]
    c = ak.calibration_by_group(y, s, g, bins=5)
    assert c["a"]["n"] == 4 and [b["n"] for b in c["a"]["bins"]] == [2, 2]
    assert c["a"]["bins"][1]["lo"] == 0.8 and c["a"]["bins"][1]["observed"] == 1.0
    assert c["a"]["bins"][0]["mean_score"] == pytest.approx(0.125) and c["a"]["bins"][0]["observed"] == 0.5
    assert c["a"]["ece"] == pytest.approx(0.5 * abs(0.125 - 0.5) + 0.5 * abs(0.95 - 1.0))
    assert [b["lo"] for b in c["b"]["bins"]] == [0.4] and c["b"]["bins"][0]["n"] == 2


def test_r5_model_card_structure_and_numbers(data):
    y, p, s, g = data
    card = ak.model_card("Child referral screen", y, p, s, g, "Support community health workers.", "Synthetic data only.")
    heads = ["# Model card: Child referral screen", "## Intended use", "## Evaluation data", "## Overall performance",
             "## Group performance", "## Disparities", "## Limitations"]
    pos = [card.index(h) for h in heads]
    assert pos == sorted(pos)
    assert "Support community health workers." in card and "Synthetic data only." in card
    assert f"accuracy: {np.mean(y == p):.3f}" in card
    m = ak.group_metrics(y, p, g)
    for z, mm in m.items():
        row = [ln for ln in card.splitlines() if ln.startswith(f"| {z} |")]
        assert len(row) == 1 and f"| {mm['n']} |" in row[0]
        if mm["tpr"] is not None:
            assert f"{mm['tpr']:.3f}" in row[0]
    assert card == ak.model_card("Child referral screen", y, p, s, g, "Support community health workers.", "Synthetic data only.")


def test_r5_card_flags_small_group_and_weak_zone(data):
    y, p, s, g = data
    card = ak.model_card("x", y, p, s, g, "u", "l")
    small = min(np.unique(g), key=lambda z: int(np.sum(g == z)))
    warn = [ln for ln in card.splitlines() if ln.startswith("WARNING: ") and small in ln]
    assert len(warn) == 1 and "too small" in warn[0]
    lines = [ln for ln in card.splitlines() if ln.startswith("- ") and "distinguishable" in ln]
    assert any("not distinguishable" not in ln for ln in lines)
