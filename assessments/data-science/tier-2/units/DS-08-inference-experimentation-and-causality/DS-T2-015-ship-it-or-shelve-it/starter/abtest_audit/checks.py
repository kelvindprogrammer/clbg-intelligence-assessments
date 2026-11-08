"""Integrity checks that must run before any effect is estimated."""


def srm_check(df, threshold=0.001):
    """R1: sample-ratio-mismatch test on a 50/50 design.

    Returns {"n_a", "n_b", "p_value", "flagged"}; counts are unique users per arm.
    """
    raise NotImplementedError("R1: srm_check")


def find_contaminated(df):
    """R2: set of user_ids that appear in more than one arm."""
    raise NotImplementedError("R2: find_contaminated")
