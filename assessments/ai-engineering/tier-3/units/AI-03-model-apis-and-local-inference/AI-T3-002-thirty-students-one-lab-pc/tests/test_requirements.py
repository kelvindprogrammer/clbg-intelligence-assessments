"""Public requirement tests (FAIL on the starter). Hidden tests use other models, workloads and hardware."""
import itertools

import numpy as np
import pytest

import servelab as sl
import toylm

CM = toylm.CostModel()


@pytest.fixture(scope="module")
def world():
    model = toylm.make_model(1)
    tok = toylm.sample_tokens(model, 3000, 11)
    return model, tok, toylm.make_workload(0, 200, 0.5)


@pytest.mark.parametrize("bits", [8, 4])
@pytest.mark.parametrize("axis,group", [(None, None), (0, None), (1, None), (1, 4), (0, 2)])
def test_r1_error_bound_range_and_scale_count(bits, axis, group):
    w = np.random.default_rng(0).normal(size=(6, 8))
    qt = sl.quantize(w, bits, axis, group)
    qmax = 2 ** (bits - 1) - 1
    assert np.abs(qt.q).max() <= qmax
    err = np.abs(sl.dequantize(qt) - w)
    assert err.shape == w.shape and err.max() <= np.abs(w).max() / qmax / 2 + 1e-12
    blocks = {(None, None): 1, (0, None): 8, (1, None): 6, (1, 4): 12, (0, 2): 24}[(axis, group)]
    assert qt.scale.size == blocks


def test_r1_exact_on_grid_and_zero_safe():
    w = np.arange(-7, 8, dtype=float).reshape(3, 5)
    assert np.array_equal(sl.dequantize(sl.quantize(w, 4)), w)
    z = np.zeros((4, 4))
    assert np.array_equal(sl.dequantize(sl.quantize(z, 4, 1, 2)), z)


def test_r1_bad_arguments():
    with pytest.raises(ValueError):
        sl.quantize(np.ones((4, 6)), 4, axis=1, group=4)
    with pytest.raises(ValueError):
        sl.quantize(np.ones((4, 6)), 4, axis=None, group=2)


def test_r1_storage_bytes():
    w = np.random.default_rng(1).normal(size=(6, 8))
    assert sl.qbytes(sl.quantize(w, 4)) == 24 + 2
    assert sl.qbytes(sl.quantize(w, 4, 1, 4)) == 24 + 2 * 12
    assert sl.qbytes(sl.quantize(w, 8, 0)) == 48 + 2 * 8


def test_r2_fp16_passthrough_and_int_sizes(world):
    model, tok, _ = world
    A, B, nb = sl.quantize_model(model, 16, "tensor")
    assert np.array_equal(A, model["A"]) and nb == (A.size + B.size) * 2
    assert sl.quantize_model(model, 8, "channel")[2] < nb / 1.8 and sl.quantize_model(model, 4, "channel")[2] < nb / 3.4
    assert sl.ppl_ratio(model, 16, "tensor", tok) == pytest.approx(1.0)


def test_r2_outliers_break_per_tensor_int4_but_not_per_channel(world):
    model, tok, _ = world
    tensor4 = sl.ppl_ratio(model, 4, "tensor", tok)
    channel4 = sl.ppl_ratio(model, 4, "channel", tok)
    group4 = sl.ppl_ratio(model, 4, "group4", tok)
    assert tensor4 > 1.5 and channel4 < 1.05 and channel4 < group4 < tensor4
    assert sl.ppl_ratio(model, 8, "channel", tok) < 1.01


def test_r3_static_single_request_exact():
    r = sl.simulate([(2.0, 100, 10)], "static", 4, 0.0, 16, CM)
    assert r.latencies == pytest.approx([100 * 0.003 + 10 * CM.step_s(1, 16)])
    assert r.makespan == pytest.approx(r.latencies[0]) and r.throughput_tok_s == pytest.approx(10 / r.makespan)


