"""scamguard: audit and harden an SMS scam detector against style shortcuts (ML-T3-015)."""
from .detector import fit_detector
from .metrics import bootstrap_ci, flip_rate, operating_threshold, subgroup_report

__all__ = ["subgroup_report", "bootstrap_ci", "flip_rate", "operating_threshold", "fit_detector"]
