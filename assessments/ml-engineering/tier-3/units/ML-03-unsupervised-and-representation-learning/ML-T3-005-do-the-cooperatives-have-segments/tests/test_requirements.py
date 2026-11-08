"""Public requirement tests (R1-R5). Fail on the starter, pass on a sound solution."""
import time

import numpy as np
import pytest

import segment_lab as sl
from conftest import DATA


def skew(c):
    return float(((c - c.mean()) ** 3).mean() / c.std() ** 3)


def blobs(seed=0, k=3, n=80, gap=25.0):
    rng = np.random.default_rng(seed)
    return np.vstack([rng.normal(0, 1, (n, 2)) + [gap * j, (j % 2) * gap] for j in range(k)])


def gauss(seed=0, n=300, p=3):
    return np.random.default_rng(seed).multivariate_normal(np.zeros(p), 0.5 * np.eye(p) + 0.5, size=n)


def test_r1_prepare_tames_units_and_tails():
    X, _ = sl.simulate(3, 500, 0)
    P = sl.prepare(X)
    assert P.shape == X.shape and np.isfinite(P).all()
    assert np.array_equal(P, sl.prepare(X))
    assert max(abs(skew(P[:, j])) for j in range(3)) < 0.8, "money columns should no longer be heavy tailed"
    s = P.std(axis=0)
    assert s.max() / s.min() < 3


def test_r1_prepare_is_unit_invariant_and_pure():
    X, _ = sl.simulate(3, 400, 1)
    X0 = X.copy()
    Y = X.copy()
    Y[:, 0] *= 100.0    # naira -> kobo
    Y[:, 1] *= 100.0
    assert np.allclose(sl.prepare(X), sl.prepare(Y), atol=1e-6)
    assert np.array_equal(X, X0)


def test_r2_null_samples_gaussian_matches_moments():
    Xp = sl.prepare(sl.simulate(1, 500, 2)[0])
    nulls = sl.null_samples(Xp, 4, 0, "gaussian_cov")
    assert len(nulls) == 4 and nulls[0].shape == Xp.shape
    assert np.allclose(nulls[0].mean(axis=0), Xp.mean(axis=0), atol=0.3)
    assert np.allclose(np.corrcoef(nulls[0], rowvar=False), np.corrcoef(Xp, rowvar=False), atol=0.2)
    assert all(np.array_equal(a, b) for a, b in zip(nulls, sl.null_samples(Xp, 4, 0, "gaussian_cov")))
    assert not np.array_equal(nulls[0], nulls[1])


def test_r2_uniform_null_stays_in_pca_box_and_bad_kind_raises():
    Xp = gauss(3)
    U = sl.null_samples(Xp, 2, 0, "uniform_pca")[0]
    c = Xp - Xp.mean(axis=0)
    _, _, Vt = np.linalg.svd(c, full_matrices=False)
    T, TU = c @ Vt.T, (U - Xp.mean(axis=0)) @ Vt.T
    assert (TU >= T.min(axis=0) - 1e-9).all() and (TU <= T.max(axis=0) + 1e-9).all()
    with pytest.raises(ValueError):
        sl.null_samples(Xp, 2, 0, "student_t")


def test_r3_gap_statistic_structure_and_signal():
    g = sl.gap_statistic(blobs(), 5, n_null=8, seed=0)
    assert sorted(g) == [1, 2, 3, 4, 5] and all(v[1] > 0 for v in g.values())
    assert g[3][0] > g[2][0] + 0.2, "three well-separated blobs should show a jump in the gap at k=3"


def test_r3_null_choice_matters_on_correlated_gaussian_data():
    Xp = gauss(4)
    g_cov = sl.gap_statistic(Xp, 4, n_null=8, seed=0, null_kind="gaussian_cov")
    g_uni = sl.gap_statistic(Xp, 4, n_null=8, seed=0, null_kind="uniform_pca")
    assert max(v[0] for v in g_cov.values()) < 0.3, "a Gaussian reference should find no gap in Gaussian data"
    assert max(v[0] for v in g_uni.values()) > 0.3, "a uniform box reference invents structure in Gaussian data"


def test_r4_stability():
    assert sl.stability(gauss(5), 1) == 1.0
    sb = sl.stability(blobs(), 3, n_boot=6, seed=0)
    sg = sl.stability(gauss(5), 3, n_boot=6, seed=0)
    assert sb > 0.95 and sb > sg + 0.1
    assert sl.stability(blobs(), 3, n_boot=6, seed=0) == sb


@pytest.mark.parametrize("seed", [0, 1])
def test_r5_no_segments_reported_as_one(seed):
    X, _ = sl.simulate(1, 500, seed)
    assert sl.estimate_k(X, 6, seed=0).k == 1


@pytest.mark.parametrize("seed", [0, 2])
def test_r5_finds_segments_in_public_simulator(seed):
    X, _ = sl.simulate(2, 600, seed)
    rep = sl.estimate_k(X, 6, seed=0)
    assert rep.k == 2 and len(rep.rationale) > 30


def test_r5_unit_change_and_speed():
    X, _ = sl.simulate(3, 600, 0)
    Y = X.copy()
    Y[:, 1] *= 1000.0
    t = time.time()
    a = sl.estimate_k(X, 6, seed=0).k
    assert time.time() - t < 30
    assert a == sl.estimate_k(Y, 6, seed=0).k


def test_r5_runs_on_real_file_and_is_deterministic():
    m = sl.load_members(DATA)
    r1, r2 = sl.estimate_k(m.X, 6, seed=3), sl.estimate_k(m.X, 6, seed=3)
    assert 1 <= r1.k <= 6 and r1.k == r2.k and isinstance(r1.rationale, str) and r1.rationale
