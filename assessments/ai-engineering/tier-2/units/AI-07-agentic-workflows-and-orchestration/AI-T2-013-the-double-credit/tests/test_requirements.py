import copy

import loan_services as ls
import sagarun as s

REQ = {"loan": "L1", "member": "M1", "amount": 100000}
CFG = s.DEFAULT_CFG
ZERO = {"reserved": 0, "credited": 0, "ledger_open": 0, "sms": 0}
FULL = {"reserved": 100000, "credited": 100000, "ledger_open": 1, "sms": 1}


def good():
    return ls.MockPlanner.good(REQ)


def run(svc=None, req=REQ, cfg=CFG, plan=None, approver=None):
    svc = svc or ls.Services()
    clock = ls.FakeClock()
    return svc, clock, s.run_saga(svc, plan or ls.MockPlanner.good(req), req, cfg, clock, approver)


def test_r1_valid_plan_has_no_errors_and_each_defect_has_its_exact_message():
    assert s.validate_plan(good(), ls.TOOLS) == []
    p = good(); p[1]["deps"] = ["s1", "s5"]
    assert s.validate_plan(p, ls.TOOLS) == ["cycle"]
    p = good(); p[3]["tool"] = "wire_transfer_abroad"
    assert s.validate_plan(p, ls.TOOLS) == ["unknown_tool: s4"]
    p = good(); p[2]["deps"] = ["s2", "s9"]
    assert s.validate_plan(p, ls.TOOLS) == ["unknown_dep: s3->s9"]
    p = good(); p[3]["id"] = "s3"
    assert s.validate_plan(p, ls.TOOLS) == ["duplicate_id: s3", "unknown_dep: s5->s4"]
    p = good(); p[4]["deps"] = ["s1"]
    assert s.validate_plan(p, ls.TOOLS) == ["irreversible_early: s5"]


def test_r2_waves_are_layers_with_sorted_ids():
    assert s.waves(good()) == [["s1"], ["s2"], ["s3", "s4"], ["s5"]]
    p = good(); p.reverse()
    assert s.waves(p) == [["s1"], ["s2"], ["s3", "s4"], ["s5"]]


def test_r3_call_step_retries_transient_and_timeouts_with_backoff():
    svc, clock = ls.Services(script={"credit_wallet": ["transient", "timeout_before", "ok"]}), ls.FakeClock()
    r = s.call_step(svc, good()[2], "L1", CFG["policy"], clock)
    assert r["ok"] and r["attempts"] == 3 and clock.sleeps[-2:] == [1.0, 2.0] and r["error"] is None


def test_r3_permanent_is_not_retried_and_exhaustion_is_reported():
    svc, clock = ls.Services(script={"credit_wallet": ["permanent"]}), ls.FakeClock()
    r = s.call_step(svc, good()[2], "L1", CFG["policy"], clock)
    assert (r["ok"], r["attempts"], r["error"], svc.calls) == (False, 1, "permanent", 1)
    svc, clock = ls.Services(script={"credit_wallet": ["transient"] * 9}), ls.FakeClock()
    r = s.call_step(svc, good()[2], "L1", CFG["policy"], clock)
    assert (r["ok"], r["attempts"], r["error"]) == (False, 4, "exhausted") and clock.sleeps == [1.0, 2.0, 4.0]


def test_r4_happy_path_commits_and_parallel_wave_saves_time():
    svc, clock, rep = run()
    assert rep["status"] == "committed" and rep["done"] == ["s1", "s2", "s3", "s4", "s5"] and rep["failed"] is None
    assert rep["makespan"] == 7.0 and clock.now() == 7.0 and svc.audit()["L1"] == FULL


def test_r4_ambiguous_timeout_is_safe_with_idempotency_keys_and_double_credits_without():
    svc, _, rep = run(ls.Services(script={"credit_wallet": ["timeout_after"]}))
    assert rep["status"] == "committed" and svc.audit()["L1"] == FULL and rep["makespan"] == 13.0
    svc, _, rep = run(ls.Services(script={"credit_wallet": ["timeout_after"]}), cfg={**CFG, "idempotent": False})
    assert svc.audit()["L1"]["credited"] == 200000


