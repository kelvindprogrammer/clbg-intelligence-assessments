"""Deterministic synthetic data for ML-T1-004 (fictional cassava plots)."""
import numpy as np

FEATURES = ["mosaic_score", "whitefly_count", "rain_mm", "soil_ph", "age_weeks"]


def make_cassava(n=600, seed=2026):
    """Return X (n, 5) and y in {0: healthy, 1: CMD, 2: CBB}. Continuous features, so ties are essentially absent."""
    rng = np.random.default_rng(seed)
    mosaic = rng.gamma(2.0, 1.4, n).clip(0, 10)
    whitefly = rng.gamma(2.5, 6.0, n)
    rain = rng.gamma(4.0, 20.0, n)
    ph = rng.normal(5.8, 0.6, n)
    age = rng.uniform(4, 40, n)
    score_cmd = 0.9 * (mosaic - 4) + 0.04 * (whitefly - 15) + rng.normal(0, 1.0, n)
    score_cbb = 0.025 * (rain - 90) + 0.6 * (ph - 5.8) * -1 + 0.03 * (age - 20) + rng.normal(0, 1.0, n)
    y = np.where((score_cmd < 0.6) & (score_cbb < 0.6), 0, np.where(score_cmd >= score_cbb, 1, 2))
    return np.column_stack([mosaic, whitefly, rain, ph, age]), y.astype(int)


def make_xor(n=800, seed=2026):
    """Two uniform features; class is 1 iff exactly one coordinate exceeds 0.5 (an interaction)."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, (n, 2))
    return X, ((X[:, 0] > 0.5) ^ (X[:, 1] > 0.5)).astype(int)


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    X, y = make_cassava(600, a.seed)
    np.savetxt(os.path.join(a.out, "cassava.csv"), np.column_stack([X, y]), delimiter=",", fmt="%.5g",
               header=",".join(FEATURES + ["label"]), comments="")
