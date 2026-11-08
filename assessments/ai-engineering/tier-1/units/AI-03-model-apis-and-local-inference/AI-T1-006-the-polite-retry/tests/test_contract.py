"""Contract tests: pass on the unmodified starter."""
import pytest

import mockllm

pytestmark = pytest.mark.contract


def test_api_exists():
    import llmclient as lc
    for n in ["backoff_delay", "parse_json_reply", "collect_stream"]:
        assert callable(getattr(lc, n)), n
    for n in ["ResilientClient", "CostLedger", "RetriesExhausted", "MalformedReply"]:
        assert isinstance(getattr(lc, n), type), n


def test_mock_provider_is_deterministic_and_scripted():
    def run():
        p = mockllm.MockProvider(script=["ok", "malformed"])
        return [p.complete("abc def").text, p.complete("abc def").text, p.complete("abc def").text]
    a = run()
    assert a == run() and a[0] == a[2] and a[1] != a[0]


def test_mock_errors_and_virtual_clock():
    clk = mockllm.VirtualClock()
    p = mockllm.MockProvider(script=["rate:3", "bad"], clock=clk)
    with pytest.raises(mockllm.RateLimitError) as e:
        p.complete("x")
    assert e.value.retry_after == 3
    with pytest.raises(mockllm.BadRequestError):
        p.complete("x")
    clk.sleep(2)
    assert clk.now() > 2 and clk.sleeps == [2]
