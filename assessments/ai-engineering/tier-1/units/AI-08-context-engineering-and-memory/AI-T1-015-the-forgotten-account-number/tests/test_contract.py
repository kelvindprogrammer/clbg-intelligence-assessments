"""Contract tests: pass on the unmodified starter."""
import pytest

import chat_mock as cm

pytestmark = pytest.mark.contract


def test_api_exists():
    import ctxbudget as c
    for n in ["count_tokens", "message_cost", "fit_window", "compact", "facts_retained", "budget_report"]:
        assert callable(getattr(c, n)), n


def test_conversation_is_deterministic_and_contains_its_facts():
    a, b = cm.make_conversation(3, 20), cm.make_conversation(3, 20)
    assert a == b and len(a["messages"]) == 20 and len(a["facts"]) == 3
    assert all(f in a["messages"][0]["text"] for f in a["facts"])


def test_summariser_is_lossy_and_bounded():
    s = cm.ExtractiveSummariser().summarise(["Hello there. Second sentence.", "Ok. More."], 4)
    assert s == "Hello there. Ok." or len(s.split()) <= 4
    assert "Second" not in s
