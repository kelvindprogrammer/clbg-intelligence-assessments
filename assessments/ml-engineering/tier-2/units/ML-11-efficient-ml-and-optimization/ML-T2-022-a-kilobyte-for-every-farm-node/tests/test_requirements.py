"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, architectures and budgets."""
import numpy as np
import pytest

import datagen
import squeeze as sq


def test_r1_quantize_by_hand():
    W = np.array([[1.0, -0.5], [0.5, 0.25], [-1.0, 0.0]])
    Q, s = sq.quantize_tensor(W, bits=3, per_channel=False)       # qmax = 3, scale = 1/3
    assert np.allclose(s, 1 / 3) and Q.dtype.kind == "i"
    assert Q.tolist() == [[3, -2], [2, 1], [-3, 0]]
    Qc, sc = sq.quantize_tensor(W, bits=3, per_channel=True)       # per output column: max|col| = 1 and 0.5
    assert np.allclose(sc, [1 / 3, 0.5 / 3])
    assert Qc[:, 1].tolist() == [-3, 2, 0]


def test_r1_roundtrip_error_bounded_and_zero_tensor():
    rng = np.random.default_rng(0)
    W = rng.normal(0, 1, (50, 20))
    for bits in (4, 6, 8):
        Q, s = sq.quantize_tensor(W, bits, per_channel=True)
        assert np.abs(Q).max() <= 2 ** (bits - 1) - 1
        assert np.all(np.abs(sq.dequantize(Q, s) - W) <= s / 2 + 1e-12)
    Q, s = sq.quantize_tensor(np.zeros((3, 2)), 4, True)
    assert np.all(Q == 0) and np.all(np.isfinite(s)) and np.all(s > 0)


def test_r2_global_prune_counts_and_order():
    Ws = [np.array([[0.1, -0.9], [0.5, 0.2]]), np.array([[3.0], [-0.05]])]
    out = sq.magnitude_prune(Ws, 0.5)                                # 6 weights -> 3 zeros: 0.05, 0.1, 0.2
    assert [w.tolist() for w in out] == [[[0.0, -0.9], [0.5, 0.0]], [[3.0], [0.0]]]
    assert Ws[0][0, 0] == 0.1                                        # input untouched
    assert sum(int((w == 0).sum()) for w in sq.magnitude_prune(Ws, 0.0)) == 0


def test_r3_storage_model_by_hand():
    # dense: 40 weights * 8 bits = 40 B, + 4 scales * 4 B + 4 biases * 4 B = 72
    assert sq.layer_bytes((10, 4), nnz=40, bits=8, n_scales=4) == 72
    # sparse: 5 nonzeros * (8 + 16) bits = 15 B + 16 + 16 = 47 (cheaper than dense, so it wins)
    assert sq.layer_bytes((10, 4), nnz=5, bits=8, n_scales=4) == 47
    assert sq.layer_bytes((10, 4), nnz=40, bits=4, n_scales=1) == 20 + 4 + 16


@pytest.fixture(scope="module")
def trained():
    return datagen.train_float_model(2026)


def test_r4_meets_budget_and_accuracy(trained):
    Ws, bs, t = trained
    base = sq.accuracy(Ws, bs, t["Xte"], t["yte"])
    m = sq.compress(Ws, bs, t["Xcal"], t["ycal"], budget_ratio=0.20, max_drop=0.025)
    assert m.bytes <= 0.20 * sq.float32_bytes(Ws, bs)
    acc = float((m.predict(t["Xte"]) == t["yte"]).mean())
    assert base - acc <= 0.03, (base, acc, m.config)


def test_r4_bytes_are_honest(trained):
    Ws, bs, t = trained
    m = sq.compress(Ws, bs, t["Xcal"], t["ycal"], 0.20, 0.025)
    assert m.bytes > 0 and isinstance(m.config, dict) and m.config
    # effective weights really are low-precision: few distinct values per column
    assert max(len(np.unique(W[:, 0])) for W in m.Ws) <= 2 ** 8


def test_r4_does_not_use_test_data_or_mutate_inputs(trained):
    Ws, bs, t = trained
    snap = [w.copy() for w in Ws]
    sq.compress(Ws, bs, t["Xcal"], t["ycal"], 0.25, 0.02)
    assert all(np.array_equal(a, b) for a, b in zip(snap, Ws))


def test_r4_tighter_budget_is_respected_or_reported(trained):
    Ws, bs, t = trained
    m = sq.compress(Ws, bs, t["Xcal"], t["ycal"], budget_ratio=0.12, max_drop=0.05)
    assert m.bytes <= 0.12 * sq.float32_bytes(Ws, bs)
