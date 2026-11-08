"""Deterministic synthetic seven-segment meter digits for ML-T1-015 (fictional; no real meter)."""
import argparse
import numpy as np

SEG = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc", 8: "abcdefg", 9: "abcdfg"}


def glyph(d):
    """12x8 seven-segment glyph for digit d."""
    g = np.zeros((12, 8))
    for s in SEG[d]:
        if s == "a": g[0:2, 1:7] = 1
        if s == "g": g[5:7, 1:7] = 1
        if s == "d": g[10:12, 1:7] = 1
        if s == "f": g[0:6, 0:2] = 1
        if s == "b": g[0:6, 6:8] = 1
        if s == "e": g[6:12, 0:2] = 1
        if s == "c": g[6:12, 6:8] = 1
    return g


def make_digits(n=600, seed=0, noise=0.25, max_shift=2):
    """Return images (n,16,12) and labels (n,). Digit is shifted by up to max_shift px, dimmed, lit by a gradient and noisy."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 10, n)
    X = np.zeros((n, 16, 12))
    for i, d in enumerate(y):
        dy, dx = (2 + np.clip(rng.integers(0, 5, 2) - 2, -max_shift, max_shift)).astype(int)
        img = np.zeros((16, 12))
        img[dy:dy + 12, dx:dx + 8] = glyph(d) * rng.uniform(0.6, 1.0)
        img += rng.uniform(0, 0.2) * np.linspace(0, 1, 16)[:, None] + noise * rng.normal(size=img.shape)
        X[i] = img
    return X, y


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    X, y = make_digits(600, a.seed)
    np.savez_compressed(f"{a.out}/meter_digits_seed{a.seed}.npz", X=X, y=y)
