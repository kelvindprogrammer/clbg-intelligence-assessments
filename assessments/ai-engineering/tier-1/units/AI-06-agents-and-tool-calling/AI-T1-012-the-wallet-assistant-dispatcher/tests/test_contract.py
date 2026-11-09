"""Contract tests: pass on the unmodified starter."""
import pytest

import wallet as w

pytestmark = pytest.mark.contract


def test_api_exists():
    import toolbox as t
    for n in ["validate_args", "ToolRegistry", "parse_tool_call", "redact", "run_agent"]:
        assert callable(getattr(t, n)), n
    assert "bvn" in t.SENSITIVE_KEYS


def test_accounts_and_tools_deterministic():
    assert w.make_accounts(2) == w.make_accounts(2) and w.make_accounts(2) != w.make_accounts(3)
    tools = w.make_tools(2)
    assert [t["name"] for t in tools] == ["check_balance", "list_transactions", "convert_currency", "get_profile"]
    assert tools[0]["fn"]("NG-1001")["balance"] == w.make_accounts(2)["NG-1001"]["balance"]
    assert all(set(t) == {"name", "schema", "fn", "description"} for t in tools)


def test_mock_models_follow_the_protocol():
    m = w.make_model("balance")
    first = m.next([{"role": "user", "content": "balance?"}])
    assert first == '{"tool": "check_balance", "args": {"account": "NG-1001"}}'
    done = m.next([{"role": "tool", "content": '{"ok": true, "result": {"balance": 4200}}'}])
    assert done.startswith("FINAL:") and "4200" in done
    assert w.make_model("loop").next([]) == w.make_model("loop").next([{"role": "tool", "content": "{}"}])
    assert w.make_model("chatty").next([]).startswith("Sure")
