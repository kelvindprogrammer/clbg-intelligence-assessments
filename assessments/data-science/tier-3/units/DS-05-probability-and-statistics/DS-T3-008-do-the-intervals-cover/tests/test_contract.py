"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.contract
DGP_SHA256 = "28b186966694ff1b66242d8182f536d84d626602298443eb78f363971c0a769b"


def test_dgp_unmodified():
    import coverage_lab.dgp as dgp
    assert hashlib.sha256(Path(dgp.__file__).read_bytes()).hexdigest() == DGP_SHA256, "dgp.py was modified"


def test_simulate_shapes_and_truth():
    from coverage_lab import simulate, true_mean
    y, c = simulate(5, [2, 3, 4, 5, 6], 0.5, 0.5, np.random.default_rng(0))
    assert len(y) == len(c) == 20 and (y > 0).all()
    assert true_mean(0.0, 0.0) == pytest.approx(1.0)


def test_public_api():
    import coverage_lab as cl
    for name in ["estimate_icc", "iid_bootstrap_ci", "cluster_bootstrap_ci", "design_effect_ci", "cluster_bootstrap_t_ci", "coverage_study", "reps_needed"]:
        assert callable(getattr(cl, name)), name
    assert list(inspect.signature(cl.coverage_study).parameters)[:8] == ["method", "k", "m", "sigma_u", "sigma_e", "reps", "B", "seed"]
