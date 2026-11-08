"""R2: one week key for every agency."""
from __future__ import annotations

import datetime as dt


def week_start(d: dt.date) -> dt.date:
    """The Monday of the ISO week containing `d`."""
    raise NotImplementedError("R2: week_start")


def iso_week_monday(label: str) -> dt.date:
    """The Monday of an ISO 8601 week label such as '2025W02'. Raise ValueError for anything else."""
    raise NotImplementedError("R2: iso_week_monday")
