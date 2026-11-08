"""Public requirement tests (R1-R8). They fail on the starter and pass on a correct solution."""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn import metrics as skm

import evalkit
from conftest import DATA


def _rand(seed, n=300, prev=0.1, ties=True):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < prev).astype(int)
    s = rng.normal(0, 1, n) + 1.2 * y
    if ties:
        s = np.round(s, 1)
    return y, s


def test_r1_confusion_counts():
    assert evalkit.confusion_counts([1, 1, 0, 0, 1], [1, 0, 0, 1, 1]) == (2, 1, 1, 1)


def test_r2_prf_and_zero_division():
    r = evalkit.precision_recall_f1([1, 1, 0, 0, 1], [1, 0, 0, 1, 1])
    assert r["precision"] == pytest.approx(2 / 3) and r["recall"] == pytest.approx(2 / 3)
    assert r["f1"] == pytest.approx(2 / 3) and r["specificity"] == pytest.approx(0.5) and r["accuracy"] == pytest.approx(0.6)
    z = evalkit.precision_recall_f1([0, 0, 0], [0, 0, 0])
    assert z["precision"] == 0.0 and z["recall"] == 0.0 and z["f1"] == 0.0


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_r3_auc_matches_oracle_with_ties(seed):
    y, s = _rand(seed)
    assert evalkit.roc_auc(y, s) == pytest.approx(skm.roc_auc_score(y, s), abs=1e-12)


def test_r3_auc_single_class_raises():
    with pytest.raises(ValueError):
        evalkit.roc_auc([0, 0, 0], [0.1, 0.2, 0.3])


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_r4_average_precision_matches_oracle_with_ties(seed):
    y, s = _rand(seed)
    assert evalkit.average_precision(y, s) == pytest.approx(skm.average_precision_score(y, s), abs=1e-12)


def test_r5_group_folds_are_disjoint_and_cover(scores):
    y, g = scores["y_true"].to_numpy(), scores["household_id"].to_numpy()
    folds = evalkit.stratified_group_kfold(y, g, 5, seed=0)
    assert len(folds) == 5
    seen = np.concatenate([te for _, te in folds])
    assert sorted(seen.tolist()) == list(range(len(y)))
    for tr, te in folds:
        assert not set(g[tr]) & set(g[te]), "a household straddles train and test"
        assert not set(tr) & set(te)


def test_r5_positives_spread_and_deterministic(scores):
    y, g = scores["y_true"].to_numpy(), scores["household_id"].to_numpy()
    a = evalkit.stratified_group_kfold(y, g, 5, seed=3)
    b = evalkit.stratified_group_kfold(y, g, 5, seed=3)
    assert all(np.array_equal(x[1], z[1]) for x, z in zip(a, b))
    pos = [int(y[te].sum()) for _, te in a]
    assert max(pos) - min(pos) <= 3, pos


def test_r6_threshold_is_largest_meeting_target(scores):
    y, s = scores["y_true"].to_numpy(), scores["risk_score"].to_numpy()
    for target in (0.8, 0.9, 0.95):
        t = evalkit.threshold_for_recall(y, s, target)
        rec = lambda th: ((s >= th) & (y == 1)).sum() / y.sum()
        assert rec(t) >= target
        higher = np.unique(s[s > t])
        if len(higher):
            assert rec(higher.min()) < target


def test_r7_ece_known_values():
    assert evalkit.expected_calibration_error([1, 1, 0, 0], [1.0, 1.0, 0.0, 0.0]) == pytest.approx(0.0)
    assert evalkit.expected_calibration_error([0, 0, 0, 0], [0.9, 0.9, 0.9, 0.9]) == pytest.approx(0.9)
    y, p = _rand(5, ties=False)
    p = 1 / (1 + np.exp(-p))
    bins = np.minimum((p * 10).astype(int), 9)
    exp = sum((bins == b).mean() * abs(y[bins == b].mean() - p[bins == b].mean()) for b in range(10) if (bins == b).any())
    assert evalkit.expected_calibration_error(y, p) == pytest.approx(exp)


def test_r8_run_report_keys_and_values(scores):
    r = evalkit.run_report(scores, 0.9, 5, 0)
    y, s = scores["y_true"].to_numpy(), scores["risk_score"].to_numpy()
    assert r["auc"] == pytest.approx(skm.roc_auc_score(y, s))
    assert r["average_precision"] == pytest.approx(skm.average_precision_score(y, s))
    assert r["recall_at_threshold"] >= 0.9
    assert r["accuracy_always_negative"] == pytest.approx(1 - y.mean())
    assert len(r["fold_positives"]) == 5 and sum(r["fold_positives"]) == int(y.sum())


def test_r8_cli_writes_metrics_json(tmp_path):
    root = Path(evalkit.__file__).resolve().parents[1]
    out = tmp_path / "o"
    p = subprocess.run([sys.executable, "-m", "evalkit", str(DATA), "--out", str(out)], cwd=root,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    d = json.loads((out / "metrics.json").read_text())
    assert d["n"] == 733


def test_no_sklearn_in_package():
    pkg = Path(evalkit.__file__).resolve().parent
    for f in pkg.glob("*.py"):
        assert not re.search(r"^\s*(import|from)\s+(sklearn|scipy)", f.read_text(), re.M), f.name
