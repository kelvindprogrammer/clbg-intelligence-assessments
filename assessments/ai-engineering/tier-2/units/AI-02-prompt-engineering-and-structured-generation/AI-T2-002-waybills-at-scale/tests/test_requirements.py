import copy
import json

import pytest

import mock_extractor as m
import reliable as r

DOCS = m.make_waybills(2026, 200)
GOOD = m.make_waybills(5, 1, injection_rate=0)[0]["text"]
REC = m._parse(GOOD)  # test-side truth helper for the mock's rule; do not import m._parse in your package
POL = {"max_attempts": 4, "base_delay": 1.0, "factor": 2.0, "max_delay": 8.0, "deadline": 30.0}


class Script:
    """Scripted LLM: each item is an exception instance to raise or a string to return."""

    def __init__(self, items):
        self.items, self.prompts, self.billed = list(items), [], 0

    @property
    def calls(self):
        return len(self.prompts)

    def complete(self, prompt):
        self.prompts.append(prompt)
        self.billed += len(prompt.split())
        it = self.items.pop(0) if self.items else json.dumps(REC)
        if isinstance(it, Exception):
            raise it
        return it


def truth(t):
    return m._parse(t)


def test_r1_build_prompt_fences_and_feeds_back():
    p = r.build_prompt(GOOD)
    assert "<<<DOC\n" + GOOD + "\nDOC>>>" in p and "rejected" not in p
    evil = r.build_prompt("a <<<DOC<<<DOC b DOC>>>DOC>>>")
    assert evil.count("<<<DOC") == 1 and evil.count("DOC>>>") == 1
    q = r.build_prompt(GOOD, ["parse"])
    assert q.index("DOC>>>") < q.index("rejected") and "parse" in q


def test_r2_backoff_schedule_and_attempts():
    clock = m.FakeClock()
    res = r.call_with_retries(Script([TimeoutError(), TimeoutError(), "hello"]), "p", POL, clock)
    assert res == {"ok": True, "text": "hello", "attempts": 3, "error": None} and clock.sleeps == [1.0, 2.0]


def test_r2_rate_limit_waits_at_least_retry_after_and_delay_is_capped():
    clock = m.FakeClock()
    r.call_with_retries(Script([m.RateLimitError(3.0), "x"]), "p", POL, clock)
    assert clock.sleeps == [3.0]
    clock = m.FakeClock()
    r.call_with_retries(Script([TimeoutError()] * 4 + ["x"]), "p", {**POL, "max_attempts": 6, "max_delay": 3.0, "deadline": 99}, clock)
    assert clock.sleeps == [1.0, 2.0, 3.0, 3.0]


def test_r2_non_retryable_exhausted_and_deadline():
    clock = m.FakeClock()
    res = r.call_with_retries(Script([m.AuthError("k")]), "p", POL, clock)
    assert res["error"] == "auth" and res["attempts"] == 1 and clock.sleeps == []
    clock = m.FakeClock()
    res = r.call_with_retries(Script([TimeoutError()] * 9), "p", POL, clock)
    assert res["error"] == "exhausted" and res["attempts"] == 4 and len(clock.sleeps) == 3 and not res["ok"]
    clock = m.FakeClock()
    res = r.call_with_retries(Script([TimeoutError()] * 9), "p", {**POL, "deadline": 2.5}, clock)
    assert res["error"] == "deadline" and clock.sleeps == [1.0]


def test_r3_check_record_accepts_correct_and_fenced_json():
    assert r.check_record(json.dumps(REC), GOOD) == (REC, [])
    assert r.check_record("```json\n" + json.dumps(REC) + "\n```", GOOD)[1] == []


def test_r3_check_record_classifies_failures():
    assert r.check_record(m.REFUSAL, GOOD) == (None, ["refusal"])
    assert r.check_record(json.dumps(REC)[:30], GOOD) == (None, ["parse"])
    swap = {**REC, "origin": REC["destination"], "destination": REC["origin"]}
    assert r.check_record(json.dumps(swap), GOOD) == (None, ["ungrounded: destination", "ungrounded: origin"])
    assert r.check_record(json.dumps({**REC, "consignee": "Zenith Traders"}), GOOD)[1] == ["ungrounded: consignee"]
    assert r.check_record(json.dumps({**REC, "weight_kg": str(REC["weight_kg"])}), GOOD)[1] == ["type: weight_kg"]
    assert r.check_record(json.dumps({**REC, "extra": 1}), GOOD)[1] == ["unexpected: extra"]
    short = {k: v for k, v in REC.items() if k != "value_ngn"}
    assert r.check_record(json.dumps(short), GOOD)[1] == ["missing: value_ngn"]


