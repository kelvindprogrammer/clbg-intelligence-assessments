"""Contract tests: pass on the unmodified starter."""
import json

import pytest

import mock_extractor as m

pytestmark = pytest.mark.contract


def test_api_exists():
    import reliable as r
    for n in ["build_prompt", "call_with_retries", "check_record", "extract_record", "run_batch", "choose_config"]:
        assert callable(getattr(r, n)), n
    assert r.DEFAULT_CFG["max_calls"] >= 1


def test_waybills_deterministic_and_small():
    a, b = m.make_waybills(3, 30), m.make_waybills(3, 30)
    assert a == b and set(a[0]) == {"id", "text"} and "WAYBILL" in a[0]["text"]


def test_mock_failure_modes_are_reachable_and_deterministic():
    doc = m.make_waybills(1, 1, injection_rate=0)[0]["text"]
    prompt = f"x\n<<<DOC\n{doc}\nDOC>>>"
    kinds = set()
    for seed in range(40):
        llm = m.MockExtractor(seed=seed, p_timeout=.2, p_ratelimit=.2, p_refuse=.2, p_malformed=.2, p_wrong=.1)
        try:
            out = llm.complete(prompt)
            kinds.add("refuse" if out == m.REFUSAL else "json" if out.endswith("}") else "cut")
        except TimeoutError:
            kinds.add("timeout")
        except m.RateLimitError:
            kinds.add("rate")
    assert kinds == {"refuse", "json", "cut", "timeout", "rate"}


def test_fake_clock_records_sleeps():
    c = m.FakeClock()
    c.sleep(1.5)
    c.sleep(2)
    assert c.now() == 3.5 and c.sleeps == [1.5, 2]
