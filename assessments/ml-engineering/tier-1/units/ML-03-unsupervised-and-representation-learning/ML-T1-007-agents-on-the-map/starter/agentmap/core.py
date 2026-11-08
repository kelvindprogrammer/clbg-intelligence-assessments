"""Implement every function marked R<n>. numpy only (no scikit-learn inside this package)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class KMeansResult:
    centers: np.ndarray   # (k, d)
    labels: np.ndarray    # (n,) ints in 0..k-1
    inertia: float        # sum of squared distances to assigned centre
    n_iter: int           # Lloyd iterations used by the best restart


def load_points(path) -> np.ndarray:
    """Return an (n, 2) float array from demand_points.csv (columns x_km, y_km)."""
    data = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=(1, 2))
    return np.asarray(data, dtype=float)


def kmeans_pp_init(X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """R1: k-means++ seeding. First centre uniform; each next centre sampled with probability
    proportional to squared distance to the nearest chosen centre. Returns (k, d) copies of rows of X."""
    raise NotImplementedError("R1: k-means++ initialisation")


def assign(X: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """R2: index of the nearest centre for every row (ties go to the lowest index). Vectorised."""
    raise NotImplementedError("R2: nearest-centre assignment")


def update_centers(X: np.ndarray, labels: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """R3: new centres = cluster means. A cluster with no points is re-seeded to the point that is
    farthest from its currently assigned (old) centre; several empty clusters take distinct points,
    farthest first. Must not modify its inputs."""
    raise NotImplementedError("R3: centre update with empty-cluster repair")


def inertia(X: np.ndarray, centers: np.ndarray, labels: np.ndarray) -> float:
    """R4: sum of squared Euclidean distances from each point to its assigned centre."""
    raise NotImplementedError("R4: inertia")


def kmeans(X: np.ndarray, k: int, *, seed: int = 0, n_init: int = 5, max_iter: int = 100,
           tol: float = 1e-6) -> KMeansResult:
    """R5: Lloyd's algorithm with n_init restarts (k-means++ each); keep the lowest inertia.
    Stop a restart when the largest centre movement is < tol or after max_iter iterations.
    Deterministic given seed. Must not modify X."""
    raise NotImplementedError("R5: Lloyd iterations with restarts")


def silhouette_scores(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """R6: per-sample silhouette s = (b - a) / max(a, b); a = mean distance to the other members of
    its own cluster, b = smallest mean distance to another cluster. Singleton clusters score 0."""
    raise NotImplementedError("R6: silhouette")


def choose_k(X: np.ndarray, k_range, seed: int = 0):
    """R7: run kmeans for each k in k_range; return (best_k, table) where table is a list of dicts
    {"k", "inertia", "silhouette"} (silhouette = mean) in k_range order and best_k maximises silhouette."""
    raise NotImplementedError("R7: model selection by silhouette")
