"""rainfall: agro-climate indices for DS-T1-003.

legacy.py is the slow, correct specification. fast.py is yours to write.
"""
from . import fast, legacy
from .loaders import load_rainfall

FUNCTIONS = ["monthly_totals", "longest_dry_spell", "onset_dates", "standardised_anomalies"]

__all__ = ["fast", "legacy", "load_rainfall", "FUNCTIONS"]
