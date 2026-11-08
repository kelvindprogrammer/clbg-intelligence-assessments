"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pandas as pd
import pytest

from conftest import DATA_DIR

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "macro_monthly.csv": "ab6e58e47408a0e9af7e8bf95ecf75148f337adcdbd8751801003381c0c186f9",
    "prices_monthly.csv": "078d0c96055279249b5fffbd70d0e1a6ae42c1e7cde76eea68124c4e0a0b80b6",
    "rainfall_monthly.csv": "0c91ed1d009d77198e97dd5f5261768019205c2fb63704d06eea9c474d8db35c",
    "states.csv": "6f95674161c7a24d0a0d556f686f3facc59259b81c9cdb7d8e4feb973cb2aad1",
}


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_data_unmodified(name):
    assert hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest() == EXPECTED_SHA256[name], f"{name} modified"


def test_panel_shape(panel):
    assert panel.states.shape[0] == 18
    assert panel.rain.shape[0] == 18 * 144
    assert panel.prices["commodity"].nunique() == 8
    assert set(panel.prices["state"]) == set(panel.states["state"])
    assert panel.macro["month"].tolist() == sorted(panel.rain["month"].unique())


def test_baseline_runs_and_follows_contract(panel):
    from rainprice import naive_register, validate_register
    reg = naive_register(panel)
    validate_register(reg)
    assert len(reg) == 18 * 8


def test_scorer_on_toy_register():
    from rainprice import REGISTER_COLUMNS, score_register
    reg = pd.DataFrame([["H1", "Kano", "millet", "deficit", 3, .1, .05, .15, .001, .01, "supported", "m", ""],
                        ["H2", "Oyo", "yam", "deficit", 0, .1, .05, .15, .001, .01, "supported", "m", ""],
                        ["H3", "Kano", "maize", "deficit", 0, 0, -1, 1, .5, .9, "not_supported", "m", ""]],
                       columns=REGISTER_COLUMNS)
    s = score_register(reg, [{"state": "Kano", "commodity": "millet", "lag": 4}, {"state": "Kano", "commodity": "maize", "lag": 2}])
    assert (s["true_positives"], s["recall"], s["fdr"], s["lag_accuracy"]) == (1, 0.5, 0.5, 1.0)


def test_contract_signature():
    from rainprice import build_register
    assert list(inspect.signature(build_register).parameters)[0] == "panel"
