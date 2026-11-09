import pytest

import chat_mock as cm
import ctxbudget as c

SYS = "Be brief."  # 3 tokens + 4 overhead = 7


def msgs(n, words=6, pin=()):
    return [{"id": i, "role": "user", "text": " ".join(["w"] * words), "pin": i in pin} for i in range(n)]


def test_r1_token_rule():
    assert c.count_tokens("") == 0
    assert c.count_tokens("Hello, world!") == 4
    assert c.count_tokens("NGN 15,000 ok?") == 6
    assert c.count_tokens("naïve  café") == 2


def test_r2_message_cost_adds_overhead():
    assert c.message_cost({"id": 0, "role": "user", "text": "a b c", "pin": False}) == 7


def test_r3_keeps_newest_contiguous_run():
    r = c.fit_window(SYS, msgs(5), 60, 10)
    assert r == {"kept": [1, 2, 3, 4], "dropped": [0], "used": 47}


def test_r3_pinned_messages_survive_and_cost_budget():
    r = c.fit_window(SYS, msgs(5, pin={0}), 60, 10)
    assert r["kept"] == [0, 2, 3, 4] and r["dropped"] == [1] and r["used"] == 47


def test_r3_stops_at_first_message_that_does_not_fit_no_holes():
    ms = msgs(3)
    ms[1]["text"] = " ".join(["w"] * 30)
    r = c.fit_window(SYS, ms, 37, 10)  # available 20: message 2 fits (10), message 1 (34) does not, so 0 is not reached
    assert r["kept"] == [2] and r["dropped"] == [0, 1]


def test_r3_errors_are_explicit():
    with pytest.raises(ValueError, match="system_too_large"):
        c.fit_window(SYS, msgs(1), 10, 5)
    with pytest.raises(ValueError, match="pinned_overflow"):
        c.fit_window(SYS, msgs(3, pin={0, 1, 2}), 40, 10)


def test_r3_does_not_mutate_input():
    ms = msgs(5)
    before = [dict(m) for m in ms]
    c.fit_window(SYS, ms, 60, 10)
    assert ms == before


def test_r4_noop_when_everything_fits():
    ms = msgs(3)
    r = c.compact(SYS, ms, 200, 10, cm.ExtractiveSummariser())
    assert [m["id"] for m in r["messages"]] == [0, 1, 2] and r["summarised"] == [] and r["used"] == 7 + 30


def test_r4_summary_replaces_dropped_history_inside_budget():
    conv = cm.make_conversation(7, 30)
    system = "You are a careful bank support assistant."
    r = c.compact(system, conv["messages"], 260, 40, cm.ExtractiveSummariser())
    assert r["messages"][0]["id"] == "summary" and r["messages"][0]["text"].startswith("[summary] ")
    assert r["summarised"] and r["summarised"][0] == 0 and r["used"] <= 260 - 40
    assert r["used"] == c.count_tokens(system) + 4 + sum(c.message_cost(m) for m in r["messages"])
    assert all(m["id"] != 0 for m in r["messages"][1:])


def test_r5_facts_retained_is_a_fraction():
    ctx = [{"id": 0, "role": "user", "text": "Account ends with 4821.", "pin": False}]
    assert c.facts_retained(ctx, ["4821", "15000", "ends"]) == pytest.approx(2 / 3)
    assert c.facts_retained(ctx, []) == 1.0
    assert c.facts_retained([], ["x"]) == 0.0


def test_r5_truncation_forgets_but_summary_and_pin_remember():
    conv = cm.make_conversation(7, 30)
    system = "You are a careful bank support assistant."
    trunc = c.fit_window(system, conv["messages"], 260, 40)
    kept = [m for m in conv["messages"] if m["id"] in trunc["kept"]]
    assert c.facts_retained(kept, conv["facts"]) == 0.0
    summ = c.compact(system, conv["messages"], 260, 40, cm.ExtractiveSummariser())
    assert 0.0 < c.facts_retained(summ["messages"], conv["facts"]) < 1.0
    pinned = [dict(m, pin=(m["id"] == 0)) for m in conv["messages"]]
    p = c.fit_window(system, pinned, 260, 40)
    assert c.facts_retained([m for m in pinned if m["id"] in p["kept"]], conv["facts"]) == 1.0


def test_r6_budget_report_sections():
    r = c.budget_report(SYS, msgs(5, pin={0}), 100, 10)
    assert r == {"system": 7, "pinned": 10, "history": 40, "reserve": 10, "free": 33, "over_by": 0}
    r = c.budget_report(SYS, msgs(5), 50, 10)
    assert r["free"] == -17 and r["over_by"] == 17
