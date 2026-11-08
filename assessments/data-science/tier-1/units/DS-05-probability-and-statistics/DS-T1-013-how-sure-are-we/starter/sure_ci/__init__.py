"""sure_ci: confidence intervals and coverage experiments for DS-T1-013.

The public API is fixed because the tests import it. Implement each function in its module.
"""
from .intervals import clopper_pearson_interval, t_interval, wald_interval, wilson_interval
from .bootstrap import basic_interval, bca_interval, bootstrap_replicates, jackknife_values, percentile_interval
from .coverage import CoverageResult, coverage_experiment
from .study import (FRAUD_P, STUDY_COLUMNS, SURVEY_COLUMNS, TRUE_MEAN, TRUE_MEDIAN, VALUE_MEANLOG, VALUE_SDLOG,
                    analyse_survey, run_study)

__all__ = [
    "t_interval", "wald_interval", "wilson_interval", "clopper_pearson_interval",
    "bootstrap_replicates", "jackknife_values", "percentile_interval", "basic_interval", "bca_interval",
    "CoverageResult", "coverage_experiment", "run_study", "analyse_survey",
    "VALUE_MEANLOG", "VALUE_SDLOG", "FRAUD_P", "TRUE_MEAN", "TRUE_MEDIAN", "STUDY_COLUMNS", "SURVEY_COLUMNS",
]
