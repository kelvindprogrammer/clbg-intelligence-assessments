"""The collection pass. Only these three functions are fixed by the tests: design everything behind them.

You will probably want separate modules for fetching, parsing, validation and storage. That is your call,
and the README asks you to justify it.
"""
from __future__ import annotations

from .contract import CollectorConfig, RunReport  # noqa: F401


def canonical_url(url: str) -> str:
    """Return one canonical form for URLs that address the same resource (see README R3)."""
    raise NotImplementedError("R3: canonical_url")


def run_once(cfg: CollectorConfig) -> RunReport:
    """Run one complete, polite collection pass against cfg.base_url and update cfg.state_dir (R1–R9)."""
    raise NotImplementedError("R1-R9: run_once")


def load_records(state_dir) -> list:
    """Every stored notice record (including withdrawn ones) as dicts with at least RECORD_FIELDS (R6)."""
    raise NotImplementedError("R6: load_records")
