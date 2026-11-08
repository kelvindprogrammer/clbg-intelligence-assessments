"""Requirement tests against the committed expected answers (public data only). Fail on the starter."""
import json
from decimal import Decimal

import duckdb
import pytest

from conftest import ROOT, load_raw

EXP = json.loads((ROOT / "tests" / "expected_public.json").read_text())
D = Decimal("0.01")


@pytest.fixture(scope="module")
def con():
    import analytics_model
    c = duckdb.connect()
    load_raw(c)
    analytics_model.build(c)
    return c


def q(con, sql):
    return con.execute(sql).fetchall()


def test_dim_agent_scd2(con):
    rows = q(con, "SELECT agent_id, tier, region, CAST(valid_from AS VARCHAR), CAST(valid_to AS VARCHAR), is_current FROM dim_agent ORDER BY 1, 4")
    assert [list(r) for r in rows] == EXP["dim"]


def test_dim_agent_has_no_gaps_or_overlaps(con):
    bad = q(con, """SELECT COUNT(*) FROM (SELECT valid_to, LEAD(valid_from) OVER (PARTITION BY agent_id ORDER BY valid_from) AS nxt FROM dim_agent)
                    WHERE nxt IS NOT NULL AND nxt <> valid_to""")
    assert bad[0][0] == 0


def test_fact_txn_membership_and_values(con):
    rows = q(con, "SELECT txn_id, CAST(amount_ngn AS VARCHAR), CAST(fee_ngn AS VARCHAR), CAST(fx_rate_date AS VARCHAR), tier, region FROM fact_txn ORDER BY txn_id")
    assert len(rows) == len(EXP["fact"]), "wrong set of transactions in fact_txn (reversals, exceptions, duplicates?)"
    for got, exp in zip(rows, EXP["fact"]):
        assert got[0] == exp[0]
        assert abs(Decimal(got[1]) - Decimal(exp[1])) <= D and abs(Decimal(got[2]) - Decimal(exp[2])) <= D, got[0]
        assert list(got[3:]) == exp[3:], got[0]


def test_fact_txn_one_row_per_txn(con):
    assert q(con, "SELECT COUNT(*) - COUNT(DISTINCT txn_id) FROM fact_txn")[0][0] == 0


def test_point_in_time_attribution_differs_from_current_tier(con):
    n = q(con, "SELECT COUNT(*) FROM fact_txn f JOIN dim_agent d ON d.agent_id = f.agent_id AND d.is_current WHERE d.tier <> f.tier")[0][0]
    assert n > 0, "tier equals the current tier everywhere: you attributed with the latest tier (Type 1)"


def test_exceptions_exact(con):
    assert [list(r) for r in q(con, "SELECT txn_id, issue FROM dq_exceptions ORDER BY txn_id")] == EXP["exceptions"]


def test_reconciliation(con):
    r = q(con, "SELECT n_txn_ids, n_reversed, n_exceptions, n_fact FROM v_reconciliation")[0]
    e = EXP["recon"]
    assert r == (e["n_txn_ids"], e["n_reversed"], e["n_exceptions"], e["n_fact"])
    assert r[0] == r[1] + r[2] + r[3]


def test_tier_daily(con):
    rows = q(con, "SELECT CAST(txn_date AS VARCHAR), tier, n_txn, CAST(volume_ngn AS VARCHAR), CAST(fee_ngn AS VARCHAR) FROM v_tier_daily ORDER BY 1, 2")
    assert len(rows) == len(EXP["tier_daily"])
    for got, exp in zip(rows, EXP["tier_daily"]):
        assert list(got[:3]) == exp[:3]
        assert abs(Decimal(got[3]) - Decimal(exp[3])) <= D * 3 and abs(Decimal(got[4]) - Decimal(exp[4])) <= D * 3


def test_build_is_idempotent_and_leaves_raw_alone(con):
    import analytics_model
    before = q(con, "SELECT COUNT(*) FROM fact_txn")[0][0], q(con, "SELECT COUNT(*) FROM raw_txn_events")[0][0]
    analytics_model.build(con)
    assert (q(con, "SELECT COUNT(*) FROM fact_txn")[0][0], q(con, "SELECT COUNT(*) FROM raw_txn_events")[0][0]) == before
    assert q(con, "SELECT COUNT(*) FROM dim_agent")[0][0] == len(EXP["dim"])
