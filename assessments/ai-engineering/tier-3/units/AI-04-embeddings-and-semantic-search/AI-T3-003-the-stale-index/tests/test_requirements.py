"""Public requirement tests (FAIL on the starter). Hidden tests use other worlds, drift strengths and query sets."""
import numpy as np
import pytest

import annlab as an
import catalogue


@pytest.fixture(scope="module")
def world():
    w = catalogue.make_catalogue(2026)
    Q, seg = catalogue.make_queries(w, 120, 1)
    idx = an.IVFIndex(64, 0).build(w["X"])
    return w, Q, seg, idx


def test_r1_kmeans_recovers_blobs_and_is_deterministic():
    rng = np.random.default_rng(0)
    means = np.array([[0, 0, 0], [8, 0, 0], [0, 8, 0], [0, 0, 8.0]])
    X = np.vstack([m + 0.2 * rng.normal(size=(50, 3)) for m in means])
    C = an.kmeans(X, 4, seed=1)
    assert C.shape == (4, 3) and np.allclose(C, an.kmeans(X, 4, seed=1))
    for m in means:
        assert np.linalg.norm(C - m, axis=1).min() < 0.3


def test_r1_kmeans_survives_duplicates_and_large_k():
    X = np.repeat(np.eye(3), 5, axis=0)
    C = an.kmeans(X, 6, seed=0)
    assert C.shape == (6, 3) and not np.isnan(C).any()


def test_r2_exact_search_ties_and_recall():
    X = np.array([[1.0, 0], [0, 1.0], [1.0, 0], [0.5, 0.5]])
    assert an.exact_search(X, np.array([1.0, 0]), 3).tolist() == [0, 2, 3]
    assert an.recall_at_k([[1, 2, 3], [4, 5, 6]], [[1, 2, 9], [4, 5, 6]]) == pytest.approx((2 / 3 + 1) / 2)


def test_r3_lists_partition_the_collection(world):
    w, Q, seg, idx = world
    sizes = idx.list_sizes()
    assert len(sizes) == 64 and sum(sizes) == 5000 and idx.build_qerr > 0


def test_r3_full_probe_equals_exact_and_ndist_accounting(world):
    w, Q, seg, idx = world
    ids, nd = idx.search(Q[0], 10, 64)
    assert ids.tolist() == an.exact_search(w["X"], Q[0], 10).tolist() and nd == 64 + 5000
    _, nd1 = idx.search(Q[1], 10, 1)
    assert (nd1 - 64) in idx.list_sizes()


def test_r3_recall_rises_with_nprobe_and_meets_bars(world):
    w, Q, seg, idx = world
    r = [an.evaluate_index(idx, Q, 10, p)[0] for p in (1, 2, 4, 8, 16)]
    assert all(b >= a - 1e-9 for a, b in zip(r, r[1:]))
    assert r[1] >= 0.6 and r[3] >= 0.93 and r[4] >= 0.98


def test_r3_add_is_searchable_without_retraining(world):
    w, Q, seg, _ = world
    idx = an.IVFIndex(32, 0).build(w["X"])
    C0 = idx.C.copy() if hasattr(idx, "C") else None
    new = catalogue.make_drift(w, 0.3, 50, 4)
    ids = idx.add(new)
    assert ids == list(range(5000, 5050)) and sum(idx.list_sizes()) == 5050
    got, _ = idx.search(new[7], 1, 1)
    assert got[0] == 5007
    if C0 is not None:
        assert np.allclose(C0, idx.C)


def test_r4_segment_recall_shows_the_tail_gap(world):
    w, Q, seg, idx = world
    r = an.segment_recall(idx, Q, seg, 10, 2)
    assert set(r) == {"head", "tail"} and r["head"] - r["tail"] > 0.05
    sel = [i for i, s in enumerate(seg) if s == "tail"]
    assert r["tail"] == pytest.approx(an.evaluate_index(idx, Q[sel], 10, 2)[0])


def test_r5_choose_config_respects_budget_and_is_near_best(world):
    w, Q, seg, idx = world
    budget = 700
    cfg = an.choose_config(w["X"], Q[:60], 10, budget)
    assert cfg is not None
    nl, npb = cfg
    r, nd = an.evaluate_index(an.IVFIndex(nl, 0).build(w["X"]), Q[:60], 10, npb)
    assert nd <= budget
    best = 0.0
    for l in (16, 32, 64, 128):
        ix = an.IVFIndex(l, 0).build(w["X"])
        for p in (1, 2, 4, 8, 16, 32):
            if p <= l:
                rr, d = an.evaluate_index(ix, Q[:60], 10, p)
                if d <= budget:
                    best = max(best, rr)
    assert r >= best - 0.03
    assert an.choose_config(w["X"], Q[:20], 10, 5) is None


def test_r6_drift_signals_and_policy(world):
    w, Q, seg, _ = world
    X = w["X"]
    ratios = {}
    for s in (0.0, 0.6, 1.0):
        idx = an.IVFIndex(64, 0).build(X)
        rep = an.drift_report(idx, catalogue.make_drift(w, s, 800, 9))
        ratios[s] = rep["qerr_ratio"]
        assert "imbalance" in rep
        assert bool(an.should_rebuild(rep)) == (s >= 0.6), s
    assert ratios[0.0] < ratios[0.6] < ratios[1.0]


def test_stale_index_really_is_worse_than_a_rebuilt_one(world):
    w, Q, seg, _ = world
    X = w["X"]
    Xn = catalogue.make_drift(w, 1.0, 1500, 3)
    stale = an.IVFIndex(64, 0).build(X)
    stale.add(Xn)
    allx = np.vstack([X, Xn])
    Qa = catalogue.queries_from_rows(allx, 100, 5)
    fresh = an.IVFIndex(64, 0).build(allx)
    assert an.evaluate_index(fresh, Qa, 10, 4)[0] - an.evaluate_index(stale, Qa, 10, 4)[0] > 0.08
