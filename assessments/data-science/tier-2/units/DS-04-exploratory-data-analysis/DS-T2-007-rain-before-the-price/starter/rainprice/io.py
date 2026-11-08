"""Loading, the register contract and the scorer (provided complete in the starter)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REGISTER_COLUMNS = ["hypothesis_id", "state", "commodity", "rain_feature", "lag_months", "effect", "ci_low", "ci_high",
                    "p_value", "q_value", "status", "method", "follow_up"]
STATUSES = ["supported", "exploratory", "not_supported", "insufficient_data"]


@dataclass
class Panel:
    rain: pd.DataFrame     # state, month, rain_mm
    prices: pd.DataFrame   # state, month, commodity, price_ngn_per_kg
    macro: pd.DataFrame    # month, fx_ngn_per_usd, petrol_ngn_per_litre, food_cpi
    states: pd.DataFrame   # state, zone, agro_zone, lat, lon


def load_panel(data_dir: str | Path) -> Panel:
    d = Path(data_dir)
    rd = lambda n: pd.read_csv(d / n, dtype={"state": str, "month": str, "commodity": str})  # noqa: E731
    return Panel(rd("rainfall_monthly.csv"), rd("prices_monthly.csv"), rd("macro_monthly.csv"), rd("states.csv"))


def validate_register(reg: pd.DataFrame) -> None:
    """Raise ValueError if `reg` does not follow the register contract (README section D.1)."""
    if list(reg.columns) != REGISTER_COLUMNS:
        raise ValueError(f"columns must be exactly {REGISTER_COLUMNS}")
    if not reg["hypothesis_id"].is_unique:
        raise ValueError("hypothesis_id must be unique")
    bad = set(reg["status"]) - set(STATUSES)
    if bad:
        raise ValueError(f"unknown status values {bad}")
    sup = reg[reg["status"] == "supported"]
    if sup[["effect", "ci_low", "ci_high", "p_value", "q_value"]].isna().any().any():
        raise ValueError("supported rows need effect, interval, p_value and q_value")
    if ((reg["p_value"].dropna() < 0) | (reg["p_value"].dropna() > 1)).any():
        raise ValueError("p_value must be in [0, 1]")


def score_register(reg: pd.DataFrame, true_pairs: list[dict]) -> dict:
    """Score a register against a list of true links [{state, commodity, lag, ...}].

    A (state, commodity) pair counts as claimed if ANY of its rows has status "supported".
    Use this on data you simulated yourself, where you know the truth.
    """
    truth = {(t["state"], t["commodity"]): t for t in true_pairs}
    sup = reg[reg["status"] == "supported"]
    claimed = set(zip(sup["state"], sup["commodity"]))
    tp = claimed & set(truth)
    lag_ok = 0
    for p in tp:
        lags = sup[(sup["state"] == p[0]) & (sup["commodity"] == p[1])]["lag_months"]
        lag_ok += int((abs(lags - truth[p]["lag"]) <= 1).any())
    return {"n_claimed": len(claimed), "n_true": len(truth), "true_positives": len(tp),
            "recall": len(tp) / len(truth) if truth else float("nan"),
            "fdr": (len(claimed) - len(tp)) / len(claimed) if claimed else 0.0,
            "lag_accuracy": lag_ok / len(tp) if tp else float("nan")}
