"""Deterministic synthetic maize-leaf photos for ML-T2-014 (fictional, procedurally drawn)."""
import argparse
import numpy as np

CLASSES = ["healthy", "blight", "rust"]
N = 24
YY, XX = np.mgrid[0:N, 0:N]


def _blur3(img):
    p = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode="edge")
    return sum(p[i:i + N, j:j + N] for i in range(3) for j in range(3)) / 9.0


def _leaf(label, rng):
    img = np.empty((N, N, 3))
    img[:] = np.array([0.20, 0.55, 0.15]) * rng.uniform(0.85, 1.15)
    img += 0.04 * rng.normal(size=(N, N, 1))                                   # texture
    img[:, N // 2 - 1:N // 2 + 1] += 0.12                                      # midrib
    if label == 1:                                                             # blight: a few large dark-brown lesions
        for _ in range(rng.integers(1, 4)):
            cy, cx, r = rng.uniform(4, 20), rng.uniform(4, 20), rng.uniform(2.5, 5.0)
            m = (YY - cy) ** 2 + (XX - cx) ** 2 < r ** 2
            img[m] = np.array([0.38, 0.24, 0.10]) * rng.uniform(0.8, 1.2)
    if label == 2:                                                             # rust: many tiny orange pustules
        for _ in range(rng.integers(14, 30)):
            cy, cx = rng.uniform(1, 23), rng.uniform(1, 23)
            m = (YY - cy) ** 2 + (XX - cx) ** 2 < rng.uniform(0.5, 1.2) ** 2
            img[m] = np.array([0.80, 0.45, 0.10])
    if label == 0 and rng.random() < 0.3:                                      # healthy leaves also get dust specks
        for _ in range(rng.integers(1, 4)):
            cy, cx = rng.uniform(1, 23), rng.uniform(1, 23)
            img[(YY - cy) ** 2 + (XX - cx) ** 2 < 1.0] = np.array([0.30, 0.25, 0.15])
    return img


def make_leaves(n=300, seed=0, camera="lab"):
    """Return images (n,24,24,3) in [0,1] and labels (n,). camera is 'lab' (good light) or 'field' (dim, colour cast, blur, noise)."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 3, n)
    X = np.empty((n, N, N, 3))
    for i, c in enumerate(y):
        img = _leaf(c, rng)
        if camera == "field":
            img = _blur3(img) * rng.uniform(0.4, 0.8) * np.array([rng.uniform(1.0, 1.25), 1.0, rng.uniform(0.6, 0.9)])
            img = img + 0.05 * rng.normal(size=img.shape)
        else:
            img = img + 0.02 * rng.normal(size=img.shape)
        X[i] = np.clip(img, 0, 1)
    return X, y


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    for cam, n in (("lab", 400), ("field", 400)):
        X, y = make_leaves(n, a.seed, cam)
        np.savez_compressed(f"{a.out}/leaves_{cam}_seed{a.seed}.npz", X=X, y=y)
