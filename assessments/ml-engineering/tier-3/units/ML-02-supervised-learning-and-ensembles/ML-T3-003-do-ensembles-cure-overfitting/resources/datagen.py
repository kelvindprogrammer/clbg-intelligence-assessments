"""Deterministic synthetic cocoa-yield problem with a known truth (ML-T3-003)."""
import numpy as np


def f_true(X):
    """Noiseless yield index from rainfall (x0), temperature (x1), soil index (x2), shade (x3); extra columns are irrelevant."""
    X = np.asarray(X)
    return 4 * np.sin(2.5 * X[:, 0]) + 3 * (X[:, 1] > 0.5) * X[:, 2] + 16 * (X[:, 3] - 0.5) ** 2


def sample(n, seed, n_irrelevant=0, noise_sd=0.5):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, (n, 4 + n_irrelevant))
    return X, f_true(X) + rng.normal(0, noise_sd, n)


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    X, y = sample(2000, a.seed)
    np.savetxt(os.path.join(a.out, "cocoa.csv"), np.column_stack([X, y]), delimiter=",", fmt="%.5g",
               header="rainfall,temperature,soil_index,shade,yield_index", comments="")
