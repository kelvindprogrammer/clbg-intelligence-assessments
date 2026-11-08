"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, specs and constraints."""
import numpy as np
import pytest
from scipy import sparse

import datagen
import langsqueeze as ls

MAX_BYTES, MAX_MACS = 10_000, 2_000


def test_r1_pareto_by_hand():
    pts = [{"size": 10, "acc": 0.70}, {"size": 5, "acc": 0.60}, {"size": 12, "acc": 0.70}, {"size": 5, "acc": 0.60},
           {"size": 3, "acc": 0.40}, {"size": 20, "acc": 0.65}]
    # point 3 duplicates point 1 (the lowest index is kept); 2 and 5 are dominated by 0
    assert ls.pareto_front(pts, minimize=["size"], maximize=["acc"]) == [0, 1, 4]


def test_r1_pareto_three_objectives_and_empty():
    pts = [{"a": 1, "b": 1, "c": 5}, {"a": 1, "b": 2, "c": 5}, {"a": 2, "b": 1, "c": 6}]
    assert ls.pareto_front(pts, minimize=["a", "b"], maximize=["c"]) == [0, 2]
    assert ls.pareto_front([], ["a"], []) == []


def test_r2_cost_model_by_hand():
    assert ls.cost_model({"kind": "linear", "n_features": 1024, "n_classes": 8, "bits": 8}, 50) == {"size_bytes": 8256, "macs": 400.0}
    s = ls.cost_model({"kind": "linear", "n_features": 1024, "n_classes": 8, "bits": 8, "nnz": 1000}, 50)
    assert s["size_bytes"] == 2689 and s["macs"] == pytest.approx(50 * 1000 / 1024)       # 13-bit index, sparse wins
    assert ls.cost_model({"kind": "linear", "n_features": 65536, "n_classes": 8, "bits": 32}, 100)["size_bytes"] == 2097152 + 32
    lr = ls.cost_model({"kind": "lowrank", "n_features": 1000, "n_classes": 8, "rank": 2, "bits": 8}, 50)
    assert lr == {"size_bytes": 2088, "macs": 116.0}


def test_r3_distill_matches_closed_form_with_unpenalised_intercept():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(60, 7)) + 3.0
    T = X @ rng.normal(size=(7, 3)) + 5.0
    W, b = ls.distill_ridge(sparse.csr_matrix(X), T, alpha=2.0)
    Xc, Tc = X - X.mean(0), T - T.mean(0)
    W0 = np.linalg.solve(Xc.T @ Xc + 2.0 * np.eye(7), Xc.T @ Tc)
    assert np.allclose(W, W0, atol=1e-6) and np.allclose(b, T.mean(0) - X.mean(0) @ W0, atol=1e-6)


def test_r5_choose_one_standard_error_rule():
    rows = [{"name": "big", "size_bytes": 9000, "macs": 900, "val_acc": 0.70},
            {"name": "mid", "size_bytes": 5000, "macs": 500, "val_acc": 0.66},       # SE of 0.70 at n=100 is 0.0458
            {"name": "tiny", "size_bytes": 1000, "macs": 100, "val_acc": 0.60},
            {"name": "huge", "size_bytes": 2_000_000, "macs": 9000, "val_acc": 0.80}]
    assert ls.choose(rows, MAX_BYTES, MAX_MACS, 100) == "mid"                         # threshold 0.70 - 0.0458 = 0.654 keeps mid, drops tiny
    assert ls.choose(rows, MAX_BYTES, MAX_MACS, 10_000) == "big"
    with pytest.raises(ValueError):
        ls.choose(rows, 500, 50, 100)


@pytest.fixture(scope="module")
def study():
    task = datagen.make_task(2026)
    W, b = datagen.train_teacher(task)
    cands = ls.build_candidates(task, W, b)
    return task, (W, b), cands


def test_r4_candidates_are_honest_and_diverse(study):
    task, (W, b), cands = study
    assert len(cands) >= 8 and len({c["family"] for c in cands}) >= 3 and len({c["name"] for c in cands}) == len(cands)
    for c in cands:
        sp, M = c["spec"], c["W"]
        assert sp["n_features"] == M.shape[0] and sp["n_classes"] == M.shape[1] == len(c["b"])
        if sp["kind"] == "linear":
            if sp["bits"] < 32:
                assert max(len(np.unique(M[:, j])) for j in range(M.shape[1])) <= 2 ** sp["bits"]
            assert sp.get("nnz", M.size) >= np.count_nonzero(M)
        else:
            assert np.linalg.matrix_rank(M) <= sp["rank"]
    assert any(c["spec"]["kind"] == "linear" and c["spec"]["bits"] == 32 and c["spec"]["n_features"] == 65536 for c in cands)


def test_r4_frontier_and_chosen_model_meet_the_brief(study):
    task, (W, b), cands = study
    avg = datagen.avg_active(task["shifted_texts"])
    rows = []
    for c in cands:
        m = ls.cost_model(c["spec"], avg)
        rows.append({"name": c["name"], "size_bytes": m["size_bytes"], "macs": m["macs"],
                     "val_acc": ls.accuracy(c, task["val_texts"], task["val_y"]),
                     "shifted": ls.accuracy(c, task["shifted_texts"], task["shifted_y"]),
                     "clean": ls.accuracy(c, task["clean_texts"], task["clean_y"])})
    front = ls.pareto_front(rows, minimize=["size_bytes", "macs"], maximize=["shifted"])
    assert len(front) >= 3
    chosen = {r["name"]: r for r in rows}[ls.choose(rows, MAX_BYTES, MAX_MACS, len(task["val_y"]))]
    teacher = max(rows, key=lambda r: r["size_bytes"])
    assert chosen["size_bytes"] <= MAX_BYTES and chosen["macs"] <= MAX_MACS
    assert chosen["clean"] >= 0.94 and chosen["shifted"] >= teacher["shifted"] - 0.08, (chosen, teacher)
    assert teacher["shifted"] < teacher["clean"] - 0.15          # the shift is real: clean accuracy hides it
