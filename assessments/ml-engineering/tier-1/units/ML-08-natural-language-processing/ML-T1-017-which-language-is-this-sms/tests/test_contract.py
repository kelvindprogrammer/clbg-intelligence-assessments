"""Contract tests: pass on the unmodified starter."""
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import smslang as sl
    for n in ["tokenize", "char_ngrams", "extract_features", "NaiveBayes", "LanguageID"]:
        assert hasattr(sl, n), n


def test_datagen_deterministic_and_balanced():
    a, b = datagen.make_messages(300, seed=3), datagen.make_messages(300, seed=3)
    assert a == b and len(a[0]) == 300
    assert min(a[1].count(l) for l in datagen.LANGS) > 70


def test_texts_are_short():
    texts, _ = datagen.make_messages(200, seed=1)
    assert max(len(t) for t in texts) < 120
