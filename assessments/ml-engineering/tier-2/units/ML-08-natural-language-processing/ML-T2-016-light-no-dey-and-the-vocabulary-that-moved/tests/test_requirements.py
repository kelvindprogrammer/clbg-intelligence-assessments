"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and a smaller training set."""
import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline

import datagen
import discotriage as dt

C = datagen.CLASSES


def test_r1_typo_zero_is_identity_and_input_untouched():
    xs = ["no light for Hilltop 500", "TOKEN dey blink"]
    keep = list(xs)
    assert dt.typo_corrupt(xs, np.random.default_rng(0), 0.0) == xs and xs == keep


def test_r1_typo_properties():
    xs, _ = datagen.make_complaints(300, 1)
    a = dt.typo_corrupt(xs, np.random.default_rng(5), 0.2)
    b = dt.typo_corrupt(xs, np.random.default_rng(5), 0.2)
    assert a == b and len(a) == len(xs)
    changed = np.mean([x != y for x, y in zip(xs, a)])
    assert 0.5 < changed <= 1.0
    for x, y in zip(xs, a):
        assert set(y) <= set(x)                                                         # no new characters invented
        assert [c for c in y if not c.isalpha()] == [c for c in x if not c.isalpha()]  # digits, spaces, punctuation untouched


def test_r2_macro_f1_by_hand():
    yt = ["a", "a", "b", "b", "c"]
    yp = ["a", "b", "b", "b", "a"]
    assert dt.macro_f1(yt, yp, ["a", "b", "c"]) == pytest.approx(f1_score(yt, yp, average="macro", zero_division=0))
    assert dt.macro_f1(yt, yp, ["a", "b", "c", "d"]) == pytest.approx(f1_score(yt, yp, average="macro", labels=list("abcd"), zero_division=0))


def test_r3_routing_by_hand():
    p = np.array([[0.9, 0.1], [0.55, 0.45], [0.6, 0.4], [0.55, 0.45], [0.2, 0.8]])
    assert dt.route_with_budget(p, ["x", "y"], 0.4) == ["x", "REVIEW", "x", "REVIEW", "y"]   # ceil(2.0) = 2; the tie goes to the earlier row
    assert dt.route_with_budget(p, ["x", "y"], 0.0) == ["x", "x", "x", "x", "y"]
    assert dt.route_with_budget(p, ["x", "y"], 0.01).count("REVIEW") == 1                   # ceiling rule
    assert set(dt.route_with_budget(p, ["x", "y"], 1.0)) == {"REVIEW"}


@pytest.fixture(scope="module")
def world():
    Xt, yt = datagen.make_complaints(1500, 1, "early")
    Xv, yv = datagen.make_complaints(300, 2, "early")
    Xe, ye = datagen.make_complaints(1000, 3, "late")
    return Xt, yt, Xv, yv, Xe, ye


@pytest.fixture(scope="module")
def model(world):
    Xt, yt, Xv, yv, *_ = world
    return dt.build_triage(Xt, yt, Xv, yv, seed=0)


def test_r4_interface(model, world):
    Xe = world[4]
    assert model.chosen_ in model.report_ and "word_tfidf_logreg" in model.report_ and len(model.report_) >= 3
    assert all(0 <= v <= 1 for v in model.report_.values()) and list(model.classes_) == sorted(C)
    assert model.predict_proba(Xe[:7]).shape == (7, 5) and np.allclose(model.predict_proba(Xe[:7]).sum(1), 1)


def test_r4_survives_vocabulary_drift(model, world):
    Xt, yt, Xv, yv, Xe, ye = world
    base = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=2000, class_weight="balanced")).fit(Xt, yt)
    fb = f1_score(ye, base.predict(Xe), average="macro")
    fm = dt.macro_f1(ye, model.predict(Xe), C)
    assert fm >= 0.80 and fm >= 1.1 * fb, (fm, fb)


def test_r4_confidence_is_usable_for_a_review_desk(model, world):
    Xe, ye = world[4], np.array(world[5])
    r = np.array(dt.route_with_budget(model.predict_proba(Xe), list(model.classes_), 0.15))
    auto = r != "REVIEW"
    wrong = model.predict(Xe) != ye
    assert auto.mean() == pytest.approx(0.85, abs=0.005)
    assert (r[auto] != ye[auto]).mean() <= 0.09 and wrong[~auto].sum() / wrong.sum() >= 0.40


def test_r4_predictions_are_per_message(model, world):
    Xe = world[4][:40]
    assert list(model.predict(Xe[:10])) == list(model.predict(Xe)[:10]) and list(model.predict(Xe[::-1])) == list(model.predict(Xe)[::-1])
