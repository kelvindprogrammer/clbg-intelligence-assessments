"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and edge cases."""
import numpy as np
import pytest

import datagen
import titlerank as r


def test_r1_recall_and_hit_by_hand():
    assert r.recall_at_k([3, 1, 2], {1, 2}, 2) == pytest.approx(0.5)
    assert r.recall_at_k([3, 1, 2], {1, 2}, 3) == pytest.approx(1.0)
    assert r.hit_rate_at_k([3, 1, 2], {2}, 2) == 0.0 and r.hit_rate_at_k([3, 1, 2], {2}, 3) == 1.0


def test_r1_ndcg_by_hand():
    expect = (1 / np.log2(3) + 1 / np.log2(4)) / (1 + 1 / np.log2(3))
    assert r.ndcg_at_k([3, 1, 2], {1, 2}, 3) == pytest.approx(expect)
    assert r.ndcg_at_k([1, 2, 3], {1, 2}, 3) == pytest.approx(1.0)


def test_r1_ideal_dcg_is_capped_by_k_and_empty_is_zero():
    assert r.ndcg_at_k([9, 1], {1, 2, 3, 4}, 2) == pytest.approx((1 / np.log2(3)) / (1 + 1 / np.log2(3)))
    assert r.ndcg_at_k([1, 2], set(), 2) == 0.0 and r.recall_at_k([1], set(), 1) == 0.0


def test_r2_leave_last_out_by_hand():
    u = np.array([0, 0, 0, 1, 1, 2, 2, 2])
    it = np.array([5, 6, 7, 1, 2, 3, 4, 5])
    t = np.array([1, 2, 3, 1, 2, 9, 9, 3])
    train, held = r.leave_last_out(u, it, t, min_views=3)
    assert held == {0: 7, 2: 4}                     # user 1 has 2 views; tie at t=9 goes to the later row
    assert train.tolist() == [True, True, False, True, True, True, False, True]


def test_r2_on_generated_data_is_chronological():
    u, i, t, g = datagen.make_views(seed=2026)
    train, held = r.leave_last_out(u, i, t)
    assert len(held) == 600 and (~train).sum() == 600
    for user in (0, 17, 333):
        assert t[(u == user) & ~train][0] >= t[(u == user) & train].max()


def test_r3_item_cosine_by_hand():
    M = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 0], [0, 0, 0]])
    S = r.item_cosine(M)
    assert S[0, 1] == pytest.approx(0.5) and S[0, 2] == pytest.approx(1 / np.sqrt(2)) and S[1, 2] == 0.0
    assert np.allclose(S, S.T) and np.allclose(np.diag(S), 0.0)


def test_r3_zero_column_gives_zero_not_nan():
    S = r.item_cosine(np.array([[1, 0, 1], [1, 0, 0]]))
    assert np.isfinite(S).all() and np.all(S[1] == 0) and np.all(S[:, 1] == 0)


def test_r4_recommend_excludes_seen_and_breaks_ties_low():
    sim = np.array([[0, .5, .5, .1], [.5, 0, .2, .3], [.5, .2, 0, .3], [.1, .3, .3, 0]])
    assert r.recommend(np.array([1, 0, 0, 0]), sim, 2) == [1, 2]
    assert r.recommend(np.array([1, 1, 0, 0]), sim, 5) == [2, 3]
    assert r.recommend(np.zeros(4), sim, 3) == [0, 1, 2]


def test_r5_popularity_recommend():
    M = np.array([[1, 1, 0, 0], [1, 0, 1, 0], [1, 1, 0, 1]])
    assert r.popularity_recommend(M, np.array([0, 0, 0, 0]), 2) == [0, 1]
    assert r.popularity_recommend(M, np.array([1, 0, 0, 0]), 2) == [1, 2]


def test_r6_evaluate_by_hand():
    M = np.zeros((2, 4))
    hit, nd = r.evaluate(M, {0: 2, 1: 3}, lambda row, k: [2, 0, 1][:k], 2)
    assert hit == pytest.approx(0.5) and nd == pytest.approx(0.5)


def test_r6_neighbours_beat_popularity_on_official_data():
    u, i, t, g = datagen.make_views(seed=2026)
    train, held = r.leave_last_out(u, i, t)
    M = np.zeros((600, 120))
    M[u[train], i[train]] = 1
    S = r.item_cosine(M)
    knn = r.evaluate(M, held, lambda row, k: r.recommend(row, S, k), 10)
    pop = r.evaluate(M, held, lambda row, k: r.popularity_recommend(M, row, k), 10)
    assert knn[0] >= 0.45 and knn[0] >= 2.0 * pop[0] and knn[1] >= 2.0 * pop[1], (knn, pop)
