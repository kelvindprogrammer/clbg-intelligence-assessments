"""Provided plumbing: loading and evaluating against the clerical sample. You don't need to change this."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_register(path: str | Path) -> pd.DataFrame:
    """Load a register with every column as text and no automatic NA conversion."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)


def load_clerical_sample(path: str | Path) -> pd.DataFrame:
    """250 PHC records whose true GH match (or absence of one) a records officer has confirmed."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)


def evaluate_links(links: pd.DataFrame, clerical: pd.DataFrame) -> dict:
    """Precision, recall and F1 of `links` (columns a_id, b_id; matches only) RESTRICTED to the
    PHC records in the clerical sample. Because the sample's truth is complete for those records,
    these are unbiased estimates of the full-register precision and recall.
    """
    ids = set(clerical["phc_id"])
    truth = {(r.phc_id, r.true_gh_id) for r in clerical.itertuples() if r.true_gh_id}
    pred = {(a, b) for a, b in zip(links["a_id"], links["b_id"]) if a in ids}
    tp = len(pred & truth)
    precision = tp / len(pred) if pred else 1.0
    recall = tp / len(truth) if truth else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "predicted": len(pred), "true": len(truth), "precision": precision, "recall": recall, "f1": f1}
