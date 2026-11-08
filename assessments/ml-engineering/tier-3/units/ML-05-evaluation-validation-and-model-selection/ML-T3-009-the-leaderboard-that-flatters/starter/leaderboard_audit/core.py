"""Starter for ML-T3-009. Signatures are fixed. scipy and scikit-learn are allowed."""
import numpy as np  # noqa: F401


def auc_se_hanley(auc, n_pos, n_neg):
    """R1: Hanley-McNeil (1982) standard error of an AUC estimate."""
    raise NotImplementedError("R1: auc_se_hanley")


def winner_inflation(n_candidates, n_pos, n_neg, true_auc, n_sims=1000, seed=0):
    """R2: Monte Carlo estimate of E[best observed AUC among n_candidates equally skilled, independent
    candidates scored on the same evaluation labels] minus true_auc. Deterministic for a seed."""
    raise NotImplementedError("R2: winner_inflation")


def nested_cv_auc(X, y, configs, make_model, outer_k=5, inner_k=3, seed=0):
    """R3: nested stratified cross-validation. `configs` is a list of dicts, `make_model(config)` returns an
    unfitted estimator with fit / predict_proba. Return a dict with keys:
      outer_auc (list), chosen (list of config indices, one per outer fold), nested_mean,
      naive_best_cv_auc (best mean AUC over configs from a single, non-nested outer_k-fold CV), naive_best_idx.
    Configuration choice for an outer fold may use only that fold's training rows."""
    raise NotImplementedError("R3: nested_cv_auc")


def paired_bootstrap_auc_diff(y, s_a, s_b, n_boot=1000, seed=0):
    """R4: return (AUC(a) - AUC(b), lo, hi) with a 95% percentile interval from resampling rows jointly."""
    raise NotImplementedError("R4: paired_bootstrap_auc_diff")


def required_n(delta_auc, auc_ref, pos_rate, corr=0.0, alpha=0.05, power=0.8):
    """R5: smallest total evaluation-set size at which a paired AUC difference of delta_auc is detectable at the
    given alpha (two-sided) and power, using Hanley SEs and correlation `corr` between the two AUC estimates."""
    raise NotImplementedError("R5: required_n")


def shrink_public_scores(public, n_pos, n_neg, n_submissions=None):
    """R6: shrink team-level public-leaderboard AUCs towards the field using the sampling noise of the public
    split; return an array of the same length. `n_submissions` (optional) is the number of submissions per team."""
    raise NotImplementedError("R6: shrink_public_scores")
