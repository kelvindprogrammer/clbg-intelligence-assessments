"""Business rules and fixed schemas, taken from the settlement policy (see README section B).

This module is correct and must not be changed: the tests import these constants.
"""
from __future__ import annotations

import datetime as dt

# Business days are West Africa Time (UTC+1, no daylight saving).
WAT = dt.timezone(dt.timedelta(hours=1), name="WAT")

# Only these transaction types earn a fee.
FEE_TYPES = frozenset({"CASH_OUT", "TRANSFER"})

# Fee bands: (upper bound INCLUSIVE, fee in NGN). Above the last bound the fee is FEE_ABOVE.
FEE_BANDS = [(5_000.00, 50.00), (20_000.00, 100.00)]
FEE_ABOVE = 200.00

# Share of the fee paid to the agent, by tier. Agents with no tier on file earn nothing
# until onboarding is completed, and must be reported as "UNASSIGNED".
COMMISSION_RATE = {"Bronze": 0.40, "Silver": 0.50, "Gold": 0.60, "UNASSIGNED": 0.0}

SETTLEMENT_COLUMNS = ["agent_id", "business_date", "txn_count", "value_ngn", "fees_ngn",
                      "commission_ngn", "tier"]
RECONCILE_COLUMNS = ["business_date", "settled_count", "settled_value_ngn", "switch_count",
                     "switch_value_ngn", "count_diff", "value_diff_ngn", "matches"]
