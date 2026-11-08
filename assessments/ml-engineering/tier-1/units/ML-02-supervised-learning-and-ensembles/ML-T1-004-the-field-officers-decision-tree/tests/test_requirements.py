"""Public requirement tests (FAIL on the starter). Hidden tests re-seed and test more edge cases."""
import re
import time

import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier

import datagen
import treeforge as tf


def test_r1_gini_values():
    assert tf.gini(np.array([0, 0, 0])) == 0.0 and tf.gini(np.array([], dtype=int)) == 0.0
    assert tf.gini(np.array([0, 1])) == pytest.approx(0.5)
    assert tf.gini(np.array([0, 0, 1, 2])) == pytest.approx(1 - (0.25 + 1 / 16 + 1 / 16))


def test_r2_hand_checked_split():
    X = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
    y = np.array([0, 0, 1, 1, 1])
    j, thr, gain = tf.best_split(X, y)
    assert (j, thr) == (0, 2.5) and gain == pytest.approx(0.48)       # parent 0.48, children pure


def test_r2_min_leaf_ties_and_constants():
    X = np.column_stack([np.arange(6.0), np.arange(6.0)])
    y = np.array([0, 0, 0, 1, 1, 1])
    assert tf.best_split(X, y)[0] == 0                                  # tie: lower feature index
    assert tf.best_split(X, y, min_samples_leaf=4) is None
    assert tf.best_split(np.ones((5, 2)), np.array([0, 1, 0, 1, 0])) is None


def test_r2_never_splits_between_equal_values():
    X = np.array([[1.0], [1.0], [2.0], [2.0]])
    y = np.array([0, 1, 0, 1])
    j, thr, gain = tf.best_split(X, y)
    assert thr == 1.5 and gain == pytest.approx(0.0)


def test_r2_speed():
    rng = np.random.default_rng(0)
    X, y = rng.normal(size=(20000, 5)), rng.integers(0, 3, 20000)
    t = time.time()
    tf.best_split(X, y)
    assert time.time() - t < 2.0


@pytest.mark.parametrize("depth,leaf", [(3, 1), (4, 1), (5, 10)])
def test_r3_r4_agrees_with_sklearn(depth, leaf):
    X, y = datagen.make_cassava(900, 2026)
    mine = tf.DecisionTree(max_depth=depth, min_samples_leaf=leaf).fit(X, y)
    ref = DecisionTreeClassifier(criterion="gini", max_depth=depth, min_samples_leaf=leaf, random_state=0).fit(X, y)
    assert mine.n_leaves_ == ref.get_n_leaves() and mine.depth_ == ref.get_depth()
    Xt, _ = datagen.make_cassava(2000, 99)
    assert (mine.predict(Xt) == ref.predict(Xt)).mean() >= 0.99
    assert np.allclose(mine.feature_importances_, ref.feature_importances_, atol=1e-9)


def test_r3_proba_and_classes():
    X, y = datagen.make_cassava(300, 5)
    t = tf.DecisionTree(max_depth=3).fit(X, y)
    p = t.predict_proba(X)
    assert p.shape == (300, 3) and np.allclose(p.sum(1), 1) and list(t.classes_) == [0, 1, 2]
    assert (t.predict(X) == t.classes_[p.argmax(1)]).all()


def test_r3_does_not_mutate_inputs_and_single_class():
    X, y = datagen.make_cassava(100, 6)
    X0, y0 = X.copy(), y.copy()
    tf.DecisionTree().fit(X, y)
    assert np.array_equal(X, X0) and np.array_equal(y, y0)
    t = tf.DecisionTree().fit(X, np.zeros(100, dtype=int))
    assert t.n_leaves_ == 1 and t.depth_ == 0 and t.feature_importances_.sum() == 0


def test_r5_rules_reproduce_predictions():
    X, y = datagen.make_cassava(500, 7)
    names = datagen.FEATURES
    t = tf.DecisionTree(max_depth=4).fit(X, y)
    rules = tf.export_rules(t, names)
    assert len(rules) == t.n_leaves_
    pat = re.compile(r"^IF (.+) THEN class=(\d+)$")
    parsed = []
    for r in rules:
        m = pat.match(r)
        assert m, r
        conds = [re.match(r"^(\w+) (<=|>) (\S+)$", c).groups() for c in m.group(1).split(" AND ")]
        parsed.append((conds, int(m.group(2))))
    for x, pred in zip(X, t.predict(X)):
        hits = [c for conds, c in parsed if all((x[names.index(f)] <= float(v)) if op == "<=" else (x[names.index(f)] > float(v)) for f, op, v in conds)]
        assert len(hits) == 1 and hits[0] == pred


def test_r5_single_leaf_rule():
    X, y = datagen.make_cassava(50, 8)
    assert tf.export_rules(tf.DecisionTree().fit(X, np.full(50, 2)), datagen.FEATURES) == ["IF TRUE THEN class=2"]


def test_xor_needs_depth():
    Xtr, ytr = datagen.make_xor(800, 1)
    Xte, yte = datagen.make_xor(2000, 2)
    a1 = (tf.DecisionTree(max_depth=1).fit(Xtr, ytr).predict(Xte) == yte).mean()
    a8 = (tf.DecisionTree(max_depth=8).fit(Xtr, ytr).predict(Xte) == yte).mean()
    assert a1 <= 0.60 and a8 >= 0.95


def test_r6_depth_sweep_monotone_train():
    Xtr, ytr = datagen.make_cassava(600, 11)
    Xva, yva = datagen.make_cassava(600, 12)
    s = tf.depth_sweep(Xtr, ytr, Xva, yva, [1, 2, 4, 8, 16])
    tr = [a for _, a, _ in s]
    assert all(b >= a - 1e-12 for a, b in zip(tr, tr[1:])) and tr[-1] - tr[0] >= 0.15
    assert [d for d, _, _ in s] == [1, 2, 4, 8, 16]
