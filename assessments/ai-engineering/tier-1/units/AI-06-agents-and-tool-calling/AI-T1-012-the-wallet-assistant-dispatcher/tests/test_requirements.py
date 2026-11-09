"""Requirement tests R1-R5. They fail on the starter and pass on a correct implementation."""
import json

import pytest

import toolbox as t
import wallet as w

S = {"account": {"type": "str", "required": True},
     "limit": {"type": "int", "required": False, "default": 3, "min": 1, "max": 8},
     "mode": {"type": "enum", "required": False, "values": ["a", "b"]},
     "rate": {"type": "float", "required": False, "min": 0.5}}


def registry(seed=1):
    reg = t.ToolRegistry()
    for tool in w.make_tools(seed):
        reg.register(tool["name"], tool["schema"], tool["fn"], tool["description"])
    return reg


def test_r1_validate_args_errors_are_sorted_and_specific():
    assert t.validate_args(S, {"account": "x"}) == []
    assert t.validate_args(S, {}) == ["missing: account"]
    assert t.validate_args(S, {"account": 5, "limit": "2", "zzz": 1, "aaa": 2}) == ["type: account", "type: limit", "unexpected: aaa", "unexpected: zzz"]
    assert t.validate_args(S, {"account": "x", "limit": 0, "rate": 0.1, "mode": "c"}) == ["enum: mode", "range: limit", "range: rate"]


def test_r1_bool_is_not_int_and_int_is_float():
    assert t.validate_args(S, {"account": "x", "limit": True}) == ["type: limit"]
    assert t.validate_args(S, {"account": "x", "rate": 2}) == []
    assert t.validate_args(S, {"account": "x", "rate": False}) == ["type: rate"]


def test_r2_describe_and_duplicates():
    reg = registry()
    lines = reg.describe().splitlines()
    assert lines[0] == "check_balance(account): Return the current balance in naira."
    assert lines[1] == "convert_currency(amount, to): Convert a naira amount into another currency."
    assert "list_transactions(account, limit?)" in lines[3] and len(lines) == 4
    with pytest.raises(ValueError):
        reg.register("check_balance", {}, lambda: 1, "dup")


def test_r2_call_outcomes_never_raise():
    reg = registry()
    assert reg.call("check_balance", {"account": "NG-1001"}) == {"ok": True, "result": {"account": "NG-1001", "balance": w.make_accounts(1)["NG-1001"]["balance"]}}
    assert reg.call("nope", {}) == {"ok": False, "error": "unknown_tool", "tool": "nope"}
    bad = reg.call("list_transactions", {"limit": 99})
    assert bad == {"ok": False, "error": "invalid_args", "details": ["missing: account", "range: limit"]}
    assert reg.call("check_balance", {"account": "NG-9999"}) == {"ok": False, "error": "tool_error", "type": "KeyError"}
    assert reg.call("check_balance", "not a dict")["error"] == "invalid_args"


def test_r2_defaults_are_applied():
    r = registry().call("list_transactions", {"account": "NG-1001"})
    assert r["ok"] and len(r["result"]["transactions"]) == 3


def test_r3_parse_forms():
    assert t.parse_tool_call('{"tool": "a", "args": {"x": 1}}') == ("call", "a", {"x": 1})
    assert t.parse_tool_call('Sure!\n```json\n{"tool": "a", "args": {}}\n```\nDone') == ("call", "a", {})
    assert t.parse_tool_call("FINAL: all good ") == ("final", "all good")


def test_r3_parse_braces_inside_strings_and_nesting():
    s = 'ok {"tool": "a", "args": {"note": "use } and { freely", "n": {"k": [1, 2]}}} trailing {'
    assert t.parse_tool_call(s) == ("call", "a", {"note": "use } and { freely", "n": {"k": [1, 2]}})


@pytest.mark.parametrize("text,reason", [("no json here", "no_json"), ('{"tool": "a", "args": {"x": ', "bad_json"),
                                          ('{"tool": "a", "args": {x: 1}}', "bad_json"), ('{"tool": "a"}', "bad_shape"),
                                          ('{"tool": 3, "args": {}}', "bad_shape"), ('{"tool": "a", "args": [1]}', "bad_shape")])
def test_r3_invalid_reasons(text, reason):
    assert t.parse_tool_call(text) == ("invalid", reason)


def test_r4_redact_recursive_and_pure():
    obj = {"name": "A", "BVN": "123", "nested": [{"phone": "0803", "ok": 1}], "pin": 1234}
    out = t.redact(obj)
    assert out == {"name": "A", "BVN": "***", "nested": [{"phone": "***", "ok": 1}], "pin": "***"}
    assert obj["pin"] == 1234 and t.redact({"x": 1}, keys=("x",)) == {"x": "***"}


def test_r5_simple_and_chatty_runs():
    for mode in ("balance", "chatty"):
        out = t.run_agent(w.make_model(mode), registry(), "What is my balance?")
        assert out["stopped"] == "final" and out["steps"] == 2 and str(w.make_accounts(1)["NG-1001"]["balance"]) in out["final"]
        assert [e["kind"] for e in out["trace"]] == ["call", "final"] and out["trace"][0]["tool"] == "check_balance"


def test_r5_recovers_from_bad_json_bad_args_and_unknown_tool():
    out = t.run_agent(w.make_model("badjson"), registry(), "balance")
    assert [e["kind"] for e in out["trace"]] == ["invalid", "call", "final"]
    out = t.run_agent(w.make_model("badargs"), registry(), "history")
    assert out["trace"][0]["result"]["error"] == "invalid_args" and out["final"] == "2 transactions."
    out = t.run_agent(w.make_model("unknown_tool"), registry(), "send money")
    assert out["trace"][0]["result"]["error"] == "unknown_tool" and "cannot move money" in out["final"]
    out = t.run_agent(w.make_model("toolerror"), registry(), "balance")
    assert out["trace"][0]["result"]["error"] == "tool_error" and out["stopped"] == "final"


def test_r5_runaway_agent_is_bounded():
    out = t.run_agent(w.make_model("loop"), registry(), "balance", max_steps=4)
    assert out["stopped"] == "max_steps" and out["final"] is None and out["steps"] == 4 and len(out["trace"]) == 4


def test_r5_sensitive_fields_never_reach_model_or_trace():
    seen = []
    inner = w.make_model("profile")

    class Spy:
        def next(self, messages):
            seen.append(json.dumps(messages))
            return inner.next(messages)

    out = t.run_agent(Spy(), registry(), "who am I?")
    blob = json.dumps(out["trace"]) + "".join(seen)
    acct = w.make_accounts(1)["NG-1001"]
    assert acct["bvn"] not in blob and acct["phone"] not in blob and acct["name"] in out["final"]
    assert "***" in blob
