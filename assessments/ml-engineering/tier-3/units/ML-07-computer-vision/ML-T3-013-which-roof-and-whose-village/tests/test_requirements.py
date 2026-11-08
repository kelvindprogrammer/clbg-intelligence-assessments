"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, other label budgets and other villages."""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import datagen
import roofmap as rm


@pytest.fixture(scope="module")
def tiles():
    return datagen.make_tiles(30, 40, seed=0)


def test_r1_block_split_keeps_villages_whole(tiles):
    X, y, v = tiles
    tr, te = rm.village_block_split(v, 1 / 3, seed=4)
    assert not set(v[tr]) & set(v[te]) and len(tr) + len(te) == len(v)
    assert len(set(v[te])) == 10 and np.all(np.diff(tr) > 0) and np.all(np.diff(te) > 0)
    tr2, te2 = rm.village_block_split(v, 1 / 3, seed=4)
    assert np.array_equal(te, te2) and not np.array_equal(te, rm.village_block_split(v, 1 / 3, seed=5)[1])
    assert len(set(v[rm.village_block_split(v, 0.001, seed=0)[1]])) == 1          # at least one village


def test_r2_cluster_bootstrap_by_hand_and_wider_than_naive():
    g = np.repeat(np.arange(10), 20)
    c = np.zeros(200); c[g < 5] = 1.0                                              # perfectly clustered: whole villages right or wrong
    m, lo, hi = rm.cluster_bootstrap_ci(c, g, n_boot=1000, seed=0)
    assert m == pytest.approx(0.5) and lo < 0.5 < hi and (hi - lo) > 0.4
    assert rm.cluster_bootstrap_ci(c, g, 1000, 0) == (m, lo, hi)
    iid = np.random.default_rng(0).permutation(c)                                  # same mean, no clustering
    _, lo2, hi2 = rm.cluster_bootstrap_ci(iid, g, n_boot=1000, seed=0)
    assert (hi2 - lo2) < 0.5 * (hi - lo)
    assert rm.cluster_bootstrap_ci(np.ones(40), np.repeat([0, 1], 20)) == (1.0, 1.0, 1.0)


def test_r3_patch_dictionary(tiles):
    X, y, v = tiles
    D = rm.patch_dictionary(X[:300], 12, seed=0)
    assert D.shape == (12, 75) and np.allclose(D.mean(1), 0, atol=1e-6)            # atoms live in the mean-removed patch space
    assert np.allclose(D, rm.patch_dictionary(X[:300], 12, seed=0), atol=1e-3) and not np.allclose(D, rm.patch_dictionary(X[:300], 12, seed=1), atol=1e-3)


def test_r4_encode_properties(tiles):
    X, y, v = tiles
    D = rm.patch_dictionary(X[:300], 12, seed=0)
    F = rm.encode(X[:50], D)
    assert F.shape == (50, 48) and np.all(np.isfinite(F)) and F.min() >= 0 and F.std() > 0
    assert np.allclose(rm.encode(X[:50] + 0.2, D), F, atol=1e-8)                   # a uniform brightness offset must not matter
    assert np.allclose(rm.encode(X[7:8], D)[0], F[7]) and np.allclose(rm.encode(X[:50][::-1], D), F[::-1])


@pytest.fixture(scope="module")
def protocol(tiles):
    X, y, v = tiles
    te_v = np.random.default_rng(100).choice(30, 10, replace=False)
    te = np.flatnonzero(np.isin(v, te_v))
    unl = np.flatnonzero(~np.isin(v, te_v))
    lab = datagen.label_budget(y, v, 10, 30, seed=0, exclude=te_v)
    m = rm.fit_roof_classifier(X[lab], y[lab], v[lab], X[unl][:600], seed=0)
    return m, lab, te


def test_r5_interface(protocol, tiles):
    m, lab, te = protocol
    X, y, v = tiles
    assert m.chosen_ in m.report_ and "raw_pixels_logreg" in m.report_ and len(m.report_) >= 3
    assert all(0 <= a <= 1 for a in m.report_.values())
    assert m.predict_proba(X[te[:9]]).shape == (9, 3) and m.predict(X[te[:9]]).shape == (9,)


def test_r5_generalises_to_unseen_villages_better_than_raw_pixels(protocol, tiles):
    m, lab, te = protocol
    X, y, v = tiles
    acc = (m.predict(X[te]) == y[te]).mean()
    base = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=0.01)).fit(X[lab].reshape(len(lab), -1), y[lab])
    acc_base = (base.predict(X[te].reshape(len(te), -1)) == y[te]).mean()
    assert acc >= 0.82 and acc >= acc_base + 0.12, (acc, acc_base)


def test_r5_report_is_village_blocked_not_optimistic(protocol, tiles):
    """The reported estimate for the chosen model must not exceed its true held-out-village accuracy by a wide margin."""
    m, lab, te = protocol
    X, y, v = tiles
    acc = (m.predict(X[te]) == y[te]).mean()
    assert m.report_[m.chosen_] <= acc + 0.15


def test_r5_predictions_are_per_tile(protocol, tiles):
    m, lab, te = protocol
    X = tiles[0][te[:30]]
    assert np.array_equal(m.predict(X)[:8], m.predict(X[:8])) and np.array_equal(m.predict(X)[::-1], m.predict(X[::-1]))
