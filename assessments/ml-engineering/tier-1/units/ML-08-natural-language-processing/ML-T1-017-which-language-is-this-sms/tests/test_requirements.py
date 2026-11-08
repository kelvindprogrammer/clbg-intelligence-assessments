"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and noise levels."""
from collections import Counter

import numpy as np
import pytest
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB

import datagen
import smslang as sl


def test_r1_tokenize():
    assert sl.tokenize("Abeg, send N500!!") == ["abeg", "send", "n", "<num>"]
    assert sl.tokenize("DON'T 12 34") == ["don't", "<num>", "<num>"]
    assert sl.tokenize("") == [] and sl.tokenize("\U0001F64F ...") == []


def test_r2_char_ngrams():
    assert sl.char_ngrams("na", 2, 3) == ["<n", "na", "a>", "<na", "na>"]
    assert sl.char_ngrams("a", 2, 4) == ["<a", "a>", "<a>"]
    assert len(sl.char_ngrams("abeg", 2, 4)) == 5 + 4 + 3


def test_r3_extract_features_counts():
    c = sl.extract_features("na na N5", 2, 2)
    assert isinstance(c, Counter) and c["w:na"] == 2 and c["c:<n"] == 4 and c["w:<num>"] == 1 and c["c:na"] == 2


@pytest.fixture(scope="module")
def corpus():
    Xt, yt = datagen.make_messages(900, seed=1)
    Xe, ye = datagen.make_messages(900, seed=2)
    return Xt, yt, Xe, ye


def test_r4_log_proba_normalised_and_sorted_classes(corpus):
    Xt, yt, *_ = corpus
    nb = sl.NaiveBayes().fit([sl.extract_features(t) for t in Xt], yt)
    assert nb.classes_ == sorted(set(yt))
    lp = nb.predict_log_proba([sl.extract_features(t) for t in Xt[:20]])
    assert lp.shape == (20, 3) and np.allclose(np.logaddexp.reduce(lp, axis=1), 0.0)


@pytest.mark.parametrize("alpha", [1.0, 0.1])
def test_r4_matches_sklearn_multinomial(corpus, alpha):
    Xt, yt, Xe, ye = corpus
    dt, de = [sl.extract_features(t) for t in Xt[:300]], [sl.extract_features(t) for t in Xe[:100]]
    nb = sl.NaiveBayes(alpha).fit(dt, yt[:300])
    dv = DictVectorizer().fit(dt)
    ref = MultinomialNB(alpha=alpha).fit(dv.transform(dt), yt[:300])
    assert np.allclose(nb.predict_log_proba(de), ref.predict_log_proba(dv.transform(de)), atol=1e-8)


def test_r4_unseen_features_ignored_and_no_underflow(corpus):
    Xt, yt, *_ = corpus
    nb = sl.NaiveBayes().fit([sl.extract_features(t) for t in Xt], yt)
    lp = nb.predict_log_proba([Counter({"w:zzzz-never-seen": 3})])[0]
    assert np.allclose(lp, nb.log_prior_ - np.logaddexp.reduce(nb.log_prior_))
    big = nb.predict_log_proba([Counter({"w:abeg": 4000, "c:<a": 4000})])[0]
    assert np.all(np.isfinite(big)) and np.logaddexp.reduce(big) == pytest.approx(0.0, abs=1e-9)


def test_r5_language_id_accuracy(corpus):
    Xt, yt, Xe, ye = corpus
    m = sl.LanguageID().fit(Xt, yt)
    acc = np.mean(np.array(m.predict(Xe)) == np.array(ye))
    assert acc >= 0.95, acc


def test_r5_predict_proba_rows_sum_to_one(corpus):
    Xt, yt, Xe, ye = corpus
    p = sl.LanguageID().fit(Xt, yt).predict_proba(Xe[:30])
    assert p.shape == (30, 3) and np.allclose(p.sum(1), 1.0)


def test_r5_abstains_on_empty_and_emoji(corpus):
    Xt, yt, Xe, ye = corpus
    m = sl.LanguageID().fit(Xt, yt)
    assert m.predict_with_abstain(["", "\U0001F64F\U0001F64F"], 0.6) == ["unk", "unk"]
    kept = np.array(m.predict_with_abstain(Xe, 0.6)) != "unk"
    assert kept.mean() > 0.9


def test_r5_noise_robustness_of_ngrams():
    Xt, yt = datagen.make_messages(900, seed=1)
    Xe, ye = datagen.make_messages(600, seed=4, noise=0.10)
    acc = np.mean(np.array(sl.LanguageID().fit(Xt, yt).predict(Xe)) == np.array(ye))
    assert acc >= 0.94, acc
