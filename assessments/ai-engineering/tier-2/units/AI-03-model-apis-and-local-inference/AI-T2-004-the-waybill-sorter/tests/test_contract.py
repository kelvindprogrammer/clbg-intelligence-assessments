"""Contract tests: pass on the unmodified starter."""
import pytest

import mockllm as m
import waybills as w

pytestmark = pytest.mark.contract


def test_api_exists():
    import gateway as g
    for n in ["normalise_key", "plan_batches", "choose_batch_size"]:
        assert callable(getattr(g, n)), n
    for n in ["RateLimiter", "Gateway", "BudgetExceeded"]:
        assert isinstance(getattr(g, n), type), n


def test_generator_deterministic_with_duplicates():
    a, b = w.make_waybills(300, 3), w.make_waybills(300, 3)
    assert a == b and len(a[0]) == 300
    uniq = {m.norm(t) for t in a[0]}
    assert 150 < len(uniq) < 260
    by = {}
    for t, l in zip(*a):
        assert by.setdefault(m.norm(t), l) == l


def test_mock_enforces_sliding_window_and_outage():
    clk = m.VirtualClock()
    p = m.MockProvider("p", {}, clk, rpm=2, tpm=10_000, outages=[(100, 110)], malformed_rate=0)
    p.complete(m.build_prompt(["a"]))
    p.complete(m.build_prompt(["a"]))
    with pytest.raises(m.RateLimitError) as e:
        p.complete(m.build_prompt(["a"]))
    assert p.violations == 1 and e.value.retry_after > 50
    clk.sleep(e.value.retry_after)
    p.complete(m.build_prompt(["a"]))
    clk.t = 101
    with pytest.raises(m.ServerError):
        p.complete(m.build_prompt(["a"]))
