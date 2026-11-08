"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect
import math
import subprocess
import sys

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "fc1b2a2c10f9923f6f3890e1ecc24bc786b5ecf9eb0204bcc4ab7087c8736d83"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "agent_survey.csv was modified"


def test_generator_reproduces_dataset(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "resources" / "generate_survey.py"), "--out", str(tmp_path),
                           "--seed", "2026"], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "agent_survey.csv").read_bytes() == DATA.read_bytes()


def test_survey_schema(survey):
    assert list(survey.columns) == ["agent_id", "lga", "daily_value_ngn", "fraud_attempt_30d", "months_operating"]
    assert len(survey) == 213 and survey["agent_id"].is_unique
    assert survey["lga"].nunique() == 6
    assert set(survey["fraud_attempt_30d"]) <= {0, 1}
    assert (survey["daily_value_ngn"] > 0).all()


def test_public_api_and_constants():
    import sure_ci as s
    for name in ["t_interval", "wald_interval", "wilson_interval", "clopper_pearson_interval", "bootstrap_replicates",
                 "jackknife_values", "percentile_interval", "basic_interval", "bca_interval", "coverage_experiment",
                 "run_study", "analyse_survey"]:
        assert callable(getattr(s, name)), name
    assert s.TRUE_MEAN == pytest.approx(120_000 * math.exp(1.1 ** 2 / 2))
    for f in [s.percentile_interval, s.basic_interval, s.bca_interval]:
        assert list(inspect.signature(f).parameters) == ["x", "stat", "B", "level", "rng"]
