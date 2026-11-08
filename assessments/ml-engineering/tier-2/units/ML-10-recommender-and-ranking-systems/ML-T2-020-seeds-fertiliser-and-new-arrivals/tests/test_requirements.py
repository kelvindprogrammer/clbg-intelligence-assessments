"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and a different catalogue mix."""
import numpy as np
import pytest

import datagen
import inputrec as r


@pytest.fixture(scope="module")
def world():
    d = datagen.make_purchases(seed=2026)
    tr, te = r.time_split(d["t"], d["cutoff"])
    n, m = d["n_users"], d["n_items"]
    Mtr = r.interaction_matrix(d["user"][tr], d["item"][tr], n, m)
    Mte = r.interaction_matrix(d["user"][te], d["item"][te], n, m)
    model = r.fit_recommender(d["user"][tr], d["item"][tr], d["t"][tr], n, m, d["item_attrs"], d["cutoff"])
    return d, tr, te, Mtr, Mte, model


def test_r1_time_split_by_hand():
    tr, te = r.time_split(np.array([0, 5, 9, 10, 12]), 10)
    assert tr.tolist() == [0, 1, 2] and te.tolist() == [3, 4]


def test_r2_interaction_matrix_by_hand():
    M = r.interaction_matrix([0, 0, 2], [1, 3, 0], 3, 4)
    assert M.shape == (3, 4) and M.tolist() == [[0, 1, 0, 1], [0, 0, 0, 0], [1, 0, 0, 0]]


def test_r2_repeat_purchases_stay_binary():
    assert r.interaction_matrix([0, 0], [1, 1], 1, 2).tolist() == [[0, 1]]


def test_r3_recall_by_hand():
    S = np.array([[9.0, 8, 7, 1], [1, 2, 3, 4]])
    tr = np.array([[1.0, 0, 0, 0], [0, 0, 0, 0]])
    te = np.array([[0.0, 1, 0, 1], [0, 0, 1, 0]])
    assert r.recall_at_k(S, tr, te, 2) == pytest.approx(0.75)          # u0: item 0 is seen, top2 = {1,2} -> 1/2; u1 -> 1
    assert r.recall_at_k(S, tr, te, 2, items=[2]) == pytest.approx(1.0)  # only user 1 has a test item among the subset
    assert r.recall_at_k(S, tr, te, 1) == pytest.approx(0.25)


def test_r3_users_without_test_items_do_not_count():
    S = np.array([[3.0, 2, 1], [1, 2, 3]])
    te = np.array([[1.0, 0, 0], [0, 0, 0]])
    assert r.recall_at_k(S, np.zeros((2, 3)), te, 1) == pytest.approx(1.0)


def test_r4_model_interface(world):
    d, tr, te, Mtr, Mte, model = world
    assert "popularity" in model.report_ and len(model.report_) >= 3 and model.chosen_ in model.report_
    assert all(0 <= v <= 1 for v in model.report_.values())
    assert model.score_matrix().shape == (d["n_users"], d["n_items"]) and np.isfinite(model.score_matrix()).all()


def test_r4_ignores_data_after_the_cutoff(world):
    d, tr, te, Mtr, Mte, model = world
    full = r.fit_recommender(d["user"], d["item"], d["t"], d["n_users"], d["n_items"], d["item_attrs"], d["cutoff"])
    assert np.allclose(full.score_matrix(), model.score_matrix()) and full.chosen_ == model.chosen_


def test_r5_beats_popularity_overall(world):
    d, tr, te, Mtr, Mte, model = world
    pop = np.tile(Mtr.sum(axis=0), (d["n_users"], 1))
    ours, base = r.recall_at_k(model.score_matrix(), Mtr, Mte, 10), r.recall_at_k(pop, Mtr, Mte, 10)
    assert ours >= 0.30 and ours >= 3.0 * base, (ours, base)


def test_r6_new_arrivals_are_recommendable(world):
    d, tr, te, Mtr, Mte, model = world
    cold = r.recall_at_k(model.score_matrix(), Mtr, Mte, 10, items=d["cold_items"])
    assert cold >= 0.40, cold


def test_r7_validation_picks_what_the_test_period_confirms(world):
    d, tr, te, Mtr, Mte, model = world
    assert model.chosen_ != "popularity"
    no_cold = r.recall_at_k(model.score_matrix(), Mtr, Mte, 10, items=np.setdiff1d(np.arange(d["n_items"]), d["cold_items"]))
    assert no_cold >= 0.15, no_cold                      # the cold-start fix must not wreck the established catalogue
