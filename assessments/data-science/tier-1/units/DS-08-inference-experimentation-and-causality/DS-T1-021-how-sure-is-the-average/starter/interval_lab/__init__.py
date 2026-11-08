"""interval_lab: confidence intervals from first principles (DS-T1-021)."""
from .intervals import bootstrap_ci, diff_means_ci_bootstrap, required_n, t_interval
from .simulate import coverage
from .report import load_transactions, summarise_regions

__all__ = ["t_interval", "bootstrap_ci", "diff_means_ci_bootstrap", "required_n", "coverage",
           "summarise_regions", "load_transactions"]
