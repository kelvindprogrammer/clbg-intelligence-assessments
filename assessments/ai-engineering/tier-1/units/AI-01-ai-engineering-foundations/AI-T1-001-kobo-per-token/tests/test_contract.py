"""Contract tests: pass on the unmodified starter."""
import pytest

import corpus

pytestmark = pytest.mark.contract


def test_api_exists():
    import tokenlab as t
    for n in ["train_bpe", "encode", "decode", "build_vocab", "token_cost", "fertility"]:
        assert callable(getattr(t, n)), n


def test_corpus_deterministic_and_multilingual():
    a, b = corpus.make_corpus(seed=3), corpus.make_corpus(seed=3)
    assert a == b and set(a) == {"en", "pcm", "yo"}
    assert any(ch in "ẹọṣ" for line in a["yo"] for ch in line)


def test_corpus_small():
    c = corpus.make_corpus()
    assert sum(len(" ".join(v)) for v in c.values()) < 100_000


def test_end_marker_constant():
    import tokenlab.bpe as b
    assert b.END == "</w>"
