"""The coverage study and the survey analysis (requirements R6-R7)."""
from __future__ import annotations

import math

import pandas as pd

# The fixed study populations (README section D.1, R6). Do not change them.
VALUE_MEANLOG = math.log(120_000.0)   # daily transaction value: lognormal(meanlog, sdlog), naira
VALUE_SDLOG = 1.1
FRAUD_P = 0.04                        # fraud attempt in the last 30 days: Bernoulli(p)
TRUE_MEAN = math.exp(VALUE_MEANLOG + VALUE_SDLOG ** 2 / 2)
TRUE_MEDIAN = math.exp(VALUE_MEANLOG)
STUDY_NS = (10, 20, 40, 160)
STUDY_COLUMNS = ["estimand", "method", "n", "coverage", "mc_se", "mean_width", "miss_below", "miss_above", "reps"]
SURVEY_COLUMNS = ["lga", "n", "mean", "mean_t_lo", "mean_t_hi", "mean_bca_lo", "mean_bca_hi", "median",
                  "median_bca_lo", "median_bca_hi", "fraud_k", "fraud_p", "fraud_wilson_lo", "fraud_wilson_hi"]


def run_study(reps: int = 1000, B: int = 1000, seed: int = 2026, ns=STUDY_NS) -> pd.DataFrame:
    """Run the coverage grid of README R6 and return one row per (estimand, method, n) with STUDY_COLUMNS.

    estimand "mean": methods t, percentile, basic, bca;  "median": percentile, basic, bca;
    "proportion": wald, wilson, clopper_pearson. All at level 0.95. Reproducible from `seed`.
    """
    raise NotImplementedError("R6: implement run_study")


def analyse_survey(df: pd.DataFrame, B: int = 5000, seed: int = 2026) -> pd.DataFrame:
    """One row per LGA (sorted by name) with SURVEY_COLUMNS, at level 0.95, reproducible from `seed`."""
    raise NotImplementedError("R7: implement analyse_survey")
