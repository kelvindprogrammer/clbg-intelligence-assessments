"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "3059f603129ecb1487c2dcf708c90edae80a5e460e7505eb65e54ae8aeced0fb"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "agent_daily.csv was modified; restore it"


def test_dataset_shape():
    import agentcast as ac
    df = ac.load_export(DATA)
    assert list(df.columns) == ["agent_id", "date", "txn_count"]
    assert df["agent_id"].nunique() == 8


def test_public_api():
    import agentcast as ac
    for name in ["to_regular", "fill_gaps", "seasonal_naive", "moving_average", "mae", "mase",
                 "rolling_origin", "backtest", "choose_baseline"]:
        assert callable(getattr(ac, name)), name
    assert list(inspect.signature(ac.backtest).parameters)[:5] == ["y", "method", "h", "initial", "step"]
