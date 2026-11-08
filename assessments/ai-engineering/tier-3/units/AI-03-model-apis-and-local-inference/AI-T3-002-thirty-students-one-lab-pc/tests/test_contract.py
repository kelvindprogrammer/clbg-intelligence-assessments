"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import toylm

pytestmark = pytest.mark.contract


def test_api_exists():
    import servelab as s
    for n in ["quantize", "dequantize", "qbytes", "quantize_model", "ppl_ratio", "simulate", "max_load_multiplier", "recommend"]:
        assert callable(getattr(s, n)), n


def test_model_is_deterministic_and_outliers_preserve_the_function():
    a, b = toylm.make_model(3), toylm.make_model(3)
    assert np.array_equal(a["A"], b["A"]) and a["outliers"] == b["outliers"]
    tok = toylm.sample_tokens(a, 1500, 4)
    flat = toylm.make_model(3, outlier_channels=0)
    p1, p2 = toylm.perplexity(a["A"], a["B"], tok), toylm.perplexity(flat["A"], flat["B"], tok)
    assert abs(p1 - p2) / p2 < 1e-6 and 1 < p1 < 48
    assert np.abs(a["A"]).max() > 10 * np.abs(flat["A"]).max()


def test_cost_model_and_workload():
    cm = toylm.CostModel()
    assert cm.weight_gb(16) == pytest.approx(6.0) and cm.memory_gb(8, 16) == pytest.approx(8.0)
    assert cm.step_s(1, 8) == pytest.approx(3 / 50 + 0.004)
    w1, w2 = toylm.make_workload(5, 50, 0.4), toylm.make_workload(5, 50, 0.4)
    assert w1 == w2 and all(w1[i][0] <= w1[i + 1][0] for i in range(49))
