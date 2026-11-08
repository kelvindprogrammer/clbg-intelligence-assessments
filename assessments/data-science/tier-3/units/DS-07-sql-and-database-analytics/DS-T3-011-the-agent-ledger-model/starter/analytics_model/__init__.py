"""Your analytical model. Raw tables already loaded in `con`: raw_agent_history, raw_txn_events, raw_fx_rates.

Create dim_agent, fact_txn, dq_exceptions, v_tier_daily and v_reconciliation (see README section D).
"""


def build(con):
    """Create the model inside the DuckDB connection `con`. Must be safe to call twice (idempotent)."""
    raise NotImplementedError("R1: create dim_agent, fact_txn, dq_exceptions, v_tier_daily and v_reconciliation")
