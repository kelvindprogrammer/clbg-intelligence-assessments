"""Contract tests: pass on the unmodified starter."""
import pytest

import loan_services as ls

pytestmark = pytest.mark.contract
REQ = {"loan": "L1", "member": "M1", "amount": 100000}


def test_api_exists():
    import sagarun as s
    for n in ["validate_plan", "waves", "call_step", "run_saga", "plan_with_repair", "violations", "run_batch"]:
        assert callable(getattr(s, n)), n
    assert s.DEFAULT_CFG["policy"]["max_attempts"] >= 1


def test_services_apply_effects_and_respect_idempotency_keys():
    svc, clock = ls.Services(), ls.FakeClock()
    svc.call("credit_wallet", {"loan": "L1", "member": "M1", "amount": 5}, "k1", clock)
    svc.call("credit_wallet", {"loan": "L1", "member": "M1", "amount": 5}, "k1", clock)
    assert svc.audit()["L1"]["credited"] == 5
    svc.call("credit_wallet", {"loan": "L1", "member": "M1", "amount": 5}, None, clock)
    svc.call("credit_wallet", {"loan": "L1", "member": "M1", "amount": 5}, None, clock)
    assert svc.audit()["L1"]["credited"] == 15 and clock.now() == 12


def test_timeout_after_applies_the_effect_and_fork_is_independent():
    svc, clock = ls.Services(script={"reserve_funds": ["timeout_after"]}), ls.FakeClock(10)
    with pytest.raises(TimeoutError):
        svc.call("reserve_funds", {"loan": "L1", "amount": 7}, "k", clock)
    assert svc.audit()["L1"]["reserved"] == 7 and clock.now() == 15
    b = clock.fork()
    b.sleep(3)
    assert clock.now() == 15 and b.now() == 18


def test_planner_is_deterministic_and_repairs_on_feedback():
    p = ls.MockPlanner(seed=1, p_bad=1.0)
    first, second = p.plan(REQ), p.plan(REQ, ["cycle"])
    assert first != second and second == ls.MockPlanner.good(REQ)
