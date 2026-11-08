"""mcmc_lab (DS-T3-007): the minimal CONTRACT the automated tests import.

Everything else (module layout, adaptation, extra samplers, experiment code) is your design.
You may move these functions into submodules as long as they stay importable from
`mcmc_lab` and `mcmc_lab.model` with these names and signatures.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import model  # noqa: F401  (the model contract lives in mcmc_lab/model.py)


@dataclass
class SamplerResult:
    draws: np.ndarray          # (n_samples, dim), one row per iteration (rejected proposals repeat the state)
    accept_rate: float
    n_divergent: int = 0


def split_rhat(chains) -> float:
    """Rank-normalised split-R-hat of Vehtari et al. (2021): the maximum of the bulk and the
    folded (tail) version. `chains` is (n_chains, n_draws). Raises ValueError for non-2-D
    input or fewer than 4 draws per chain."""
    raise NotImplementedError("R1: implement split_rhat")


def ess_bulk(chains) -> float:
    """Bulk effective sample size of Vehtari et al. (2021): ESS of the rank-normalised split
    chains, with autocorrelations combined across chains and truncated by Geyer's initial
    monotone sequence."""
    raise NotImplementedError("R1: implement ess_bulk")


def rwm(logp, x0, n_samples: int, scale, rng: np.random.Generator) -> SamplerResult:
    """Random-walk Metropolis with Gaussian proposals of per-coordinate sd `scale`."""
    raise NotImplementedError("R2: implement rwm")


def hmc(logp_and_grad, x0, n_samples: int, step_size: float, n_leapfrog: int, rng: np.random.Generator,
        inv_mass=None) -> SamplerResult:
    """Hamiltonian Monte Carlo with leapfrog integration and a diagonal inverse mass matrix
    (default identity). logp_and_grad(x) -> (log density, gradient). Count a transition as
    divergent when the energy error is non-finite or larger than 1000; reject it."""
    raise NotImplementedError("R3: implement hmc")


def sbc_ranks(prior_draw, simulate, posterior_draws, n_sims: int, n_post: int, rng: np.random.Generator) -> np.ndarray:
    """Simulation-based calibration ranks (Talts et al. 2018).

    For each of n_sims simulations: theta = prior_draw(rng) (1-D array), data = simulate(theta, rng),
    draws = posterior_draws(data, n_post, rng) with shape (n_post, len(theta)); the rank of each
    component is the number of posterior draws strictly less than theta. Returns int array
    (n_sims, len(theta)) with values in 0..n_post."""
    raise NotImplementedError("R5: implement sbc_ranks")
