"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect
import subprocess
import sys

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "9d1016852e6977e86425514a213106eb54f3b0234aa00eaa29327edd47cbf023"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "armyworm_survey.csv was modified"


def test_generator_reproduces_dataset(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "resources" / "generate_survey.py"), "--out", str(tmp_path),
                           "--seed", "2026"], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "armyworm_survey.csv").read_bytes() == DATA.read_bytes()


def test_survey_loads(survey):
    assert survey.J == 30 and survey.n.size == 281
    assert (survey.y <= survey.n).all() and set(survey.x) <= {0.0, 1.0}


def test_contract_signatures():
    import mcmc_lab as ml
    assert list(inspect.signature(ml.hmc).parameters)[:6] == ["logp_and_grad", "x0", "n_samples", "step_size",
                                                               "n_leapfrog", "rng"]
    assert list(inspect.signature(ml.model.logp_and_grad).parameters) == ["theta", "data", "centred"]
    for name in ["split_rhat", "ess_bulk", "rwm", "sbc_ranks"]:
        assert callable(getattr(ml, name)), name
