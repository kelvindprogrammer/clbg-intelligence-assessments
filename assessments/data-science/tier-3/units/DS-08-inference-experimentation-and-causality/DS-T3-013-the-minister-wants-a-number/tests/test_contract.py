"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
SHA = "6bea76392233a2479f0988f80604f2da2f29044395a13df5bd32bb43a73ab7db"


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA, "minigrid_panel.csv was modified"


def test_panel_shape():
    from staggered_did import load_panel
    df = load_panel(DATA)
    assert list(df.columns) == ["unit_id", "period", "cohort", "outcome"]
    assert df["unit_id"].nunique() == 80 and df["period"].nunique() == 12 and len(df) == 960
    assert sorted(df["cohort"].unique()) == [0, 5, 7, 9]


def test_api_present():
    import staggered_did as sd
    for n in ["twfe_att", "group_time_att", "aggregate_att", "cluster_bootstrap", "pretrend_test", "analyze"]:
        assert callable(getattr(sd, n)), n
