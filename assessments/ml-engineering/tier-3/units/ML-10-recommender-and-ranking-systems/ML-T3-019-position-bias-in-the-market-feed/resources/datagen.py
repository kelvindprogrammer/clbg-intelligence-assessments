"""Deterministic synthetic click logs for a fictional marketplace feed (ML-T3-019).

Each query shows K = 8 vendor listings in a ranked list. A click happens with probability exam[position] * relevance,
the standard position-based model. The *logging policy* ranked listings with an imperfect score that also penalised small
vendors; a random 10% of queries were shown in uniformly random order (an exploration slice).

`true_relevance` and `TRUE_EXAM` are the generator's hidden truth. They exist for the tests and for your simulations of
the *generator*; a submission whose feature pipeline, training or selection touches them is an integrity breach.
"""
import numpy as np

K = 8
D = 5                                    # x0..x3 listing quality signals, x4 = small-vendor flag
TRUE_EXAM = 1.0 / (np.arange(K) + 1.0) ** 1.2
_W = np.array([1.0, 0.8, -0.7, 0.5, 0.9])
_B = -2.2
_W_LOG = np.array([0.8, 0.2, -0.2, 0.3, -2.0])


def true_relevance(X):
    return 1.0 / (1.0 + np.exp(-(X @ _W + _B)))


def make_logs(n_queries=8000, seed=2026, random_frac=0.10):
    """Return a dict of row-level arrays (n_queries * K rows, grouped by query): qid, pos, X, click, randomized."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_queries, K, D))
    X[:, :, 4] = (rng.random((n_queries, K)) < 0.3).astype(float)
    rand_q = rng.random(n_queries) < random_frac
    logscore = X @ _W_LOG + rng.normal(0, 0.8, (n_queries, K))
    order = np.argsort(-logscore, axis=1, kind="stable")
    order[rand_q] = np.argsort(rng.random((rand_q.sum(), K)), axis=1)
    Xs = np.take_along_axis(X, order[:, :, None], axis=1)
    p = TRUE_EXAM[None, :] * true_relevance(Xs)
    click = (rng.random((n_queries, K)) < p).astype(int)
    return {"qid": np.repeat(np.arange(n_queries), K), "pos": np.tile(np.arange(K), n_queries), "X": Xs.reshape(-1, D),
            "click": click.ravel(), "randomized": np.repeat(rand_q, K)}


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = make_logs(seed=a.seed)
    np.savetxt(os.path.join(a.out, "feed_log.csv"), np.column_stack([d["qid"], d["pos"], d["X"], d["click"], d["randomized"]]), delimiter=",", fmt="%.5g",
               header="qid,pos,quality,rating,distance_km,delivery_speed,small_vendor,click,randomized", comments="")