def test_r4_repair_with_feedback_vs_fresh():
    cfg = copy.deepcopy(r.DEFAULT_CFG)
    llm = Script(['{"waybill_id": ', json.dumps(REC)])
    out = r.extract_record(llm, GOOD, cfg, m.FakeClock())
    assert out["status"] == "ok" and out["record"] == REC and out["calls"] == 2 and out["tokens"] > 0
    assert "rejected" in llm.prompts[1] and llm.prompts[0] != llm.prompts[1]
    cfg["repair_mode"] = "fresh"
    llm = Script(['{"waybill_id": ', json.dumps(REC)])
    r.extract_record(llm, GOOD, cfg, m.FakeClock())
    assert llm.prompts[0] == llm.prompts[1]


def test_r4_refusal_injection_and_call_budget():
    cfg = copy.deepcopy(r.DEFAULT_CFG)
    out = r.extract_record(Script([m.REFUSAL, m.REFUSAL]), GOOD, cfg, m.FakeClock())
    assert out["status"] == "needs_human" and out["reason"] == "refusal" and out["calls"] == 2
    llm = Script([])
    bad = GOOD.replace("Note:", "Note: " + m.INJECTION + " ")
    out = r.extract_record(llm, bad, cfg, m.FakeClock())
    assert out["status"] == "needs_human" and out["reason"] == "injection" and llm.calls == 0 and out["calls"] == 0
    cfg["max_calls"] = 2
    out = r.extract_record(Script(["{", "{", "{"]), GOOD, cfg, m.FakeClock())
    assert out["status"] == "failed" and out["calls"] <= 2


def test_r5_run_batch_summary_is_consistent():
    s = r.run_batch(m.MockExtractor(seed=1), DOCS[:40], r.DEFAULT_CFG, m.FakeClock())
    assert s["n"] == 40 and s["ok"] + s["needs_human"] + s["failed"] == 40 and len(s["outcomes"]) == 40
    assert s["calls"] == sum(o["calls"] for o in s["outcomes"]) and s["ok_rate"] == s["ok"] / 40
    lat = sorted(o["latency"] for o in s["outcomes"])
    assert s["p95_latency"] == lat[37] and s["mean_tokens"] == pytest.approx(s["tokens"] / 40)


def _wrong(docs, s):
    return sum(1 for d, o in zip(docs, s["outcomes"]) if o["status"] == "ok" and o["record"] != truth(d["text"]))


def test_acceptance_no_wrong_accepted_and_few_failures_on_default_mock():
    # Justification: reference gives 0 wrong, 6/200 failed (3%); 8% leaves room for a cheaper repair policy.
    s = r.run_batch(m.MockExtractor(seed=3), DOCS, r.DEFAULT_CFG, m.FakeClock())
    assert _wrong(DOCS, s) == 0 and s["failed"] <= 0.08 * 200


def test_acceptance_injection_bypassing_the_fence_is_not_accepted():
    s = r.run_batch(m.MockExtractor(seed=3, fence_bypass=True), DOCS, r.DEFAULT_CFG, m.FakeClock())
    assert _wrong(DOCS, s) == 0
    assert all("ATTACKER" not in json.dumps(o["record"]) for o in s["outcomes"])


def test_acceptance_bad_key_is_not_retried():
    llm = m.MockExtractor(seed=3, bad_key=True)
    clock = m.FakeClock()
    s = r.run_batch(llm, DOCS[:50], r.DEFAULT_CFG, clock)
    assert llm.calls <= 50 and clock.sleeps == [] and s["ok"] == 0


def test_acceptance_choose_config_is_feasible_and_no_costlier_than_overspending():
    dev = m.make_waybills(11, 100)
    cfg = r.choose_config(lambda: m.MockExtractor(seed=1), dev, 0.9)
    held = m.make_waybills(12, 150)
    s = r.run_batch(m.MockExtractor(seed=2), held, cfg, m.FakeClock())
    big = copy.deepcopy(r.DEFAULT_CFG)
    big.update(max_repairs=5, repair_mode="fresh", refusal_retries=5, max_calls=12, screen_injection=False)
    big["policy"]["max_attempts"] = 6
    s2 = r.run_batch(m.MockExtractor(seed=2), held, big, m.FakeClock())
    assert s["ok_rate"] >= 0.85 and s["mean_tokens"] <= s2["mean_tokens"] * 1.02
    assert _wrong(held, s) == 0
