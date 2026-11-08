"""Contract tests: these pass on the unmodified starter (the legacy code).

They check that the data is intact and that the public API exists with the required signatures.
"""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "transactions.csv": "d51ecf1c191c3d99d35774999692a9c25d14072497200cf4e8dbc1fe1c9a498d",
    "agents.csv": "3e1f18cb08ac476f45acf556a4681ceb3ad1dc19cae20fb7d36ebc33bdaff469",
    "switch_control_totals.csv": "60c7aff5f397e268c2a85563fce1d73b7da943e7053db1a8b091e70496037650",
}


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_data_is_unmodified(name):
    digest = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256[name], f"{name} has been modified. Restore the original file."


def test_loaders(tx, agents, control):
    assert list(tx.columns) == ["txn_ref", "agent_id", "terminal_id", "channel", "txn_type", "amount_ngn",
                                "status", "switch_time_utc", "received_at_utc"]
    assert tx["amount_ngn"].dtype == "float64"
    assert len(tx) == 12346
    assert list(agents.columns) == ["agent_id", "state", "tier", "valid_from", "valid_to"]
    assert list(control.columns) == ["business_date", "successful_count", "successful_value_ngn"]
    assert len(control) == 14


def test_rules_are_fixed():
    import settlement as s
    assert s.FEE_BANDS == [(5000.0, 50.0), (20000.0, 100.0)] and s.FEE_ABOVE == 200.0
    assert s.COMMISSION_RATE == {"Bronze": 0.40, "Silver": 0.50, "Gold": 0.60, "UNASSIGNED": 0.0}
    assert s.FEE_TYPES == {"CASH_OUT", "TRANSFER"}
    assert s.SETTLEMENT_COLUMNS == ["agent_id", "business_date", "txn_count", "value_ngn", "fees_ngn",
                                    "commission_ngn", "tier"]


def test_public_api_signatures():
    import settlement as s
    expected = {
        "normalise_agent_ids": ["tx"], "resolve_retries": ["tx"], "settled_only": ["tx"],
        "add_business_date": ["tx"], "attach_tier": ["tx", "agents"], "fee_for_amount": ["amount", "txn_type"],
        "daily_settlement": ["tx", "agents"], "reconcile_with_switch": ["settlement", "control"],
    }
    for name, params in expected.items():
        assert list(inspect.signature(getattr(s, name)).parameters) == params, name
