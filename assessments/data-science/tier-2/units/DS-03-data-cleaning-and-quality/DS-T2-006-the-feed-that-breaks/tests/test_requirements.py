"""Public requirement tests. These FAIL on the starter until you implement feedguard.

They check behaviour that follows directly from the brief. The hidden suite replays two
NEW 20-day sequences (different dates, holidays and faults on different days) and checks
every delivery's status and every quarantined row.
"""
import json

import pandas as pd
import pytest

from conftest import INBOX, REF

import feedguard

TYPES = {"cash_in", "cash_out", "transfer", "bill_payment", "airtime"}
STATUSES = {"accepted", "accepted_with_quarantine", "quarantined"}


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    ledger = feedguard.process_inbox(INBOX, out)
    return out, ledger


def test_ledger_shape(run):
    out, ledger = run
    assert list(ledger.columns) == feedguard.LEDGER_COLUMNS
    assert len(ledger) == 20 and ledger["business_date"].is_monotonic_increasing
    assert set(ledger["status"]) <= STATUSES
    assert (out / "ledger.csv").is_file() and (out / "alerts.jsonl").is_file()


def test_every_row_accounted_for(run):
    _, ledger = run
    ok = ledger["status"] != "quarantined"
    assert (ledger.loc[ok, "n_accepted"] + ledger.loc[ok, "n_quarantined"] == ledger.loc[ok, "n_rows"]).all()
    assert (ledger.loc[~ok, "n_accepted"] == 0).all()


def test_history_warm_up_is_accepted(run):
    _, ledger = run
    assert (ledger["status"].iloc[:5] == "accepted").all(), "the first five deliveries are clean"


def test_obvious_breakages_quarantined(run):
    """A renamed column and a semicolon-delimited file can never be accepted."""
    _, ledger = run
    s = ledger.set_index("business_date")["status"]
    for d in ["2026-06-09", "2026-06-10"]:
        assert s[d] == "quarantined", d


def test_public_holiday_is_not_a_volume_incident(run):
    _, ledger = run
    assert ledger.set_index("business_date").loc["2026-06-12", "status"] == "accepted"


def test_accepted_rows_satisfy_contract(run):
    out, ledger = run
    agents = set(pd.read_csv(REF / "agents.csv", dtype=str)["agent_id"])
    seen = set()
    for d in ledger.loc[ledger["status"] != "quarantined", "business_date"]:
        df = pd.read_csv(out / "accepted" / f"{d}.csv", dtype=str, keep_default_na=False)
        amt, fee = pd.to_numeric(df["amount_ngn"]), pd.to_numeric(df["fee_ngn"])
        assert set(df["txn_type"]) <= TYPES, d
        assert (amt > 0).all() and (fee >= 0).all() and (fee <= amt).all(), d
        assert df["agent_id"].isin(agents).all(), d
        assert df["txn_time"].str.endswith("+01:00").all() and (df["txn_time"].str[:10] == d).all(), d
        assert df["txn_id"].is_unique, d
        assert not (set(df["txn_id"]) & seen), f"{d}: transactions accepted twice across deliveries"
        seen |= set(df["txn_id"])


def test_quarantine_is_explained(run):
    out, ledger = run
    alerts = [json.loads(line) for line in (out / "alerts.jsonl").read_text(encoding="utf-8").splitlines() if line]
    alerted = {a["business_date"] for a in alerts}
    for _, r in ledger[ledger["status"] != "accepted"].iterrows():
        assert r["business_date"] in alerted, f"{r['business_date']} was not accepted but raised no alert"
        assert (out / "quarantine" / r["business_date"]).is_dir()
        assert r["findings"], r["business_date"]


def test_some_rows_quarantined_individually(run):
    _, ledger = run
    assert (ledger["status"] == "accepted_with_quarantine").sum() >= 1
