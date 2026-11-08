"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, limits, prices and outages."""
import math

import pytest

import gateway as gw
import mockllm as m
import waybills as w


def world(seed=2026, n=600):
    texts, labels = w.make_waybills(n, seed)
    dev_t, dev_l = w.make_waybills(200, seed + 1000)
    truth = {m.norm(t): l for t, l in list(zip(texts, labels)) + list(zip(dev_t, dev_l))}
    return texts, labels, dev_t, dev_l, truth


def fleet(truth, outage=(80, 170), seed=0):
    clk = m.VirtualClock()
    a = m.MockProvider("fastcheap", truth, clk, rpm=20, tpm=2500, price_in=20, price_out=60,
                       outages=[outage] if outage else [], seed=seed)
    b = m.MockProvider("steady", truth, clk, rpm=60, tpm=20000, price_in=80, price_out=240, base_s=2.5,
                       acc=0.995, decay=0.01, malformed_rate=0.01, seed=seed)
    return clk, a, b


def naive(texts, truth):
    clk, a, _ = fleet(truth)
    for t in texts:
        while True:
            try:
                a.complete(m.build_prompt([t]))
                break
            except m.RateLimitError as e:
                clk.sleep(e.retry_after)
            except m.ServerError:
                clk.sleep(5)
    return a.billed_kobo, clk.now()


def test_r1_normalise_key():
    assert gw.normalise_key("  URGENT:  Cement   Bags!! ") == "urgent: cement bags"
    assert gw.normalise_key("Yam Tubers .") == "yam tubers" == m.norm("yam  tubers!")
    assert gw.normalise_key("...") == ""


def test_r2_plan_batches_dedupes_in_first_seen_order():
    texts = ["B x", "a  y.", "b X!", "c", "A Y", "d", "e"]
    assert gw.plan_batches(texts, 2) == [["b x", "a y"], ["c", "d"], ["e"]]
    assert gw.plan_batches([], 3) == [] and gw.plan_batches(["q"], 1) == [["q"]]


def test_r3_limiter_request_window():
    clk = m.VirtualClock()
    lim = gw.RateLimiter(3, 10_000, clk)
    for _ in range(3):
        assert lim.wait_time(5) == 0
        lim.commit(5)
    assert lim.wait_time(5) == pytest.approx(60)
    clk.sleep(30)
    assert lim.wait_time(5) == pytest.approx(30)
    clk.sleep(30)
    assert lim.wait_time(5) == 0


def test_r3_limiter_token_window_uses_oldest_events_first():
    clk = m.VirtualClock()
    lim = gw.RateLimiter(100, 100, clk)
    lim.commit(60)
    clk.sleep(10)
    lim.commit(30)
    assert lim.wait_time(10) == 0
    assert lim.wait_time(50) == pytest.approx(50)     # needs the 60-token event (sent at t=0) to expire
    assert lim.wait_time(80) == pytest.approx(60)    # needs both earlier events gone
    with pytest.raises(ValueError):
        lim.wait_time(101)


def test_r3_acquire_sleeps_then_commits():
    clk = m.VirtualClock()
    lim = gw.RateLimiter(1, 100, clk)
    lim.acquire(10)
    lim.acquire(10)
    assert clk.now() == pytest.approx(60)
    assert lim.wait_time(10) == pytest.approx(60)


def test_r4_labels_in_order_valid_and_deduplicated():
    texts, labels, *_, truth = world(1, 120)
    clk = m.VirtualClock()
    p = m.MockProvider("p", truth, clk, rpm=60, tpm=20000, acc=1.0, decay=0, malformed_rate=0)
    g = gw.Gateway([p], clk, batch_size=4)
    out = g.classify_all(texts)
    uniq = len({m.norm(t) for t in texts})
    assert out == labels
    assert p.n_calls == math.ceil(uniq / 4) and g.stats.cache_hits == len(texts) - uniq


