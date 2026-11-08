"""Deterministic synthetic aerial roof tiles for ML-T3-013 (fictional villages, procedurally drawn)."""
import argparse
import numpy as np

CLASSES = ["metal_sheet", "thatch", "concrete_tile"]
S = 20


def _roof(label, rng):
    r = np.zeros((12, 12, 3))
    yy, xx = np.mgrid[0:12, 0:12]
    if label == 0:                                   # corrugated metal: bright, regular ridges, one orientation
        period = rng.integers(2, 4)
        ridge = ((xx if rng.random() < 0.5 else yy) % period == 0).astype(float)
        r[:] = np.array([0.56, 0.58, 0.60]) + 0.12 * ridge[..., None]
        r += 0.03 * rng.normal(size=r.shape)
    elif label == 1:                                 # thatch: brown/yellow, strong fine texture
        r[:] = np.array([0.54, 0.48, 0.36])
        r += 0.10 * rng.normal(size=r.shape[:2] + (1,)) + 0.05 * rng.normal(size=r.shape)
    else:                                            # concrete tile: flat mid grey with coarse grid seams
        r[:] = np.array([0.56, 0.55, 0.52])
        seam = ((xx % 6 == 0) | (yy % 6 == 0)).astype(float)
        r -= 0.12 * seam[..., None]
        r += 0.03 * rng.normal(size=r.shape)
    return r


def make_tiles(n_villages=24, per_village=40, seed=0):
    """Return X (N,20,20,3) in [0,1], y (N,), village (N,). Each village has its own lighting, tint, ground colour,
    sensor noise and a dominant roof material (80% of its roofs)."""
    rng = np.random.default_rng(seed)
    Xs, ys, vs = [], [], []
    for v in range(n_villages):
        gain, tint = rng.uniform(0.5, 1.4), rng.normal(1.0, 0.15, 3)
        dom = rng.integers(0, 3)
        ground = np.array([[0.45, 0.40, 0.30], [0.30, 0.38, 0.22], [0.50, 0.44, 0.38]][dom]) * rng.uniform(0.8, 1.2, 3)
        sig = rng.uniform(0.03, 0.10)
        for _ in range(per_village):
            lab = dom if rng.random() < 0.8 else rng.integers(0, 3)
            img = np.empty((S, S, 3)); img[:] = ground
            img += 0.04 * rng.normal(size=img.shape)
            oy, ox = rng.integers(2, 7, 2)
            img[oy:oy + 12, ox:ox + 12] = _roof(lab, rng)
            img = np.clip(img * gain * tint + sig * rng.normal(size=img.shape), 0, 1)
            Xs.append(img); ys.append(lab); vs.append(v)
    return np.array(Xs), np.array(ys), np.array(vs)


def label_budget(y, village, n_villages=8, n_per_class=20, seed=0, exclude=()):
    """Indices of a small labelled set: n_per_class tiles of each class drawn from n_villages random villages (never from `exclude`)."""
    rng = np.random.default_rng(seed)
    vs = rng.choice(np.setdiff1d(np.unique(village), np.asarray(exclude, dtype=int)), n_villages, replace=False)
    pool = np.flatnonzero(np.isin(village, vs))
    return np.sort(np.concatenate([rng.choice(pool[y[pool] == c], min(n_per_class, int((y[pool] == c).sum())), replace=False) for c in range(3)]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    X, y, v = make_tiles(24, 40, a.seed)
    np.savez_compressed(f"{a.out}/roof_tiles_seed{a.seed}.npz", X=X.astype(np.float32), y=y, village=v)
