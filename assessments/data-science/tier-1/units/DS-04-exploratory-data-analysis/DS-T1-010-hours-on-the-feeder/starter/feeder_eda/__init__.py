"""feeder_eda: supply-hours exploration for the DS-T1-010 feeder outage logs.

The public API is fixed because the tests import it.
"""
from .io import BAND_MIN_HOURS, EXPORT_TIME, PERIOD_START, TIME_FORMAT, load_all, load_coverage, load_events, load_feeders
from .events import merge_intervals, parse_events
from .supply import daily_supply, feeder_summary
from .uncertainty import band_summary, block_bootstrap_mean_ci, flag_misbanded
from .answers import build_answers, grid_collapse_days

__all__ = [
    "BAND_MIN_HOURS", "EXPORT_TIME", "PERIOD_START", "TIME_FORMAT", "load_all", "load_coverage", "load_events",
    "load_feeders", "merge_intervals", "parse_events", "daily_supply", "feeder_summary", "band_summary",
    "block_bootstrap_mean_ci", "flag_misbanded", "build_answers", "grid_collapse_days",
]
