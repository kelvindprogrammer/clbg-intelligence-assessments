"""Public requirement tests (FAIL on the starter). Hidden tests use other scripts, seeds and prices."""
import random

import pytest

import llmclient as lc
import mockllm as m


class Half:
    def random(self):
        return 0.5


def make(script, **kw):
    clk = m.VirtualClock()
    prov = m.MockProvider(script=script, clock=clk)
    ledger = lc.CostLedger(30, 90)
    return lc.ResilientClient(prov, clk, ledger=ledger, **kw), prov, clk, ledger


def test_r1_backoff_values_and_cap():
    assert lc.backoff_delay(0, 1.0, 30.0, Half()) == 0.5
    assert lc.backoff_delay(3, 1.0, 30.0, Half()) == 4.0
    assert lc.backoff_delay(10, 1.0, 30.0, Half()) == 15.0


def test_r2_parse_plain_and_fenced():
    assert lc.parse_json_reply(' {"a": 1} ') == {"a": 1}
    assert lc.parse_json_reply('```json\n{"a": 1}\n```') == {"a": 1}
    assert lc.parse_json_reply('```\n{"a": [2]}\n```') == {"a": [2]}


@pytest.mark.parametrize("bad", ['{"a": 1', "hello", "[1, 2]", "", "```json\n```"])
def test_r2_parse_rejects(bad):
    with pytest.raises(lc.MalformedReply):
        lc.parse_json_reply(bad)
    assert issubclass(lc.MalformedReply, ValueError)


def test_r3_happy_path_no_sleep():
    c, prov, clk, led = make([])
    r = c.complete("my transfer failed")
    assert r.attempts == 1 and "intent" in r.data and clk.sleeps == [] and led.calls == 1


def test_r3_retries_use_seeded_full_jitter():
    c, prov, clk, led = make(["timeout", "server", "ok"], seed=7)
    r = c.complete("hello world")
    rng = random.Random(7)
    expect = [rng.random() * min(30.0, 0.5 * 2 ** i) for i in range(2)]
    assert r.attempts == 3 and clk.sleeps == pytest.approx(expect)


def test_r3_rate_limit_honours_retry_after():
    c, prov, clk, led = make(["rate:7", "rate:0.01", "ok"], seed=1)
    c.complete("x y")
    rng = random.Random(1)
    d0, d1 = rng.random() * 0.5, rng.random() * 1.0
    assert clk.sleeps == pytest.approx([max(7, d0), max(0.01, d1)])
    assert clk.sleeps[0] >= 7


def test_r3_bad_request_is_not_retried():
    c, prov, clk, led = make(["bad", "ok"])
    with pytest.raises(m.BadRequestError):
        c.complete("x")
    assert len(prov.calls) == 1 and clk.sleeps == []


def test_r3_exhaustion_reports_attempts_and_does_not_sleep_after_last():
    c, prov, clk, led = make(["timeout"] * 9, max_attempts=4)
    with pytest.raises(lc.RetriesExhausted) as e:
        c.complete("x")
    assert e.value.attempts == 4 and isinstance(e.value.last_error, m.ProviderTimeout)
    assert len(prov.calls) == 4 and len(clk.sleeps) == 3


def test_r3_malformed_is_retried_and_fence_is_not():
    c, prov, clk, led = make(["fence"])
    assert c.complete("x").attempts == 1
    c, prov, clk, led = make(["malformed", "ok"])
    assert c.complete("x").attempts == 2 and len(clk.sleeps) == 1


def test_r4_stream_complete_and_interrupted():
    prov = m.MockProvider(script=["ok", "cut"])
    full = lc.collect_stream(prov.complete("a b", stream=True))
    assert full.complete and full.text.startswith("{") and full.text.endswith("}")
    part = lc.collect_stream(prov.complete("a b", stream=True))
    assert not part.complete and 0 < len(part.text) < len(full.text)
    assert lc.collect_stream(iter([])) == lc.StreamResult("", True)


def test_r5_ledger_arithmetic():
    led = lc.CostLedger(30, 90)
    led.record(m.Response("t", 1000, 500))
    led.record(m.Response("t", 200, 100))
    assert (led.prompt_tokens, led.completion_tokens, led.calls) == (1200, 600, 2)
    assert led.cost_kobo == pytest.approx((1200 * 30 + 600 * 90) / 1000)


def test_r5_only_delivered_responses_are_billed_including_malformed():
    c, prov, clk, led = make(["server", "timeout", "malformed", "ok"], max_attempts=6)
    c.complete("one two three")
    assert led.calls == 2 and led.prompt_tokens == 6


def test_r3_same_seed_same_waits_different_seed_differs():
    runs = []
    for seed in (3, 3, 4):
        c, prov, clk, led = make(["timeout"] * 3 + ["ok"], seed=seed)
        c.complete("x")
        runs.append(clk.sleeps)
    assert runs[0] == runs[1] != runs[2]
