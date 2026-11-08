"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and a different exploration share."""
import numpy as np
import pytest

import datagen as dg
import feedrank as f


def true_value(X, qid, rank):
    """Generator truth, used for scoring only: expected clicks per query if listings sit at `rank`."""
    return float((dg.true_relevance(X) * dg.TRUE_EXAM[rank]).sum() / len(np.unique(qid)))


@pytest.fixture(scope="module")
def world():
    tr = dg.make_logs(seed=2026)
    te = dg.make_logs(n_queries=3000, seed=3026)
    exam = f.estimate_exam(tr["pos"], tr["click"], tr["randomized"], dg.K)
    return tr, te, exam


def test_r1_estimate_exam_by_hand():
    pos = np.array([0, 0, 1, 1, 0, 1])
    click = np.array([1, 1, 1, 0, 0, 0])
    rnd = np.array([1, 1, 1, 1, 0, 0])
    assert f.estimate_exam(pos, click, rnd, 2).tolist() == pytest.approx([1.0, 0.5])


def test_r1_estimate_exam_close_to_truth(world):
    tr, te, exam = world
    assert exam[0] == pytest.approx(1.0) and np.abs(exam - dg.TRUE_EXAM).max() <= 0.10


def test_r2_rank_within_queries_by_hand():
    qid = np.array([0, 0, 0, 1, 1])
    assert f.rank_within_queries(qid, np.array([0.1, 0.9, 0.5, 2.0, 2.0])).tolist() == [2, 0, 1, 0, 1]


def test_r3_ips_value_by_hand():
    qid, pos = np.array([0, 0, 1, 1]), np.array([0, 1, 0, 1])
    click, exam, new = np.array([1, 1, 0, 1]), np.array([1.0, 0.5]), np.array([1, 0, 0, 1])
    assert f.ips_value(qid, pos, click, exam, new) == pytest.approx(3.5 / 2)
    assert f.ips_value(qid, pos, click, exam, new, clip=1.5) == pytest.approx(3.0 / 2)


def test_r3_ips_tracks_truth_for_a_policy_that_was_never_run(world):
    tr, te, exam = world
    new = f.rank_within_queries(tr["qid"], dg.true_relevance(tr["X"]))     # probe policy: the generator's best order
    est, truth = f.ips_value(tr["qid"], tr["pos"], tr["click"], exam, new), true_value(tr["X"], tr["qid"], new)
    logged_avg = tr["click"].sum() / len(np.unique(tr["qid"]))
    assert abs(est - truth) / truth <= 0.08 and truth > 1.3 * logged_avg


def test_r4_ranker_interface(world):
    tr, te, exam = world
    m = f.fit_ranker(tr["X"], tr["pos"], tr["click"], exam)
    s = m.score(te["X"])
    assert s.shape == (len(te["X"]),) and np.isfinite(s).all() and np.array_equal(s, m.score(te["X"]))


def test_r4_ranker_beats_the_logging_policy_and_the_naive_click_model(world):
    from sklearn.linear_model import LogisticRegression
    tr, te, exam = world
    ours = f.fit_ranker(tr["X"], tr["pos"], tr["click"], exam)
    naive = LogisticRegression(C=10, max_iter=500).fit(tr["X"], tr["click"])
    v_ours = true_value(te["X"], te["qid"], f.rank_within_queries(te["qid"], ours.score(te["X"])))
    v_naive = true_value(te["X"], te["qid"], f.rank_within_queries(te["qid"], naive.decision_function(te["X"])))
    v_log = true_value(te["X"], te["qid"], te["pos"])
    assert v_ours >= v_log + 0.15 and v_ours >= v_naive + 0.008, (v_ours, v_naive, v_log)


def test_r5_exposure_share_by_hand():
    qid, rank, grp = np.array([0, 0, 1, 1]), np.array([0, 1, 0, 1]), np.array([1, 0, 0, 1])
    assert f.exposure_share(qid, rank, grp, np.array([1.0, 0.5])) == pytest.approx(0.5)
    assert f.exposure_share(qid, rank, np.ones(4), np.array([1.0, 0.5])) == pytest.approx(1.0)


def test_r5_debiasing_lifts_small_vendor_exposure(world):
    tr, te, exam = world
    ours = f.fit_ranker(tr["X"], tr["pos"], tr["click"], exam)
    r_ours = f.rank_within_queries(te["qid"], ours.score(te["X"]))
    small = te["X"][:, 4]
    assert f.exposure_share(te["qid"], r_ours, small, dg.TRUE_EXAM) >= 1.4 * f.exposure_share(te["qid"], te["pos"], small, dg.TRUE_EXAM)
