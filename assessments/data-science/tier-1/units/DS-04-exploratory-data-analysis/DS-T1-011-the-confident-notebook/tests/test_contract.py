"""Contract tests: these pass on the unmodified starter."""
import hashlib
import py_compile

import pytest

from conftest import DATA_DIR, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "agents.csv": "7b77eac5205439a3573c0050e7675512fc9ce61456ec60030b38c5518b87132d",
    "monthly_activity.csv": "316aec7f6673e208bdfc4d258421b0667910d788c27c6eacef0494ee088e5240",
}


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_data_unmodified(name):
    assert hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest() == EXPECTED_SHA256[name], \
        f"{name} has been modified. Restore the original file."


def test_schema(data):
    agents, act = data
    assert list(agents.columns) == ["agent_id", "state", "lga_type", "onboard_month", "status", "churn_month",
                                    "trained", "q1_bottom_120", "coached_q2"]
    assert list(act.columns) == ["agent_id", "month", "txn_count", "txn_value_ngn", "float_balance_avg_ngn",
                                 "fraud_flagged", "fraud_confirmed"]
    assert len(agents) == 2000 and agents["agent_id"].is_unique
    assert set(act["agent_id"]) <= set(agents["agent_id"])
    assert agents["state"].nunique() == 12
    assert int(agents["q1_bottom_120"].sum()) == 120 and int(agents["coached_q2"].sum()) == 60


NOTEBOOK_SHA256 = "7cd60fb581c714ceb21f01e6b5f37508d6c7001c19457cb6192d8ba2a83d63a7"


def test_flawed_notebook_unmodified_and_valid_python():
    nb = ROOT / "resources" / "flawed_notebook" / "agent_insights.py"
    assert hashlib.sha256(nb.read_bytes()).hexdigest() == NOTEBOOK_SHA256, "the notebook under audit must not be edited"
    py_compile.compile(str(ROOT / "resources" / "flawed_notebook" / "agent_insights.py"), doraise=True)


def test_public_api_and_vocabulary():
    import notebook_audit as na
    assert na.CLAIM_IDS == [f"C{i}" for i in range(1, 11)]
    assert na.VERDICTS == ["supported", "unsupported"]
    assert "none" in na.FLAWS and len(na.FLAWS) == 13
    assert sorted(na.CORRECTIONS, key=lambda s: int(s[1:])) == na.CLAIM_IDS
    for f in na.CORRECTIONS.values():
        assert callable(f)
    assert callable(na.validate_audit) and callable(na.state_churn_pvalues)
