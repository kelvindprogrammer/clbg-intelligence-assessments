"""Daily agent settlement: the LEGACY implementation.

Written in 2024 by a contractor and in production since. Finance reports that the
totals "never quite match the switch". Each function below has a docstring that
states what it is SUPPOSED to do (the specification). The code is what it actually does.

Your job: find every place where the code does not meet its specification, prove it
with a failing test, fix it, and measure how much each defect cost. Do not change the
function names or parameters: the tests import them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .rules import COMMISSION_RATE, FEE_ABOVE, FEE_BANDS, FEE_TYPES, SETTLEMENT_COLUMNS


def normalise_agent_ids(tx: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of tx with agent_id in canonical form ("AG" followed by 4 digits).

    Some terminal firmware sends agent IDs in lower case or with stray spaces.
    The input frame must not be modified.
    """
    tx["agent_id"] = tx["agent_id"].str.upper()
    return tx


def resolve_retries(tx: pd.DataFrame) -> pd.DataFrame:
    """Return one row per txn_ref: the message with the latest received_at_utc.

    The switch resends a message when it does not get an acknowledgement in time, and it
    sends a new message for the same txn_ref when a transaction's status changes later
    (for example SUCCESS -> REVERSED). The latest message received is authoritative.
    """
    return tx.drop_duplicates()


def settled_only(tx: pd.DataFrame) -> pd.DataFrame:
    """Return only the transactions that settle: final status SUCCESS.

    FAILED and REVERSED transactions contribute nothing: no count, no value, no fee.
    """
    tx = tx[tx["status"].isin(["SUCCESS", "REVERSED"])]
    # zero out reversals, then keep only rows with a positive amount
    tx[tx["status"] == "REVERSED"]["amount_ngn"] = 0.0
    return tx[tx["amount_ngn"] > 0]


def add_business_date(tx: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of tx with a business_date column ("YYYY-MM-DD").

    The business date is the calendar date in West Africa Time (UTC+1) of switch_time_utc.
    """
    tx = tx.copy()
    tx["business_date"] = pd.to_datetime(tx["switch_time_utc"]).dt.strftime("%Y-%m-%d")
    return tx


def attach_tier(tx: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    """Return tx with a tier column: the agent's tier ON THE TRANSACTION'S BUSINESS DATE.

    agents holds the tier history: a row applies from valid_from (inclusive) to valid_to
    (exclusive); valid_to is "" for the current row. Transactions whose agent has no row
    in agents get tier "UNASSIGNED". Every input row appears exactly once in the output.
    """
    return tx.merge(agents[["agent_id", "tier"]], on="agent_id", how="inner")


def fee_for_amount(amount: pd.Series, txn_type: pd.Series) -> pd.Series:
    """Return the fee in NGN for each transaction (float64, same index as amount).

    Fees apply only to FEE_TYPES. Bands are in rules.FEE_BANDS with INCLUSIVE upper
    bounds (a ₦5,000.00 cash-out pays the ₦50 fee), and FEE_ABOVE applies above the last bound.
    """
    edges = [0.0] + [b for b, _ in FEE_BANDS] + [np.inf]
    labels = [f for _, f in FEE_BANDS] + [FEE_ABOVE]
    fee = pd.cut(amount, bins=edges, labels=labels, right=False).astype("float64")
    return fee.where(txn_type.isin(FEE_TYPES), 0.0)


def daily_settlement(tx: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    """Return one row per (agent_id, business_date) with SETTLEMENT_COLUMNS.

    txn_count, value_ngn, fees_ngn and commission_ngn cover settled transactions only.
    commission_ngn = fee x COMMISSION_RATE[tier]. Money columns are rounded to 2 dp.
    tier is the agent's tier on that business date. Rows are sorted by agent_id, business_date.
    """
    tx = normalise_agent_ids(tx)
    tx = resolve_retries(tx)
    tx = settled_only(tx)
    tx = add_business_date(tx)
    tx = attach_tier(tx, agents)
    tx["fee_ngn"] = fee_for_amount(tx["amount_ngn"], tx["txn_type"])
    tx["commission_ngn"] = tx["fee_ngn"] * tx["tier"].map(COMMISSION_RATE)
    out = (tx.groupby(["agent_id", "business_date"], as_index=False)
             .agg(txn_count=("txn_ref", "count"), value_ngn=("amount_ngn", "sum"),
                  fees_ngn=("fee_ngn", "sum"), commission_ngn=("commission_ngn", "sum"),
                  tier=("tier", "last")))
    for c in ["value_ngn", "fees_ngn", "commission_ngn"]:
        out[c] = out[c].round(2)
    return out[SETTLEMENT_COLUMNS].sort_values(["agent_id", "business_date"]).reset_index(drop=True)
