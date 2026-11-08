"""collector: a polite, change-aware collector for the Ajana State e-procurement portal (DS-T2-003).

Only the names re-exported here are fixed by the tests. Structure everything else as you see fit.
"""
from .contract import ALARM_KINDS, RECORD_FIELDS, CollectorConfig, RunReport
from .pipeline import canonical_url, load_records, run_once
from .robots import Robots

__all__ = ["ALARM_KINDS", "RECORD_FIELDS", "CollectorConfig", "RunReport", "canonical_url", "load_records",
           "run_once", "Robots"]