def test_r3_static_batch_forms_when_full_or_after_wait():
    reqs = [(0.0, 100, 4), (0.1, 50, 8), (0.2, 80, 2), (50.0, 10, 3)]
    r = sl.simulate(reqs, "static", 3, 5.0, 8, CM)
    end = 0.2 + (100 + 50 + 80) * 0.003 + 8 * CM.step_s(3, 8)           # full at the 3rd arrival
    assert r.latencies[:3] == pytest.approx([end - 0.0, end - 0.1, end - 0.2])
    assert r.latencies[3] == pytest.approx(5.0 + 10 * 0.003 + 3 * CM.step_s(1, 8))   # waits max_wait, runs alone


def test_r3_continuous_request_joins_mid_flight():
    reqs = [(0.0, 100, 3), (0.1, 50, 2)]
    r = sl.simulate(reqs, "continuous", 4, 0.0, 8, CM)
    assert r.latencies == pytest.approx([0.65, 0.55])


def test_r3_input_order_is_preserved_and_unsorted_input_works():
    reqs = [(5.0, 20, 5), (0.0, 20, 5), (2.0, 20, 5)]
    a = sl.simulate(reqs, "continuous", 2, 0.0, 8, CM)
    b = sl.simulate(sorted(reqs), "continuous", 2, 0.0, 8, CM)
    assert a.latencies[1] == pytest.approx(b.latencies[0]) and a.latencies[0] == pytest.approx(b.latencies[2])


def test_r3_memory_limit_and_policy_names():
    with pytest.raises(ValueError):
        sl.simulate([(0.0, 10, 5)], "static", 16, 0.0, 16, CM)
    with pytest.raises(ValueError):
        sl.simulate([(0.0, 10, 5)], "magic", 2, 0.0, 8, CM)


def test_r3_continuous_beats_static_tail_under_load(world):
    _, _, wl = world
    s = sl.simulate(wl, "static", 8, 0.2, 8, CM)
    c = sl.simulate(wl, "continuous", 8, 0.0, 8, CM)
    assert c.p95 < 0.5 * s.p95 and c.throughput_tok_s >= 0.95 * s.throughput_tok_s


def test_r4_capacity_multiplier(world):
    _, _, wl = world
    cfg = dict(bits=8, scheme="channel", policy="continuous", max_batch=8, max_wait_s=0.0)
    assert sl.max_load_multiplier(wl, cfg, CM, 1e6) == 12
    assert sl.max_load_multiplier(wl, cfg, CM, 0.5) == 0
    mid = sl.max_load_multiplier(wl, cfg, CM, 12.0)
    assert 1 <= mid < 12


def test_r5_recommendation_is_feasible_and_best_on_its_own_grid(world):
    model, tok, wl = world
    slo, cap = 10.0, 1.03
    rec = sl.recommend(model, wl, CM, slo, cap, tok)
    assert rec["p95_s"] <= slo and rec["ppl_ratio"] <= cap and rec["memory_gb"] <= CM.mem_cap_gb
    # independent brute force over a coarse grid using your own simulate / ppl_ratio / capacity functions
    best = 0
    for bits, scheme, pol, mb in itertools.product((16, 8, 4), ("tensor", "channel", "group8"), ("static", "continuous"), (2, 4, 8)):
        if CM.memory_gb(mb, bits) > CM.mem_cap_gb or (bits == 16 and scheme != "tensor"):
            continue
        if bits != 16 and sl.ppl_ratio(model, bits, scheme, tok) > cap:
            continue
        cfg = dict(bits=bits, scheme=scheme, policy=pol, max_batch=mb, max_wait_s=0.0)
        if sl.simulate(wl, pol, mb, 0.0, bits, CM).p95 <= slo:
            best = max(best, sl.max_load_multiplier(wl, cfg, CM, slo))
    assert rec["capacity"] >= best > 0
