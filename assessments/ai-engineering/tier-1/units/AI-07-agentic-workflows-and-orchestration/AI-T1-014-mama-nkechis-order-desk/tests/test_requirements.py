import json

import desk_model as dm
import orderdesk as o


def mk(fn, nxt, retries=0):
    return {"fn": fn, "next": nxt, "retries": retries}


LINEAR = {
    "a": mk(lambda s, c: ({"x": s.get("x", 0) + 1}, "go"), {"go": "b"}),
    "b": mk(lambda s, c: ({"y": s["x"] * 10}, "*"), {"*": o.END}),
}


def test_r1_runs_routes_and_traces():
    r = o.run_workflow(LINEAR, "a", {"x": 4}, {})
    assert r["status"] == "done" and r["state"] == {"x": 5, "y": 50} and r["error"] is None
    assert r["trace"] == [{"step": "a", "label": "go", "attempts": 1}, {"step": "b", "label": "*", "attempts": 1}]


def test_r1_input_state_is_not_mutated_and_steps_cannot_alias_state():
    st = {"x": 1, "items": [1]}
    g = {"a": mk(lambda s, c: (s["items"].append(2) or {}, "*"), {"*": o.END})}
    r = o.run_workflow(g, "a", st, {})
    assert st == {"x": 1, "items": [1]} and r["state"]["items"] == [1]


def test_r1_label_falls_back_to_star_and_missing_edge_is_an_error():
    g = {"a": mk(lambda s, c: ({}, "weird"), {"*": o.END})}
    assert o.run_workflow(g, "a", {}, {})["status"] == "done"
    g = {"a": mk(lambda s, c: ({}, "weird"), {"go": o.END})}
    r = o.run_workflow(g, "a", {}, {})
    assert (r["status"], r["error"]) == ("error", "no_edge: a:weird")
    assert o.run_workflow(g, "zzz", {}, {})["error"] == "unknown_step: zzz"


def test_r2_transient_errors_are_retried_up_to_the_step_limit():
    m = dm.DeskModel(fail_first=2)
    g = {"a": mk(lambda s, c: ({"i": m.classify("x")["intent"]}, "*"), {"*": o.END}, retries=2)}
    r = o.run_workflow(g, "a", {}, {})
    assert r["status"] == "done" and r["trace"][0]["attempts"] == 3 and r["state"]["i"] == "other"
    m = dm.DeskModel(fail_first=3)
    g = {"a": mk(lambda s, c: ({"i": m.classify("x")}, "*"), {"*": o.END}, retries=2)}
    r = o.run_workflow(g, "a", {"k": 1}, {})
    assert (r["status"], r["error"], r["state"]) == ("error", "a: TransientError", {"k": 1}) and m.calls == 3


def test_r2_other_exceptions_are_not_retried_and_never_escape():
    calls = []

    def boom(s, c):
        calls.append(1)
        raise ValueError("bad")
    r = o.run_workflow({"a": mk(boom, {"*": o.END}, retries=5)}, "a", {}, {})
    assert r["status"] == "error" and r["error"] == "a: ValueError" and len(calls) == 1


def test_r3_cycles_are_stopped_by_visit_limit_and_step_limit():
    g = {"a": mk(lambda s, c: ({}, "*"), {"*": "b"}), "b": mk(lambda s, c: ({}, "*"), {"*": "a"})}
    r = o.run_workflow(g, "a", {}, {}, max_visits=3)
    assert r["status"] == "loop" and r["error"] == "loop: a" and len(r["trace"]) == 6
    r = o.run_workflow(g, "a", {}, {}, max_steps=3, max_visits=99)
    assert r["status"] == "loop" and r["error"] == "max_steps" and len(r["trace"]) == 3


def test_r4_pause_gives_a_json_checkpoint_and_resume_continues():
    g = {
        "a": mk(lambda s, c: ({"asked": True}, "*"), {"*": "HUMAN:b"}),
        "b": mk(lambda s, c: ({"done": s["answer"]}, "*"), {"*": o.END}),
    }
    r = o.run_workflow(g, "a", {}, {})
    assert r["status"] == "paused" and r["checkpoint"]["resume_at"] == "b"
    cp = json.loads(json.dumps(r["checkpoint"]))
    r2 = o.resume(g, cp, {}, {"answer": "yes"})
    assert r2["status"] == "done" and r2["state"] == {"asked": True, "answer": "yes", "done": "yes"}
    assert r["state"] == {"asked": True}


def test_r5_validate_graph_reports_sorted_problems():
    f = lambda s, c: ({}, "*")
    g = {"a": mk(f, {"*": "b", "x": "ghost"}), "b": mk(f, {"*": "a"}), "orphan": mk(f, {"*": o.END})}
    assert o.validate_graph(g, "a") == ["no_end", "unknown_target: a->ghost", "unreachable: orphan"]
    assert o.validate_graph(LINEAR, "a") == []
    assert o.validate_graph(LINEAR, "nope") == ["unknown_start"]
    h = {"a": mk(f, {"*": "HUMAN:b"}), "b": mk(f, {"*": o.END})}
    assert o.validate_graph(h, "a") == []


def desk(model=None, **kw):
    return o.build_order_desk(model or dm.DeskModel(**kw), dm.CATALOGUE)


def test_r6_desk_graph_is_statically_valid():
    assert o.validate_graph(desk(), "classify") == []


def test_r6_order_is_priced():
    r = o.run_workflow(desk(), "classify", {"text": "please send me 2 bags of rice and 3 tins of palm oil"}, {})
    assert r["status"] == "done" and r["state"]["total"] == 2 * 45000 + 3 * 30000
    assert r["state"]["reply"] == "Total NGN 180000 for 2 line(s)" and r["state"]["outcome"] == "quoted"
    assert [t["step"] for t in r["trace"]] == ["classify", "extract", "price", "confirm"]


def test_r6_complaint_pauses_for_staff_then_finishes():
    r = o.run_workflow(desk(), "classify", {"text": "the garri was spoilt"}, {})
    assert r["status"] == "paused" and r["checkpoint"]["resume_at"] == "resolved"
    r2 = o.resume(desk(), r["checkpoint"], {}, {"staff_note": "refund sent"})
    assert r2["status"] == "done" and r2["state"]["reply"] == "Handled by staff: refund sent" and r2["state"]["outcome"] == "escalated"


def test_r6_unknown_item_triggers_clarification_loop_that_ends():
    asks = iter(["I want 1 bag of rice"])
    ctx = {"ask_customer": lambda s: next(asks, None)}
    r = o.run_workflow(desk(), "classify", {"text": "send me 1 bag of diamonds"}, ctx)
    assert r["status"] == "done" and r["state"]["total"] == 45000 and r["state"]["clarifications"] == 1
    r = o.run_workflow(desk(), "classify", {"text": "send me 1 bag of diamonds"}, {"ask_customer": lambda s: None})
    assert r["status"] == "paused" and r["checkpoint"]["resume_at"] == "resolved"


def test_r6_flaky_model_is_absorbed_by_retries():
    r = o.run_workflow(desk(fail_first=2), "classify", {"text": "order 1 gallon of palm oil"}, {})
    assert r["status"] == "done" and r["state"]["total"] == 30000 and r["trace"][0]["attempts"] == 3
