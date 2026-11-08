"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import rolloutlab as rl
    for n in ["two_prop_z", "noninferior", "RolloutController"]:
        assert callable(getattr(rl, n)), n
    assert rl.RolloutController({"stages": datagen.STAGES}).last_reason == ""


def test_candidates_deterministic_and_mixed():
    a, b = datagen.make_candidates(100, 5), datagen.make_candidates(100, 5)
    assert a == b and {c["kind"] for c in a} == set(datagen.KINDS)
    assert all(len(c["eff"]) == 2 for c in a)


def test_observation_contains_no_hidden_truth_and_schedule_baseline_is_unsafe():
    seen = {}

    class Spy:
        def __init__(self, info):
            pass

        def decide(self, obs):
            seen.update(obs)
            return "advance" if obs["days_in_stage"] >= 3 else "hold"

    datagen.run_rollout(Spy, datagen.make_candidates(1, 1)[0], 1)
    assert set(seen) == {"day", "stage", "days_in_stage", "frac", "champ", "cand", "shadow", "lat_cand", "lat_champ"}
    m = datagen.evaluate(datagen.ScheduleController, n=60, seed=3)
    assert m["harmful_promoted"] > 0.7 and m["good_promoted"] > 0.9
