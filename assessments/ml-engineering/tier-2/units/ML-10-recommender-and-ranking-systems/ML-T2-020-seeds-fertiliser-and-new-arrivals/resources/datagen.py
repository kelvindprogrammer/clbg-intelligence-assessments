"""Deterministic synthetic purchase log for a fictional farm-input marketplace (ML-T2-020)."""
import numpy as np

CATS = ["seed", "fertiliser", "agrochemical", "tool", "feed", "irrigation"]


def make_purchases(n_farmers=800, seed=2026, days=335, cutoff=300):
    """Return a dict: user, item, t (int arrays sorted by t), item_attrs (n_items, 9), launch (n_items,), cold_items.
    150 items: 100 launched by day 200, 25 launched in days 265-274 (validation-era arrivals) and 25 launched in
    days 300-309 (arrivals after the cutoff; the test window is days 300-334). Farmers have 4 latent tastes; item_attrs holds a category one-hot, a
    price tier and two noisy taste coordinates. Arrivals get a 1.5x novelty boost. No farmer buys an item twice."""
    rng = np.random.default_rng(seed)
    n_items, d = 150, 4
    launch = np.r_[rng.integers(0, 200, 100), rng.integers(265, 275, 25), rng.integers(cutoff, cutoff + 10, 25)]
    cat = np.arange(n_items) % len(CATS)
    centres = rng.normal(0, 1.2, (len(CATS), d))
    V = centres[cat] + rng.normal(0, 0.5, (n_items, d))
    pop = rng.pareto(1.6, n_items) + 1.0
    price = rng.integers(0, 3, n_items).astype(float)
    attrs = np.column_stack([np.eye(len(CATS))[cat], price, V[:, :2] + rng.normal(0, 0.4, (n_items, 2))])
    U = rng.normal(0, 1, (n_farmers, d))
    users, items, times = [], [], []
    for u in range(n_farmers):
        k = int(rng.integers(10, 30))
        ts = np.sort(rng.integers(0, days, k))
        taste = np.exp(1.6 * (V @ U[u] / np.sqrt(d))) * pop
        seen = np.zeros(n_items, dtype=bool)
        for tt in ts:
            w = taste * (launch <= tt) * ~seen * np.where(tt - launch < 30, 1.5, 1.0)
            if w.sum() == 0:
                continue
            i = rng.choice(n_items, p=w / w.sum())
            seen[i] = True
            users.append(u), items.append(i), times.append(int(tt))
    order = np.argsort(times, kind="stable")
    return {"user": np.array(users)[order], "item": np.array(items)[order], "t": np.array(times)[order],
            "item_attrs": attrs, "launch": launch, "cold_items": np.flatnonzero(launch >= cutoff), "n_items": n_items,
            "n_users": n_farmers, "cutoff": cutoff}


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = make_purchases(seed=a.seed)
    np.savetxt(os.path.join(a.out, "purchases.csv"), np.column_stack([d["user"], d["item"], d["t"]]), delimiter=",", fmt="%d", header="farmer,item,day", comments="")
    np.savetxt(os.path.join(a.out, "items.csv"), np.column_stack([np.arange(d["n_items"]), d["launch"], d["item_attrs"]]), delimiter=",", fmt="%.4g",
               header="item,launch_day,cat_seed,cat_fert,cat_agro,cat_tool,cat_feed,cat_irrig,price_tier,taste_a,taste_b", comments="")
