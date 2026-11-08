"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import regimes

pytestmark = pytest.mark.contract


def test_api_exists():
    import retrainlab as rl
    for n in ["simulate", "candidate_policies", "evaluate_policies", "pareto_front", "recommend", "sweep",
              "Policy", "Result", "fit_model", "LabelNotYetAvailable"]:
        assert hasattr(rl, n), n


def test_regimes_are_deterministic_and_shaped():
    for kind in regimes.KINDS:
        a, b = regimes.make_regime(kind, 3), regimes.make_regime(kind, 3)
        assert np.array_equal(a["X"], b["X"]) and np.array_equal(a["y"], b["y"])
        assert a["X"].shape == (130, 200, 8) and a["y"].shape == (130, 200) and a["delay"] == 12
        assert 0.15 < a["y"].mean() < 0.55


def test_fit_model_and_default_policy():
    import retrainlab as rl

    class V:
        visible_weeks = list(range(40))

    p = rl.Policy()
    assert p.decide(50, V()) is False and p.train_weeks(50, V()) == list(range(14, 40))
    with pytest.raises(ValueError):
        rl.fit_model(np.zeros((4, 2)), np.zeros(4))
