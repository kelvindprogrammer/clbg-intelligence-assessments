"""Provided plumbing. A candidate is a dict: name, family, spec (for cost_model), W (effective weights, F x C) and b."""
import numpy as np


def quantise_cols(W, bits):
    """Symmetric per-column quantisation; returns the dequantised (effective) matrix."""
    W = np.asarray(W, float)
    qmax = 2 ** (bits - 1) - 1
    m = np.abs(W).max(axis=0)
    s = np.where(m > 0, m / qmax, 1.0)
    return np.clip(np.rint(W / s), -qmax, qmax) * s


def accuracy(cand, texts, y):
    """Accuracy of a candidate, recomputed from its weights (never from anything the candidate reports about itself)."""
    from datagen import vectorizer
    X = vectorizer(cand["W"].shape[0]).transform(texts)
    return float(((X @ cand["W"] + cand["b"]).argmax(1) == np.asarray(y)).mean())
