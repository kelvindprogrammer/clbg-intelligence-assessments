"""Deterministic synthetic logistic problems with controlled conditioning (ML-T3-001)."""
import numpy as np


def make_logistic(n=1500, d=8, kappa=100.0, seed=0, kind="scale"):
    """Columns have scales geometrically spaced from 1 to sqrt(kappa) (Hessian condition number ~ kappa).

    kind='scale'   : axis-aligned ill-conditioning (a diagonal rescaling can undo it).
    kind='rotated' : the same spectrum rotated by a random orthogonal matrix (correlated columns).
    Labels follow a logistic model, so the problem is not separable and f* is finite.
    """
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(n, d))
    s = np.geomspace(1.0, np.sqrt(kappa), d)
    X = Z * s
    if kind == "rotated":
        Q, _ = np.linalg.qr(rng.normal(size=(d, d)))
        X = X @ Q
    elif kind != "scale":
        raise ValueError(kind)
    w = rng.normal(size=d) / s * 0.8
    p = 1.0 / (1.0 + np.exp(-(X @ (Q.T @ w if kind == "rotated" else w))))
    y = (rng.random(n) < p).astype(float)
    return X, y


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--kappa", type=float, default=100.0)
    ap.add_argument("--kind", default="scale")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    X, y = make_logistic(1500, 8, a.kappa, a.seed, a.kind)
    np.savetxt(os.path.join(a.out, "problem.csv"), np.column_stack([X, y]), delimiter=",", fmt="%.6g",
               header=",".join(f"x{i}" for i in range(X.shape[1])) + ",y", comments="")
