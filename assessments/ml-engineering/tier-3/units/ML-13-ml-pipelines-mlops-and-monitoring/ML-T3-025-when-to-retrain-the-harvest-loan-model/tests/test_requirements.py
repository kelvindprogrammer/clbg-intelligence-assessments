"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, delays and costs."""
import numpy as np
import pytest

import regimes
import retrainlab as rl

CFG = {"retrain_cost": 150.0, "t0": 36}


class Never(rl.Policy):
    pass


class Weekly(rl.Policy):
    window = 8

    def decide(self, t, view):
        return True


class Spy(rl.Policy):
    def __init__(self):
        self.ts, self.checks = [], []

    def decide(self, t, view):
        self.ts.append(t)
        dl = view.delay
        self.checks.append((view.visible_weeks == list(range(0, t - dl + 1)),
                            view.y(t - dl).shape, view.X(t).shape))
        for bad in (t - dl + 1, t):
            with pytest.raises(rl.LabelNotYetAvailable):
                view.y(bad)
        with pytest.raises(ValueError):
            view.X(t + 1)
        return False


@pytest.fixture(scope="module")
def shock():
    return regimes.make_regime("shock", 1)


def test_r1_never_matches_independent_computation(shock):
    s = shock
    r = rl.simulate(Never(), s, CFG)
    m = rl.fit_model(s["X"][:25].reshape(-1, 8), s["y"][:25].reshape(-1))  # labels known at week 36: weeks 0..24
    errs = [int(np.sum(m.predict(s["X"][t]) != s["y"][t])) for t in range(36, 130)]
    assert r.n_retrains == 0 and r.retrain_weeks == [] and r.retrain_cost_total == 0.0
    assert list(r.errors_by_week) == errs and r.error_cost == sum(errs) and r.total_cost == sum(errs)


def test_r1_weekly_accounting(shock):
    r = rl.simulate(Weekly(), shock, CFG)
    assert r.retrain_weeks == list(range(36, 130)) and r.n_retrains == 94
    assert r.retrain_cost_total == 94 * 150.0 and r.total_cost == r.error_cost + r.retrain_cost_total
    r2 = rl.simulate(Weekly(), shock, {**CFG, "retrain_cost": 10.0})
    assert r2.error_cost == r.error_cost and r2.total_cost == r.error_cost + 940.0


def test_r1_policy_sees_only_what_is_known(shock):
    spy = Spy()
    rl.simulate(spy, shock, CFG)
    assert spy.ts == list(range(36, 130))
    assert all(a and b == (200,) and c == (200, 8) for a, b, c in spy.checks)


def test_r1_retrain_uses_exactly_the_requested_weeks(shock):
    class Once(rl.Policy):
        def decide(self, t, view):
            return t == 50

        def train_weeks(self, t, view):
            return [3, 5, 9, 20, 38]

    s = shock
    r = rl.simulate(Once(), s, CFG)
    m0 = rl.fit_model(s["X"][:25].reshape(-1, 8), s["y"][:25].reshape(-1))
    m1 = rl.fit_model(s["X"][[3, 5, 9, 20, 38]].reshape(-1, 8), s["y"][[3, 5, 9, 20, 38]].reshape(-1))
    errs = [int(np.sum((m0 if t < 50 else m1).predict(s["X"][t]) != s["y"][t])) for t in range(36, 130)]
    assert list(r.errors_by_week) == errs and r.retrain_weeks == [50] and r.total_cost == sum(errs) + 150.0


def test_r1_rejects_unlabelled_or_empty_training_weeks(shock):
    class Peek(rl.Policy):
        def decide(self, t, view):
            return t == 40

        def train_weeks(self, t, view):
            return [10, 30]  # week 30 is labelled only from week 42

    class Empty(Peek):
        def train_weeks(self, t, view):
            return []

    with pytest.raises(rl.LabelNotYetAvailable):
        rl.simulate(Peek(), shock, CFG)
    with pytest.raises((rl.LabelNotYetAvailable, ValueError)):
        rl.simulate(Empty(), shock, CFG)


def test_r2_candidate_policies_contract():
    cands = rl.candidate_policies(CFG)
    assert len(cands) >= 5 and {"never", "weekly"} <= set(cands)
    for name, fac in cands.items():
        a, b = fac(), fac()
        assert isinstance(a, rl.Policy) and a is not b, name


def test_r3_evaluate_policies_shape_and_value(shock):
    f = {"never": Never, "weekly": Weekly}
    tab = rl.evaluate_policies(f, {"shock": [shock]}, CFG)
    assert set(tab) == {"never", "weekly"} and set(tab["never"]) == {"shock"}
    assert tab["never"]["shock"] == rl.simulate(Never(), shock, CFG).total_cost


def test_r4_pareto_front():
    pts = [(1, 9), (2, 8), (2, 9), (3, 3), (5, 1), (5, 1), (4, 4)]
    assert rl.pareto_front(pts) == [0, 1, 3, 4, 5]
    assert rl.pareto_front([(1, 1)]) == [0]


def test_r5_recommend_minimax_regret():
    t = {"A": {"k1": 10, "k2": 50}, "B": {"k1": 30, "k2": 20}, "C": {"k1": 12, "k2": 60}}
    assert rl.recommend(t) == "B"
    assert rl.recommend({"Z": {"x": 5, "y": 5}, "M": {"x": 5, "y": 5}}) == "M"
    assert rl.recommend({"A": {"x": 1, "y": 9}, "B": {"x": 9, "y": 1}, "C": {"x": 4, "y": 4}}) == "C"


def test_r6_sweep_changes_with_retrain_cost(shock):
    out = rl.sweep({"never": Never, "weekly": Weekly}, {"shock": [shock]}, CFG, "retrain_cost", [1.0, 1e6])
    assert out == {1.0: "weekly", 1e6: "never"}


def test_acceptance_member_policies_find_the_structure():
    cands = rl.candidate_policies(CFG)
    streams = {k: [regimes.make_regime(k, 1)] for k in regimes.KINDS}
    tab = rl.evaluate_policies(cands, streams, CFG)
    for kind, bar in (("shock", 0.90), ("seasonal", 0.92)):
        best = min(tab[n][kind] for n in tab if n not in ("never", "weekly"))
        assert best <= bar * tab["never"][kind], (kind, best, tab["never"][kind])
    rec = rl.recommend(tab)
    assert all(tab[rec][k] < tab["weekly"][k] for k in tab[rec])
