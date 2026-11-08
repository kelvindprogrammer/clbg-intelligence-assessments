"""Whose label is it anyway? Find, size and survive label noise in field-agent annotations.
Replace each R<n> stub. numpy and scikit-learn only."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class LabelData:
    X: np.ndarray          # (n, 12) leaf-image embeddings
    annotator: np.ndarray  # (n,) int 0..3, which field agent labelled the leaf
    y: np.ndarray          # (n,) noisy labels: 0 healthy, 1 mosaic, 2 brown streak
    gold_idx: np.ndarray   # indices of the 60 leaves also labelled by an expert
    gold_y: np.ndarray     # the expert labels (trusted, but only 60)


def load_labels(path, gold_path) -> LabelData:
    """Provided."""
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    ids = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=(0,), dtype=str)
    ann = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=(1,), dtype=str)
    X = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=range(2, len(header) - 1))
    y = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=(len(header) - 1,)).astype(int)
    gid = np.genfromtxt(gold_path, delimiter=",", skip_header=1, usecols=(0,), dtype=str)
    gy = np.genfromtxt(gold_path, delimiter=",", skip_header=1, usecols=(1,)).astype(int)
    pos = {i: k for k, i in enumerate(ids)}
    return LabelData(X, np.array([int(a[1:]) for a in ann]), y, np.array([pos[g] for g in gid]), gy)


def oof_proba(X: np.ndarray, y: np.ndarray, n_splits: int = 5, seed: int = 0, n_classes: int = 3) -> np.ndarray:
    """R1: out-of-fold class probabilities, shape (n, n_classes), rows sum to 1. Every row is predicted by a model
    that never saw that row (stratified k-fold on y, seeded). Model choice is yours; justify it."""
    raise NotImplementedError("R1: out-of-fold probabilities")


def estimate_noise(X: np.ndarray, y: np.ndarray, annotator: np.ndarray, seed: int = 0) -> dict:
    """R2: {"overall": estimated fraction of mislabelled items, "per_annotator": {annotator: estimated rate}}.
    No ground truth is available beyond the 60 gold labels, which you may use for calibration or checking but the
    estimator must work from (X, y, annotator) alone. Document the assumptions of your estimator."""
    raise NotImplementedError("R2: noise rate estimation")


def select_for_relabel(X: np.ndarray, y: np.ndarray, annotator: np.ndarray, budget: int, seed: int = 0) -> np.ndarray:
    """R3: indices (unique ints, exactly `budget` of them, most suspicious first) of the labels you would send to
    an expert. An expert relabelling costs money, so precision matters."""
    raise NotImplementedError("R3: relabel selection")


def fit_robust(X: np.ndarray, y: np.ndarray, annotator: np.ndarray, seed: int = 0):
    """R4: return a fitted classifier with .predict(X) that is as accurate as you can make it on CLEAN data when
    trained on these noisy labels (for example by discarding or down-weighting suspicious items). Deterministic."""
    raise NotImplementedError("R4: noise-robust training")