def test_r4_permanent_failure_compensates_the_failed_step_too_in_reverse_order():
    svc, clock, rep = run(ls.Services(script={"post_ledger": ["permanent"]}))
    assert rep["status"] == "rolled_back" and rep["failed"] == "s4" and rep["done"] == ["s1", "s2", "s3"]
    assert rep["compensated"] == ["s4", "s3", "s2"] and svc.audit()["L1"] == ZERO and rep["makespan"] == 10.0


def test_r4_ambiguous_timeout_on_a_step_that_then_exhausts_is_still_cleaned_up():
    svc, _, rep = run(ls.Services(script={"credit_wallet": ["timeout_after"] * 4}))
    assert rep["status"] == "rolled_back" and rep["failed"] == "s3" and svc.audit()["L1"] == ZERO


def test_r4_failed_compensation_is_reported_as_stuck():
    svc, _, rep = run(ls.Services(script={"post_ledger": ["permanent"]}, permanent_tools=("release_funds",)))
    assert rep["status"] == "stuck" and rep["compensation_failed"] == ["s2"] and rep["compensated"] == ["s4", "s3"]


def test_r4_invalid_plan_makes_no_calls_and_ineligible_member_stops_at_once():
    p = good(); p[1]["deps"] = ["s1", "s5"]
    svc, _, rep = run(plan=p)
    assert rep["status"] == "invalid" and rep["errors"] == ["cycle"] and svc.calls == 0
    svc, _, rep = run(req={"loan": "L2", "member": "X9", "amount": 5})
    assert rep["status"] == "rolled_back" and rep["failed"] == "s1" and svc.calls == 1 and svc.audit() == {}


def test_r4_large_loan_needs_approval_before_any_money_moves():
    big = {"loan": "L3", "member": "M1", "amount": 600000}
    svc, _, rep = run(req=big)
    assert rep["status"] == "rejected" and svc.calls == 1 and svc.audit() == {} and rep["makespan"] == 1.0
    svc, _, rep = run(req=big, approver=lambda r, p: False)
    assert rep["status"] == "rejected"
    asked = []
    svc, _, rep = run(req=big, approver=lambda r, p: asked.append(r["loan"]) or True)
    assert rep["status"] == "committed" and asked == ["L3"]


def test_r5_plan_with_repair_feeds_errors_back_and_gives_up_on_stubborn_planners():
    r = s.plan_with_repair(ls.MockPlanner(seed=3, p_bad=1.0), REQ, ls.TOOLS)
    assert r["asks"] == 2 and r["plan"] == good() and len(r["errors_history"]) == 1 and r["errors_history"][0]
    r = s.plan_with_repair(ls.MockPlanner(seed=3, p_bad=1.0, stubborn=True), REQ, ls.TOOLS, max_asks=3)
    assert r["plan"] is None and r["asks"] == 3 and len(r["errors_history"]) == 3


def test_r6_violations_compare_world_with_promises():
    reqs = [REQ, {"loan": "L2", "member": "M2", "amount": 50}]
    audit = {"L1": dict(FULL, credited=200000), "L2": dict(ZERO, reserved=50)}
    assert s.violations(audit, reqs, ["committed", "rolled_back"]) == ["L1: credited", "L2: reserved"]
    assert s.violations({}, reqs, ["stuck", "rejected"]) == []


def test_r6_batch_has_no_violations_under_failures_bad_plans_and_approvals():
    reqs = [{"loan": f"L{i}", "member": ("X1" if i % 17 == 0 else f"M{i}"), "amount": 50000 * (1 + i % 14)} for i in range(80)]
    svc = ls.Services(seed=4, p_transient=.1, p_timeout_after=.1, p_timeout_before=.05)
    out = s.run_batch(svc, ls.MockPlanner(seed=4, p_bad=.2), reqs, CFG, ls.FakeClock, approver=lambda r, p: r["amount"] < 600000)
    assert out["violations"] == [] and out["n"] == 80
    assert out["committed"] + out["rolled_back"] + out["rejected"] + out["stuck"] + out["invalid"] == 80
    assert out["committed"] >= 40 and out["rejected"] >= 1 and out["p95_makespan"] >= 7.0
