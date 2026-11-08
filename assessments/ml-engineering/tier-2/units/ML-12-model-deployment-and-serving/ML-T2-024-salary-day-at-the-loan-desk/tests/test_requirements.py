"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, traffic levels and SLOs."""
import numpy as np
import pytest

import datagen
import servesim as ss


def test_r1_exact_on_clean_data_and_robust_to_spikes():
    sizes = np.array([1, 2, 4, 8, 16, 32])
    a, b = ss.calibrate_cost(sizes, 10 + 0.5 * sizes)
    assert a == pytest.approx(10) and b == pytest.approx(0.5)
    for seed in (1, 2, 3):
        s, t, (ta, tb) = datagen.make_timings(seed)
        a, b = ss.calibrate_cost(s, t)
        assert abs(a - ta) / ta < 0.10 and abs(b - tb) / tb < 0.10, (seed, a, b, ta, tb)


def test_r2_hand_trace_batch_fills_before_timeout():
    r = ss.simulate([0.0, 1.0, 2.0, 3.0], ss.Policy(2, 10.0, 10), (5.0, 1.0))
    assert np.allclose(r["latency"], [8.0, 7.0, 13.0, 12.0])
    assert [m for _, m, _ in r["batches"]] == [2, 2] and not np.any(r["shed"])


def test_r2_timeout_dispatches_partial_batch():
    r = ss.simulate([0.0, 50.0], ss.Policy(4, 10.0, 10), (5.0, 1.0))      # each waits 10 ms, then serves alone
    assert np.allclose(r["latency"], [16.0, 16.0]) and [m for _, m, _ in r["batches"]] == [1, 1]


def test_r2_load_shedding_when_queue_is_full():
    r = ss.simulate([0.0, 0.1, 0.2], ss.Policy(1, 0.0, 1), (5.0, 0.0))
    assert r["shed"].tolist() == [False, False, True]
    assert np.allclose(r["latency"][:2], [5.0, 9.9]) and np.isnan(r["latency"][2])


def test_r2_busy_server_lets_batches_grow():
    arr = np.arange(0.0, 40.0, 1.0)                                          # 1 request per ms, batch of 1 takes 6 ms
    r = ss.simulate(arr, ss.Policy(32, 0.0, 100), (5.0, 1.0))
    sizes = [m for _, m, _ in r["batches"]]
    assert sizes[0] == 1 and max(sizes) > 5 and sum(sizes) == 40


def test_r3_summarize_by_hand():
    res = {"latency": np.array([10.0, 20.0, np.nan, 30.0]), "shed": np.array([False, False, True, False]),
           "batches": [(0.0, 2, 10.0), (20.0, 1, 10.0)], "arrivals": np.array([0.0, 1.0, 2.0, 20.0])}
    m = ss.summarize(res, 25.0)
    assert m["p50"] == 20.0 and m["p99"] == 30.0 and m["shed_rate"] == pytest.approx(0.25)
    assert m["mean_batch"] == pytest.approx(1.5) and m["slo_ok"] is False


@pytest.fixture(scope="module")
def tuned():
    s, t, truth = datagen.make_timings(2026)
    cost = ss.calibrate_cost(s, t)
    pol = ss.tune_policy(datagen.make_arrivals(2026), cost)
    return pol, truth


def test_r4_policy_generalises_to_fresh_traffic(tuned):
    pol, truth = tuned
    for seed in (31, 32):
        m = ss.summarize(ss.simulate(datagen.make_arrivals(seed), pol, truth), datagen.SLO_MS)
        assert m["p99"] <= datagen.SLO_MS and m["shed_rate"] <= 0.01, (pol, m)


def test_r4_policy_survives_a_25_percent_bigger_surge(tuned):
    pol, truth = tuned
    m = ss.summarize(ss.simulate(datagen.make_arrivals(33, surge=1.25), pol, truth), datagen.SLO_MS)
    assert m["p99"] <= datagen.SLO_MS and m["shed_rate"] <= 0.02, (pol, m)


def test_r4_naive_policies_fail_so_the_task_is_real():
    s, t, truth = datagen.make_timings(2026)
    arr = datagen.make_arrivals(2026)
    one = ss.summarize(ss.simulate(arr, ss.Policy(1, 0.0, 10_000), truth), datagen.SLO_MS)
    slow = ss.summarize(ss.simulate(arr, ss.Policy(64, 200.0, 10_000), truth), datagen.SLO_MS)
    assert not one["slo_ok"] and not slow["slo_ok"]
