"""Data-contract and drift gate for a market-price feed. Provided: KINDS, prefixes, Decision, decide,
load_contract, load_batches. Implement R1-R8."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import yaml

# Fault kinds and the action a correct gate takes on a batch containing exactly that fault.
KINDS = {"rename_column": "block", "new_column": "accept", "type_change": "block", "unit_change": "block",
         "null_spike": "quarantine", "new_category": "quarantine", "date_flip": "block", "dup_keys": "quarantine"}
# Reason codes are 'family:what[:column]'. These prefixes decide the action.
BLOCK_PREFIXES = ("schema:missing_column", "schema:type_change", "rule:date_format", "rule:range", "drift:scale_shift")
QUARANTINE_PREFIXES = ("rule:null", "rule:category", "rule:key_duplicate", "drift:null_rate", "drift:new_category")
# Anything else (for example 'schema:new_column:<col>') is informational and does not stop a batch.


@dataclass
class Decision:
    action: str                                 # 'accept' | 'quarantine' | 'block'
    reasons: list = field(default_factory=list)  # reason codes, e.g. 'rule:null:state'


def decide(reasons: list) -> Decision:
    """Provided: block if any reason has a BLOCK prefix, else quarantine if any has a QUARANTINE prefix, else accept."""
    if any(r.startswith(BLOCK_PREFIXES) for r in reasons):
        return Decision("block", list(reasons))
    if any(r.startswith(QUARANTINE_PREFIXES) for r in reasons):
        return Decision("quarantine", list(reasons))
    return Decision("accept", list(reasons))


def load_contract(path) -> dict:
    """Provided: parse resources/contract.yaml."""
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def load_batches(folder) -> list:
    """Provided: the batch_*.csv files as DataFrames in name order (identifier columns read as text)."""
    return [pd.read_csv(p, dtype={"market_id": str, "state": str, "commodity": str, "observed_on": str})
            for p in sorted(Path(folder).glob("batch_*.csv"))]


def infer_schema(df: pd.DataFrame) -> dict:
    """R1: {column: 'int' | 'float' | 'string'} from the pandas dtype (integer kinds -> int, float -> float,
    everything else -> string)."""
    raise NotImplementedError("R1: infer_schema")


def diff_schema(contract: dict, schema: dict) -> list:
    """R2: reason codes for structural differences between the contract and an inferred schema:
    `schema:missing_column:<col>` for a contract column that is absent;
    `schema:type_change:<col>` when the types are incompatible (int and float contract columns accept int or float
    data; string accepts only string; numeric vs string either way is a change);
    `schema:new_column:<col>` for a column the contract does not know (informational)."""
    raise NotImplementedError("R2: diff_schema")


def validate_batch(df: pd.DataFrame, contract: dict) -> list:
    """R3: reason codes for row-level rule violations whose RATE exceeds the contract's allowance (rate = violating
    rows / all rows in the batch). Rules: `rule:null:<col>` (null rate above max_null_rate, default 0),
    `rule:category:<col>` (unknown categories above max_unknown_rate, default 0), `rule:date_format:<col>` (strings not
    parseable with date_format above max_bad_rate, default 0), `rule:range:<col>` (values outside [min, max] above
    max_out_of_range_rate, default 0), `rule:key_duplicate:key` (share of rows repeating an earlier row's key above
    max_key_duplicate_rate). Columns that are absent or retyped are the schema check's business: skip them quietly."""
    raise NotImplementedError("R3: validate_batch")


def fit_baseline(batches: list, contract: dict):
    """R4a: learn what 'normal' looks like from batches known to be clean, and return any object your
    `detect_drift` understands. You must decide what to learn (per-commodity price levels, null rates, ...) and
    how to set thresholds from the batch-to-batch variation you see, including gradual inflation and the smaller
    Sunday batches, which are NOT faults."""
    raise NotImplementedError("R4: fit_baseline")


def detect_drift(df: pd.DataFrame, baseline) -> list:
    """R4b: reason codes for statistical drift that the contract cannot see: `drift:scale_shift:<col>` (a numeric
    column's level has jumped by a factor that normal variation cannot explain, such as a change of unit) and
    `drift:null_rate:<col>` (a column's null rate has jumped relative to its baseline even though the contract
    still allows it). Never raise on a missing or retyped column."""
    raise NotImplementedError("R4: detect_drift")


def gate(df: pd.DataFrame, contract: dict, baseline) -> Decision:
    """R5: combine R2, R3 and R4 and return `decide(all reasons)`."""
    raise NotImplementedError("R5: gate")


def run_stream(batches: list, contract: dict, n_baseline: int = 15) -> list:
    """R6: fit the baseline on `batches[:n_baseline]` (assumed clean) and return one Decision per remaining batch,
    in order. You may update the baseline with accepted batches if you can justify it."""
    raise NotImplementedError("R6: run_stream")


def inject_fault(df: pd.DataFrame, kind: str, seed: int = 0) -> pd.DataFrame:
    """R7: return a COPY of a clean batch with exactly one fault of `kind` (a key of KINDS) injected, using only the
    seed for randomness. Required effects: rename_column renames price_ngn_per_kg to `price`; new_column adds an
    all-null column; type_change turns n_quotes into text such as '7 quotes'; unit_change multiplies price by 100
    (naira to kobo); null_spike nulls about 25% of `state`; new_category renames every 'Garri' to 'Garri (white)';
    date_flip swaps day and month in observed_on (DD/MM/YYYY -> MM/DD/YYYY); dup_keys appends a random 25% copy of
    the rows. Raise ValueError for an unknown kind."""
    raise NotImplementedError("R7: inject_fault")


def operating_characteristics(batches: list, contract: dict, n_fit: int = 10, n_eval: int = 5, seed: int = 0) -> pd.DataFrame:
    """R8: estimate your gate's behaviour. Fit on `batches[:n_fit]`; take the next `n_eval` clean batches. Return a
    DataFrame [kind, n, detected, rate] with one row `clean` (detected = number of clean batches that were NOT
    accepted, i.e. false alarms) and one row per fault kind (detected = number of faulted copies, injected with
    seed + index, on which the gate's action equals KINDS[kind])."""
    raise NotImplementedError("R8: operating_characteristics")
