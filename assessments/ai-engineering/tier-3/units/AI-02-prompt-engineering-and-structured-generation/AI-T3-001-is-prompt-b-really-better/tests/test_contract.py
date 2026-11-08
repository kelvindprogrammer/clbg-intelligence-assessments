"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import prompt_mock as pm

pytestmark = pytest.mark.contract


def test_api_exists():
    import promptlab as p
    for n in ["evaluate_prompt", "paired_bootstrap", "required_items", "check_leakage", "regression_gate",
              "operating_characteristics"]:
        assert callable(getattr(p, n)), n
    assert 0 < p.DEFAULT_GATE["level"] < 1


def test_eval_set_deterministic_with_slices():
    a, b = pm.make_eval_set(3, 200), pm.make_eval_set(3, 200)
    assert a == b and {it["lang"] for it in a} == set(pm.LANGS)
    assert 5 < sum(it["attack"] for it in a) < 40


def test_mock_same_prompt_same_seed_is_identical_and_edit_gives_fresh_noise():
    items, mock = pm.make_eval_set(1, 200), pm.PromptMock()
    p = pm.make_prompt()
    assert np.array_equal(mock.run(p, items, 0), mock.run(p, items, 0))
    assert not np.array_equal(mock.run(p, items, 0), mock.run(p, items, 1))
    assert not np.array_equal(mock.run(p, items, 0), mock.run(p + "\nBe polite.", items, 0))


def test_mock_documented_effects_have_the_documented_sign():
    items, mock = pm.make_eval_set(2, 600), pm.PromptMock()
    acc = lambda pr: np.mean([mock.run(pr, items, s).mean() for s in range(4)])  # noqa: E731
    base = acc(pm.make_prompt())
    assert acc(pm.make_prompt(json=False)) < base - 0.05
    assert acc(pm.make_prompt(guard=False)) < base - 0.02
    assert acc(pm.make_prompt(shots={"en": 1, "pcm": 1, "yo": 1, "ha": 1})) > base
