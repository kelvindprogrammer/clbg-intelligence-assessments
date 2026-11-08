"""Claim-checking toolkit for a school-meals attendance survey. Implement R1-R7. `load_export` is provided."""
from __future__ import annotations

import pandas as pd


def load_export(path) -> pd.DataFrame:
    """Provided. Columns: school_id, group ('programme' | 'comparison'), period ('before' | 'after'), pupil_id,
    regular (1 if the pupil attended at least 80% of school days, else 0)."""
    return pd.read_csv(path, dtype={"school_id": str, "group": str, "period": str, "pupil_id": str})


def wilson_ci(k: int, n: int, level: float = 0.95) -> tuple:
    """R1: Wilson score interval for a proportion k/n. With z = NormalDist().inv_cdf(0.5 + level/2) (standard
    library), p = k/n: centre = (p + z^2/(2n)) / (1 + z^2/n); half = z * sqrt(p(1-p)/n + z^2/(4n^2)) / (1 + z^2/n).
    Return (max(0, centre-half), min(1, centre+half)) as floats, with the lower bound exactly 0.0 when k == 0 and the
    upper bound exactly 1.0 when k == n (avoid floating-point residue)."""
    raise NotImplementedError("R1: wilson_ci")


def diff_in_proportions(k1: int, n1: int, k2: int, n2: int, level: float = 0.95) -> tuple:
    """R2: Wald interval for p1 - p2 with the UNPOOLED standard error sqrt(p1(1-p1)/n1 + p2(1-p2)/n2).
    Return (difference, lower, upper)."""
    raise NotImplementedError("R2: diff_in_proportions")


def bootstrap_ci(values, stat, n_boot: int = 2000, seed: int = 0, level: float = 0.95) -> tuple:
    """R3: percentile bootstrap. rng = numpy.random.default_rng(seed); for each of n_boot iterations draw
    idx = rng.integers(0, n, n) (n = len(values)) and compute stat(values[idx]). Return the (1-level)/2 and
    (1+level)/2 quantiles (np.quantile, default method) of the n_boot statistics as floats."""
    raise NotImplementedError("R3: bootstrap_ci")


def cluster_did(df: pd.DataFrame, n_boot: int = 2000, seed: int = 0, level: float = 0.95) -> dict:
    """R4: difference-in-differences of the share of regular attenders, with a school-level (cluster) bootstrap.
    programme_change = pooled after-rate minus pooled before-rate over the programme pupils; comparison_change
    likewise; estimate = programme_change - comparison_change.
    Naive interval: Wald, treating every pupil as independent: se = sqrt(sum over the four group-period cells of
    p(1-p)/n); estimate +- z*se.
    Cluster interval: rng = default_rng(seed). In each of n_boot iterations resample the programme schools with
    replacement (schools sorted by school_id; draw rng.integers(0, k, k)), THEN the comparison schools the same way;
    pool the pupils of the resampled schools to recompute each change; store the difference. Interval = the percentile
    quantiles of the n_boot values.
    Return a dict with keys: estimate, lo, hi (cluster interval), naive_lo, naive_hi, programme_change,
    comparison_change, width_ratio ((hi - lo) / (naive_hi - naive_lo))."""
    raise NotImplementedError("R4: cluster_did")


def verdict(result: dict, claimed: float | None = None) -> str:
    """R5: judge the press release's causal claim using the cluster interval in `result`. `claimed` defaults to
    result['programme_change'] (the raw before/after rise the release reports). Return 'inconclusive' if the
    interval contains 0; else 'supported' if it contains `claimed`; else 'overstated'."""
    raise NotImplementedError("R5: verdict")


def write_manifest(path, data_path, seed: int) -> dict:
    """R6: write (and return) a JSON reproducibility manifest with keys data_sha256 (SHA-256 of the data file's
    bytes), seed, n_rows (rows in the data), python (platform.python_version()), pandas (pandas.__version__).
    Write with sort_keys=True so the file is byte-identical across runs on the same machine."""
    raise NotImplementedError("R6: write_manifest")
