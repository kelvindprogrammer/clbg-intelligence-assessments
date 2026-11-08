"""Public requirement tests (R1-R7). They fail on the starter and pass on a correct solution."""
import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, pairwise_distances_argmin, silhouette_samples

from conftest import DATA
import agentmap as am


@pytest.fixture(scope="module")
def X():
    return am.load_points(DATA)


def blobs(seed=0, centres=((0, 0), (60, 0), (0, 60), (60, 60)), n=60, sd=1.5):
    rng = np.random.default_rng(seed)
    pts = np.vstack([rng.normal(c, sd, (n, 2)) for c in centres])
    return pts, np.repeat(np.arange(len(centres)), n)


def test_r1_init_returns_rows_of_x_and_is_seeded(X):
    c1 = am.kmeans_pp_init(X, 5, np.random.default_rng(1))
    c2 = am.kmeans_pp_init(X, 5, np.random.default_rng(1))
    assert c1.shape == (5, 2) and np.array_equal(c1, c2)
    assert all((X == row).all(axis=1).any() for row in c1)


def test_r1_init_spreads_over_separated_blobs():
    P, t = blobs()
    for s in range(20):
        c = am.kmeans_pp_init(P, 4, np.random.default_rng(s))
        picked = {int(np.argmin(((P - r) ** 2).sum(1)) // 60) for r in c}
        assert len(picked) == 4, "k-means++ should pick one seed per distant blob"


def test_r2_assign_matches_bruteforce(X):
    C = X[:7].copy()
    assert np.array_equal(am.assign(X, C), pairwise_distances_argmin(X, C))
    tie = am.assign(np.array([[1.0, 0.0]]), np.array([[0.0, 0.0], [2.0, 0.0]]))
    assert tie[0] == 0


def test_r3_update_is_mean_and_pure(X):
    rng = np.random.default_rng(3)
    labels = rng.integers(0, 4, len(X))
    C = X[:4].copy()
    X0, C0 = X.copy(), C.copy()
    new = am.update_centers(X, labels, C)
    for j in range(4):
        assert np.allclose(new[j], X[labels == j].mean(axis=0))
    assert np.array_equal(X, X0) and np.array_equal(C, C0)


def test_r3_empty_cluster_takes_farthest_point():
    X = np.array([[0.0, 0], [1, 0], [10, 0], [11, 0]])
    C = np.array([[0.5, 0], [100, 100], [200, 200]])
    labels = np.array([0, 0, 0, 0])
    new = am.update_centers(X, labels, C)
    far = np.argsort(-((X - C[0]) ** 2).sum(1))
    assert np.allclose(new[1], X[far[0]]) and np.allclose(new[2], X[far[1]])
    assert not np.allclose(new[1], new[2])


def test_r4_inertia(X):
    km = KMeans(5, n_init=1, random_state=0).fit(X)
    assert am.inertia(X, km.cluster_centers_, km.labels_) == pytest.approx(km.inertia_, rel=1e-9)


def test_r5_quality_close_to_sklearn(X):
    mine = am.kmeans(X, 5, seed=0, n_init=10)
    ref = KMeans(5, n_init=10, random_state=0).fit(X)
    assert mine.inertia <= ref.inertia_ * 1.01
    assert mine.labels.shape == (len(X),) and mine.centers.shape == (5, 2)
    assert mine.inertia == pytest.approx(am.inertia(X, mine.centers, mine.labels))


def test_r5_recovers_blobs_and_converges():
    P, t = blobs(2)
    r = am.kmeans(P, 4, seed=1)
    assert adjusted_rand_score(t, r.labels) == pytest.approx(1.0)
    assert r.n_iter < 100


def test_r5_deterministic_and_pure(X):
    X0 = X.copy()
    a, b = am.kmeans(X, 4, seed=5), am.kmeans(X, 4, seed=5)
    assert np.array_equal(a.labels, b.labels) and np.array_equal(a.centers, b.centers)
    assert np.array_equal(X, X0)


def test_r5_restarts_never_hurt(X):
    one = am.kmeans(X, 6, seed=2, n_init=1)
    many = am.kmeans(X, 6, seed=2, n_init=12)
    assert many.inertia <= one.inertia + 1e-9


def test_r5_edge_k_equals_n_and_k1():
    P, _ = blobs(4, n=3)
    assert am.kmeans(P, len(P), seed=0).inertia == pytest.approx(0.0, abs=1e-9)
    r1 = am.kmeans(P, 1, seed=0)
    assert np.allclose(r1.centers[0], P.mean(axis=0))


def test_r6_silhouette_matches_sklearn(X):
    r = am.kmeans(X, 5, seed=0)
    assert np.allclose(am.silhouette_scores(X, r.labels), silhouette_samples(X, r.labels), atol=1e-9)


def test_r6_singleton_scores_zero():
    P, t = blobs(5, n=10)
    lab = t.copy()
    lab[0] = 9
    s = am.silhouette_scores(P, lab)
    assert s[0] == 0.0 and np.allclose(s, silhouette_samples(P, lab), atol=1e-9)


def test_r7_choose_k_finds_blob_count_and_reports_table():
    P, _ = blobs(6, centres=((0, 0), (50, 5), (10, 55)))
    best, table = am.choose_k(P, range(2, 7), seed=0)
    assert best == 3 and [row["k"] for row in table] == [2, 3, 4, 5, 6]
    assert best == max(table, key=lambda r: r["silhouette"])["k"]
    assert all(set(row) == {"k", "inertia", "silhouette"} for row in table)