def test_r4_cache_persists_between_calls():
    texts, labels, *_, truth = world(2, 60)
    clk = m.VirtualClock()
    p = m.MockProvider("p", truth, clk, rpm=60, tpm=20000)
    g = gw.Gateway([p], clk, batch_size=5)
    g.classify_all(texts)
    calls = p.n_calls
    g.classify_all(texts[::-1])
    assert p.n_calls == calls and g.stats.cache_hits >= len(texts)


def test_r4_never_triggers_a_rate_limit():
    texts, labels, *_, truth = world(3, 200)
    clk = m.VirtualClock()
    p = m.MockProvider("p", truth, clk, rpm=5, tpm=400)
    g = gw.Gateway([p], clk, batch_size=2)
    g.classify_all(texts)
    assert p.violations == 0 and g.stats.makespan_s > 60


def test_r4_survives_malformed_replies():
    texts, labels, *_, truth = world(4, 150)
    clk = m.VirtualClock()
    p = m.MockProvider("p", truth, clk, rpm=60, tpm=20000, malformed_rate=0.35, acc=1.0, decay=0)
    out = gw.Gateway([p], clk, batch_size=6).classify_all(texts)
    assert out == labels


def test_r4_fails_over_during_outage_and_returns_to_primary():
    texts, labels, *_, truth = world(5, 600)
    clk, a, b = fleet(truth, outage=(0, 50))
    g = gw.Gateway([a, b], clk, batch_size=5, cooldown=20)
    out = g.classify_all(texts)
    assert len(out) == len(texts) and g.stats.calls["steady"] > 0 and g.stats.calls["fastcheap"] > 0
    assert a.violations == 0 and b.violations == 0


def test_r4_all_providers_down_waits_instead_of_crashing():
    texts, labels, *_, truth = world(6, 40)
    clk = m.VirtualClock()
    a = m.MockProvider("a", truth, clk, outages=[(0, 100)])
    b = m.MockProvider("b", truth, clk, outages=[(0, 100)])
    out = gw.Gateway([a, b], clk, batch_size=5, cooldown=15).classify_all(texts)
    assert len(out) == 40 and clk.now() >= 100


def test_r5_budget_stops_spending():
    texts, labels, *_, truth = world(7, 300)
    clk, a, b = fleet(truth, outage=None)
    g = gw.Gateway([a, b], clk, batch_size=5, budget_kobo=20.0)
    with pytest.raises(gw.BudgetExceeded):
        g.classify_all(texts)
    assert 20.0 <= g.stats.cost_kobo < 20.0 + 6
    assert g.stats.cost_kobo == pytest.approx(a.billed_kobo + b.billed_kobo)


def test_r6_choose_batch_size_is_cheap_and_accurate():
    texts, labels, dev_t, dev_l, truth = world(8)

    def make():
        return m.MockProvider("p", truth, m.VirtualClock(), rpm=20, tpm=2500)
    k = gw.choose_batch_size(make, dev_t, dev_l, min_accuracy=0.96)
    probe = make()
    mean_acc = sum(probe._p_correct(i) for i in range(k)) / k
    assert 4 <= k <= 12 and mean_acc >= 0.90


def test_end_to_end_beats_the_naive_loop():
    texts, labels, dev_t, dev_l, truth = world(2026)
    k = gw.choose_batch_size(lambda: m.MockProvider("fastcheap", truth, m.VirtualClock(), rpm=20, tpm=2500), dev_t, dev_l)
    clk, a, b = fleet(truth)
    g = gw.Gateway([a, b], clk, batch_size=k)
    out = g.classify_all(texts)
    acc = sum(x == y for x, y in zip(out, labels)) / len(labels)
    n_cost, n_time = naive(texts, truth)
    assert acc >= 0.95 and a.violations == b.violations == 0
    assert g.stats.cost_kobo <= 0.6 * n_cost and g.stats.makespan_s <= 0.25 * n_time
    assert g.stats.cost_kobo == pytest.approx(a.billed_kobo + b.billed_kobo)
