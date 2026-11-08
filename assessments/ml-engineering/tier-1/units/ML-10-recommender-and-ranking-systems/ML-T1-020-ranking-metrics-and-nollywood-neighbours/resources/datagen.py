"""Deterministic synthetic viewing log for a fictional Nigerian streaming app (ML-T1-020)."""
import numpy as np

GENRES = ["nollywood_drama", "afrobeats_concert", "comedy_skit", "faith_and_family", "football", "documentary"]


def make_views(n_users=600, n_items=120, seed=2026):
    """Return user, item, t (int arrays, sorted by t) and item_genre (n_items,). Each user favours one or two genres;
    items differ in popularity. About 8-25 views per user, no repeats."""
    rng = np.random.default_rng(seed)
    item_genre = np.arange(n_items) % len(GENRES)
    pop = rng.pareto(1.5, n_items) + 1.0
    U, I, T = [], [], []
    clock = 0
    for u in range(n_users):
        fav = rng.choice(len(GENRES), size=rng.integers(1, 3), replace=False)
        w = pop * np.where(np.isin(item_genre, fav), 30.0, 1.0)
        k = int(rng.integers(8, 26))
        items = rng.choice(n_items, size=k, replace=False, p=w / w.sum())
        times = np.sort(rng.integers(0, 10_000, k)) + clock
        U += [u] * k
        I += items.tolist()
        T += times.tolist()
        clock += 1
    order = np.argsort(np.array(T) * 1000 + np.array(U), kind="stable")
    return np.array(U)[order], np.array(I)[order], np.array(T)[order], item_genre


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    u, i, t, g = make_views(seed=a.seed)
    np.savetxt(os.path.join(a.out, "views.csv"), np.column_stack([u, i, t]), delimiter=",", fmt="%d", header="user,item,t", comments="")
