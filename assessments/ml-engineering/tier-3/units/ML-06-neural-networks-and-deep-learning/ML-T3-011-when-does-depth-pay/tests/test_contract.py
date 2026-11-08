import hashlib

import numpy as np
import pytest

pytestmark = pytest.mark.contract


def test_task_generator_is_deterministic_and_unmodified():
    from regimes import KINDS, make_task
    assert KINDS == ("smooth", "axis", "rotated")
    X, y = make_task("smooth", 300, 7)
    X2, y2 = make_task("smooth", 300, 7)
    assert X.shape == (300, 12) and np.array_equal(X, X2) and np.array_equal(y, y2)
    digest = hashlib.sha256(np.round(X, 8).tobytes() + y.tobytes()).hexdigest()
    assert digest == "3e700bc02a291d207392c0a5e2df29a35b59e6bf23791aa561aec742ee8393e1"
    assert 0.2 < y.mean() < 0.8


def test_api_exists():
    import regimes
    for n in ["fit_predict", "run_study", "paired_summary", "crossover", "MLP", "make_task"]:
        assert callable(getattr(regimes, n)), n


def test_all_kinds_generate():
    from regimes import KINDS, make_task
    for k in KINDS:
        X, y = make_task(k, 100, 1, n_noise=3)
        assert X.shape == (100, 9) and set(y) == {0, 1}
