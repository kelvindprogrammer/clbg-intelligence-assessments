"""Contract tests: these pass on the unmodified starter.

They check data integrity, generator determinism, the provided helpers and the API signatures.
"""
import hashlib
import inspect
import subprocess
import sys

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "seed_adoption_survey.csv": "d6116bf24d7498114946ac14f7a31e6503b82993539c3183cd534367d8cf6fa0",
    "maize_price_history.csv": "dc922daf5ff3f93e0240bb84492f8fad540a48d848c0255180f09d2a7a554d25",
    "maize_price_forecast.csv": "56632a3c85ab673a9d3847836fc305fb4e6ee326c36f3883b0525ba86ccf1035",
    "march_price_samples.csv": "7d68ba16ab6cb665a43df6cea88bc13a652b45d3b97f421ce7bfe4563fe4b1c8",
}


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_data_unmodified(name):
    assert _sha(DATA / name) == EXPECTED_SHA256[name], f"{name} has been modified. Restore it or regenerate with seed 2026."


def test_generator_reproduces_committed_data(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "resources" / "generate_data.py"), "--out", str(tmp_path), "--seed", "2026"],
                   check=True, capture_output=True)
    for name, digest in EXPECTED_SHA256.items():
        assert _sha(tmp_path / name) == digest, name


def test_schemas(data):
    assert list(data["seed_adoption_survey"].columns) == ["state", "farmers_surveyed", "adopted"]
    assert list(data["maize_price_forecast"].columns) == ["market", "month", "q0.025", "q0.1", "q0.25", "q0.5",
                                                          "q0.75", "q0.9", "q0.975"]
    assert set(data["march_price_samples"].groupby("market").size()) == {4000}


def test_provided_helpers():
    from uncertainty_viz import level_columns, quantile_columns
    import pandas as pd
    assert level_columns(0.95) == ("q0.025", "q0.975")
    assert level_columns(0.8) == ("q0.1", "q0.9")
    assert level_columns(0.5) == ("q0.25", "q0.75")
    assert quantile_columns(pd.DataFrame(columns=["month", "q0.9", "q0.1", "q0.5"])) == ["q0.1", "q0.5", "q0.9"]


def test_api_signatures():
    import uncertainty_viz as uv
    assert issubclass(uv.QuantileCrossingError, ValueError)
    assert list(inspect.signature(uv.wilson_interval).parameters) == ["k", "n", "level"]
    assert list(inspect.signature(uv.stack_dots).parameters) == ["values", "bin_width", "origin"]
    fan = inspect.signature(uv.fan_chart).parameters
    assert fan["levels"].default == (0.5, 0.8, 0.95) and fan["time_col"].kind is inspect.Parameter.KEYWORD_ONLY
    dot = inspect.signature(uv.quantile_dotplot).parameters
    assert dot["threshold"].kind is inspect.Parameter.KEYWORD_ONLY
