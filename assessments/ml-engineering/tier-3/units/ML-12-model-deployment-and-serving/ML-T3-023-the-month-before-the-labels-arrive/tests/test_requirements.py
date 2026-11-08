"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, lags, base rates and signatures."""
import pytest

import datagen
import rolloutlab as rl


def test_r1_two_prop_z_by_hand():
    assert rl.two_prop_z(30, 100, 20, 100) == pytest.approx(0.1 / (0.25 * 0.75 * 0.02) ** 0.5)
    assert rl.two_prop_z(20, 100, 30, 100) == pytest.approx(-rl.two_prop_z(30, 100, 20, 100))
    assert rl.two_prop_z(0, 0, 5, 10) == 0.0 and rl.two_prop_z(0, 50, 0, 50) == 0.0


def test_r2_noninferior_by_hand():
    # pc = pk = 0.1; se = sqrt(.09/100 + .09/1000) = 0.03146
    assert rl.noninferior(10, 100, 100, 1000, margin_rel=0.5, z=1.0) is True        # 0.0315 <= 0.05
    assert rl.noninferior(10, 100, 100, 1000, margin_rel=0.5, z=2.0) is False       # 0.0629 > 0.05
    assert rl.noninferior(5, 100, 100, 1000, margin_rel=0.0, z=1.0) is True         # clearly better
    assert rl.noninferior(0, 0, 100, 1000, margin_rel=0.5, z=1.0) is False          # no evidence is not safety


def test_r3_controller_returns_valid_actions_with_reasons():
    seen = []

    class Wrap(rl.RolloutController):
        def decide(self, obs):
            a = super().decide(obs)
            seen.append((a, self.last_reason))
            return a

    datagen.run_rollout(Wrap, datagen.make_candidates(1, 11)[0], 11)
    assert seen and all(a in ("hold", "advance", "rollback") and isinstance(r, str) and r for a, r in seen)


@pytest.fixture(scope="module")
def result():
    return datagen.evaluate(rl.RolloutController, n=150, seed=2026)


def test_r3_catches_harmful_candidates(result):
    assert result["caught"] >= 0.90 and result["harmful_promoted"] <= 0.05, result["per_kind"]


def test_r3_still_promotes_good_candidates_in_reasonable_time(result):
    assert result["good_promoted"] >= 0.75 and result["good_median_days"] <= 40, result


def test_r3_harm_is_a_fraction_of_the_fixed_schedule(result):
    assert result["harm_ratio"] <= 0.35, result["harm_ratio"]


def test_r3_deterministic():
    a = datagen.evaluate(rl.RolloutController, n=40, seed=9)
    b = datagen.evaluate(rl.RolloutController, n=40, seed=9)
    assert a == b


def test_r3_works_when_lag_and_rates_change():
    m = datagen.evaluate(rl.RolloutController, n=120, seed=5, approval_shift=0.03,
                         params=dict(label_lag=10, base_default=(0.10, 0.16), daily_requests=2400, seg_share=(0.7, 0.3)))
    assert m["caught"] >= 0.85 and m["good_promoted"] >= 0.65 and m["harm_ratio"] <= 0.45, m
