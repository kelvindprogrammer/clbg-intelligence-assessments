"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import lm as lmmod

pytestmark = pytest.mark.contract


def test_api_exists():
    import decodelab as d
    for n in ["softmax", "filter_top_k", "filter_top_p", "apply_repetition_penalty", "generate",
              "sequence_logprob", "beam_search", "evaluate_config", "choose_decoding"]:
        assert callable(getattr(d, n)), n


def test_mock_lm_is_deterministic_and_normalised():
    a, b = lmmod.build_lm(5), lmmod.build_lm(5)
    lg = a.logits([])
    assert np.array_equal(lg, b.logits([])) and abs(np.exp(lg).sum() - 1) < 1e-9 and len(a.vocab) == len(lg)


def test_mock_lm_validity_check():
    m = lmmod.build_lm()
    ids = [m.vocab.index(w) for w in "your balance is 5000 naira".split()]
    assert m.is_valid(ids) and not m.is_valid(ids + [m.vocab.index("free")])
