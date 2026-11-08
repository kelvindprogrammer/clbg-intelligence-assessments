"""climate_story: hot days in Nigerian cities from NASA POWER, told with small multiples (DS-T1-017).

The public API is fixed because the tests import it.
"""
from .analysis import (MIN_COVERAGE, MIN_YEARS, annual_hot_days, monthly_climatology, percentile_threshold,
                       period_change, read_power_csv)
from .plots import small_multiples

__all__ = ["MIN_COVERAGE", "MIN_YEARS", "annual_hot_days", "monthly_climatology", "percentile_threshold",
           "period_change", "read_power_csv", "small_multiples"]
