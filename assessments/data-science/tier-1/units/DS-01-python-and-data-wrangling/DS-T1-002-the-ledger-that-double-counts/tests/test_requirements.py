"""Public requirement tests. These FAIL on the legacy starter until you fix it.

Each test pins down one sentence of a docstring specification in settlement/pipeline.py.
They are a sample: the assessors run a larger hidden suite on a freshly generated ledger.
Write one regression test of your own per defect you find, in tests/test_member_*.py.
"""
import warnings

import pandas as pd
import pytest

import settlement as s


def _tx(**cols):
    n = len(next(iter(cols.values())))
    base = {
        "txn_ref": [f"TX{i}" for i in range(n)], "agent_id": ["AG1000"] * n, "terminal_id": ["T10001"] * n,
        "channel": ["CARD"] * n, "txn_type": ["CASH_OUT"] * n, "amount_ngn": [1000.0] * n,
        "status": ["SUCCESS"] * n, "switch_time_utc": ["2026-09-02T10:00:00Z"] * n,
        "received_at_utc": ["2026-09-02T10:00:05.000Z"] * n,
    }
    base.update(cols)
    df = pd.DataFrame(base)
    df["amount_ngn"] = df["amount_ngn"].astype("float64")
    return df


def test_agent_ids_are_stripped_and_upper_cased():
    tx = _tx(agent_id=["AG1234", "ag1234", "AG1234 ", " ag1234 "])
    assert set(s.normalise_agent_ids(tx)["agent_id"]) == {"AG1234"}


def test_normalise_does_not_modify_its_input():
    tx = _tx(agent_id=["ag1234"])
    s.normalise_agent_ids(tx)
    assert tx["agent_id"].tolist() == ["ag1234"]


def test_retries_collapse_to_latest_message():
    tx = _tx(txn_ref=["TX1", "TX1", "TX1", "TX2"],
             status=["SUCCESS", "SUCCESS", "REVERSED", "SUCCESS"],
             received_at_utc=["2026-09-02T10:00:05.000Z", "2026-09-02T10:04:00.000Z",
                              "2026-09-02T13:00:00.000Z", "2026-09-02T10:00:09.000Z"])
    out = s.resolve_retries(tx.iloc[[2, 0, 3, 1]])     # arrival order in the file is not time order
    assert sorted(out["txn_ref"]) == ["TX1", "TX2"]
    assert out.set_index("txn_ref").loc["TX1", "status"] == "REVERSED"


def test_reversed_and_failed_do_not_settle():
    tx = _tx(status=["SUCCESS", "REVERSED", "FAILED"], amount_ngn=[1000.0, 2000.0, 3000.0])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out = s.settled_only(tx)
    assert out["status"].tolist() == ["SUCCESS"]
    assert out["amount_ngn"].tolist() == [1000.0]


@pytest.mark.parametrize("utc,expected", [
    ("2026-09-02T22:59:59Z", "2026-09-02"),
    ("2026-09-02T23:00:00Z", "2026-09-03"),   # midnight in Lagos
    ("2026-09-02T23:45:10Z", "2026-09-03"),
    ("2026-09-03T00:30:00Z", "2026-09-03"),
])
def test_business_date_is_west_africa_time(utc, expected):
    out = s.add_business_date(_tx(switch_time_utc=[utc]))
    assert out["business_date"].tolist() == [expected]


def test_tier_is_effective_dated_and_never_duplicates_rows():
    agents = pd.DataFrame({"agent_id": ["AG1000", "AG1000", "AG2000"], "state": ["Lagos"] * 3,
                           "tier": ["Bronze", "Silver", "Gold"],
                           "valid_from": ["2026-01-01", "2026-09-05", "2025-01-01"],
                           "valid_to": ["2026-09-05", "", ""]})
    tx = _tx(agent_id=["AG1000", "AG1000", "AG2000", "AG9999"])
    tx["business_date"] = ["2026-09-04", "2026-09-05", "2026-09-04", "2026-09-04"]
    out = s.attach_tier(tx, agents)
    assert len(out) == 4
    assert out["tier"].tolist() == ["Bronze", "Silver", "Gold", "UNASSIGNED"]


@pytest.mark.parametrize("amount,ttype,fee", [
    (4999.99, "CASH_OUT", 50.0), (5000.00, "CASH_OUT", 50.0), (5000.01, "TRANSFER", 100.0),
    (20000.00, "TRANSFER", 100.0), (20000.01, "CASH_OUT", 200.0), (5000.00, "CASH_IN", 0.0),
])
def test_fee_bands_have_inclusive_upper_bounds(amount, ttype, fee):
    got = s.fee_for_amount(pd.Series([amount]), pd.Series([ttype]))
    assert got.tolist() == [fee]


def test_reconcile_small_example():
    settlement = pd.DataFrame({"agent_id": ["A", "B", "A"], "business_date": ["2026-09-01", "2026-09-01", "2026-09-02"],
                               "txn_count": [2, 1, 4], "value_ngn": [100.0, 50.0, 400.0], "fees_ngn": [0.0] * 3,
                               "commission_ngn": [0.0] * 3, "tier": ["Gold"] * 3})
    control = pd.DataFrame({"business_date": ["2026-09-01", "2026-09-03"], "successful_count": [3, 1],
                            "successful_value_ngn": [150.0, 10.0]})
    out = s.reconcile_with_switch(settlement, control)
    assert list(out.columns) == s.RECONCILE_COLUMNS
    assert out["business_date"].tolist() == ["2026-09-01", "2026-09-02", "2026-09-03"]
    assert out["matches"].tolist() == [True, False, False]
    assert out["count_diff"].tolist() == [0, 4, -1]


def test_official_ledger_reconciles_with_the_switch(tx, agents, control):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        settlement = s.daily_settlement(tx, agents)
    rec = s.reconcile_with_switch(settlement, control)
    assert rec["matches"].all(), rec.loc[~rec["matches"]]
    assert list(settlement.columns) == s.SETTLEMENT_COLUMNS
    assert not settlement.duplicated(["agent_id", "business_date"]).any()
