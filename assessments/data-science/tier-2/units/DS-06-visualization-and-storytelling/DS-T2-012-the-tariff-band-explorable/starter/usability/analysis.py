"""Usability analysis (the contract). See resources/usability_schema.md for the data format."""
from __future__ import annotations

import pandas as pd


def sus_score(responses) -> float:
    """R6: System Usability Scale score (0-100) from ten responses (1-5) in the standard item order.

    Raise ValueError unless there are exactly ten integer responses between 1 and 5.
    """
    raise NotImplementedError("R6: implement sus_score")


def summarise_sessions(sessions: pd.DataFrame) -> dict:
    """R6: {"n_participants", "completion_rate", "median_time_s", "mean_comprehension_gain"} from sessions.csv.

    completion_rate is the share of (participant, task) rows completed; the comprehension gain is
    post minus pre, averaged per participant first (one pre/post pair per participant) and then across participants.
    """
    raise NotImplementedError("R6: implement summarise_sessions")
