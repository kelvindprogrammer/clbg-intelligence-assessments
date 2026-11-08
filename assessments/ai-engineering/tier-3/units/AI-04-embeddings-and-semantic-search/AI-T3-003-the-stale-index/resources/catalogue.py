"""Synthetic product-catalogue embeddings with planted cluster structure, head/tail queries and distribution drift.

All vectors are unit length. Nothing is stored in the repository; the generator makes them in milliseconds.
`python resources/catalogue.py --out DIR --seed 2026` writes a small summary JSON only.

    world = make_catalogue(seed)                 # dict: X (n,d), label, centers, tail_clusters
    Q, seg = make_queries(world, 200, seed)      # seg[i] in {'head','tail'}
    X_new  = make_drift(world, strength, m, seed)   # new arrivals; strength 0 = same distribution
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _unit(M):
    n = np.linalg.norm(M, axis=-1, keepdims=True)
    return M / np.maximum(n, 1e-12)


def make_catalogue(seed: int = 2026, n: int = 5000, d: int = 32, n_clusters: int = 40, sigma: float = 0.30):
    """Clusters have Zipf-like sizes; the smallest quarter are 'tail' clusters (niche products, rarer languages)."""
    rng = np.random.default_rng(seed)
    centers = _unit(rng.normal(size=(n_clusters, d)))
    w = 1.0 / np.arange(1, n_clusters + 1) ** 0.9
    w /= w.sum()
    label = rng.choice(n_clusters, size=n, p=w)
    X = _unit(centers[label] + sigma * rng.normal(size=(n, d)) / np.sqrt(d) * 3)
    tail = np.arange(n_clusters - n_clusters // 4, n_clusters)
    return dict(X=X, label=label, centers=centers, tail_clusters=tail, sigma=sigma, d=d)


def make_queries(world, n: int = 200, seed: int = 0, noise: float = 0.25):
    """Queries are noisy copies of catalogue items. Tail queries (from tail clusters) are noisier (x2)."""
    rng = np.random.default_rng(seed + 7)
    X, label = world["X"], world["label"]
    tail_mask = np.isin(label, world["tail_clusters"])
    rows = rng.choice(len(X), size=n)
    # ensure ~25% tail queries
    tail_rows = np.flatnonzero(tail_mask)
    sel = rng.random(n) < 0.25
    rows[sel] = rng.choice(tail_rows, size=int(sel.sum()))
    is_tail = tail_mask[rows]
    scale = np.where(is_tail, 2 * noise, noise)[:, None]
    Q = _unit(X[rows] + scale * rng.normal(size=(n, X.shape[1])) * 3 / np.sqrt(X.shape[1]))
    return Q, np.where(is_tail, "tail", "head")


def queries_from_rows(X, n: int, seed: int = 0, noise: float = 0.25):
    rng = np.random.default_rng(seed + 11)
    rows = rng.choice(len(X), size=n)
    return _unit(X[rows] + noise * rng.normal(size=(n, X.shape[1])) * 3 / np.sqrt(X.shape[1]))


def make_drift(world, strength: float, m: int = 1500, seed: int = 0):
    """New arrivals. With probability `strength` an item comes from a NEW cluster (a new product category);
    the remaining items come from existing clusters whose centres have moved by 0.35 * strength."""
    rng = np.random.default_rng(seed + 101)
    d, sigma = world["d"], world["sigma"]
    centers = world["centers"]
    new_centers = _unit(rng.normal(size=(8, d)))
    moved = _unit(centers + 0.35 * strength * rng.normal(size=centers.shape))
    from_new = rng.random(m) < strength
    cid_old = rng.integers(0, len(centers), size=m)
    cid_new = rng.integers(0, len(new_centers), size=m)
    base = np.where(from_new[:, None], new_centers[cid_new], moved[cid_old])
    return _unit(base + sigma * rng.normal(size=(m, d)) / np.sqrt(d) * 3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    w = make_catalogue(a.seed)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / "summary.json").write_text(json.dumps({"n": len(w["X"]), "d": w["d"], "clusters": int(w["label"].max()) + 1}), encoding="utf-8")
