"""Public requirement tests. These FAIL on the starter until you implement the package.

They use only the public registers and the clerical sample. The hidden suite runs your
code on re-generated registers (a different population) and scores it against the complete
ground truth, so tuning to these 250 records will not help.
"""
import time

import pytest

import linkage as lk


@pytest.fixture(scope="module")
def outputs(registers):
    a, b, c = registers
    t0 = time.time()
    res = {"cand": lk.candidate_pairs(a, b), "det": lk.deterministic_link(a, b), "fs": lk.link(a, b, c)}
    res["seconds"] = time.time() - t0
    return res


def test_candidate_pairs_format(outputs, registers):
    a, b, _ = registers
    cp = outputs["cand"]
    assert list(cp.columns) == ["a_id", "b_id"]
    assert not cp.duplicated().any()
    assert set(cp["a_id"]) <= set(a["phc_id"]) and set(cp["b_id"]) <= set(b["gh_id"])


def test_blocking_reduces_comparisons(outputs, registers):
    a, b, _ = registers
    rr = 1 - len(outputs["cand"]) / (len(a) * len(b))
    assert rr >= 0.99, f"reduction ratio {rr:.4f}: blocking keeps too many pairs"


def test_blocking_keeps_sample_matches(outputs, registers):
    _, _, c = registers
    truth = {(r.phc_id, r.true_gh_id) for r in c.itertuples() if r.true_gh_id}
    kept = truth & set(zip(outputs["cand"]["a_id"], outputs["cand"]["b_id"]))
    assert len(kept) / len(truth) >= 0.95, f"blocking loses {1 - len(kept) / len(truth):.1%} of sample matches"


def test_link_format_and_one_to_one(outputs):
    fs = outputs["fs"]
    assert list(fs.columns) == ["a_id", "b_id", "score", "decision"]
    assert set(fs["decision"]) <= {"match", "review"}
    m = fs[fs["decision"] == "match"]
    assert m["a_id"].is_unique and m["b_id"].is_unique


def test_deterministic_is_one_to_one(outputs):
    d = outputs["det"]
    assert list(d.columns) == ["a_id", "b_id"]
    assert d["a_id"].is_unique and d["b_id"].is_unique


def test_probabilistic_beats_baseline_on_sample(outputs, registers):
    _, _, c = registers
    fs = lk.evaluate_links(outputs["fs"][outputs["fs"]["decision"] == "match"], c)
    det = lk.evaluate_links(outputs["det"], c)
    assert fs["precision"] >= 0.93, fs
    assert fs["f1"] >= det["f1"] + 0.05, (fs, det)


def test_runs_in_reasonable_time(outputs):
    assert outputs["seconds"] < 300
