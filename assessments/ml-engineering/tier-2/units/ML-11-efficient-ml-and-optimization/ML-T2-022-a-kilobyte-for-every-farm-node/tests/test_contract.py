"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import squeeze as sq
    for n in ["quantize_tensor", "dequantize", "magnitude_prune", "layer_bytes", "compress", "forward", "accuracy"]:
        assert callable(getattr(sq, n)), n


def test_datagen_deterministic_and_learnable():
    a, b = datagen.make_task(3, 200, 50, 50), datagen.make_task(3, 200, 50, 50)
    assert all(np.array_equal(a[k], b[k]) for k in a)
    Ws, bs, task = datagen.train_float_model(2026)
    import squeeze as sq
    assert [w.shape for w in Ws] == [(24, 64), (64, 32), (32, 4)]
    assert sq.accuracy(Ws, bs, task["Xte"], task["yte"]) > 0.80
    assert sq.float32_bytes(Ws, bs) == 4 * (24 * 64 + 64 * 32 + 32 * 4 + 64 + 32 + 4)
