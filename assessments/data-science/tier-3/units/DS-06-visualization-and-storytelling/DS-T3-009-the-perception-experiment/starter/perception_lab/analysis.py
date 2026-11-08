"""Analysis and power simulation. Signatures are fixed; internals are yours."""
from __future__ import annotations


def log_abs_error(judged_pct, true_pct):
    """Cleveland-McGill error log2(|judged - true| + 1/8), elementwise, percentages on a 0-100 scale (R4)."""
    raise NotImplementedError("R4: the log absolute error measure")


def analyze(responses, B=2000, seed=0):
    """Rank encodings from a responses table (columns participant, encoding, true_pct, judged_pct) (R5).

    Return a DataFrame sorted by rank with columns encoding, mean_log_error, ci_low, ci_high, mean_signed_error, rank
    (rank 1 = lowest mean log error). The unit of analysis is the PARTICIPANT: average within participant first, then
    bootstrap participants (with replacement, B draws, seeded) for a 95% percentile interval of each encoding's mean.
    mean_signed_error is the mean of (judged_pct - true_pct) in percentage points (positive = overestimated ratio).
    """
    raise NotImplementedError("R5: participant-level bootstrap and ranking")


def ranking_recovery_rate(n_participants, repeats, reps, seed, ratios=(0.3, 0.5, 0.7, 0.9), true_order=None, params=None):
    """Power of the experiment to recover the true ranking (R6).

    For i in range(reps): build a design with your make_design, simulate responses with observer.simulate_responses
    (using `params`, default observer.DEFAULT_PARAMS), analyse with your analyze (B=200 is enough here), and check
    that the estimated ranking equals `true_order` (default: the order implied by DEFAULT_PARAMS, best first:
    bar_common, bar_unaligned, pie_angle, circle_area). Return the fraction of replications that recover it.
    Deterministic given `seed`; use a distinct seed per replication.
    """
    raise NotImplementedError("R6: simulate whole experiments")
