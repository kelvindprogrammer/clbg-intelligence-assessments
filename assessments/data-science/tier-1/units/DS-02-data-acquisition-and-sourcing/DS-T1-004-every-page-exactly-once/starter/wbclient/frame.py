"""R9: observations to a tidy DataFrame."""
from __future__ import annotations

import pandas as pd  # noqa: F401

COLUMNS = ["indicator_id", "country_iso3", "year", "value", "obs_status"]


def to_frame(observations):
    """Return a pandas DataFrame with one row per observation and COLUMNS, typed and sorted as README R9 specifies."""
    raise NotImplementedError("R9: to_frame")
