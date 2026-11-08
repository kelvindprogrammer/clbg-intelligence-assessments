"""Public requirement tests: they FAIL on the starter. They check the contract's correctness,
not your research. Tolerances are stated next to each check."""
import math

import numpy as np
import pytest

import mcmc_lab as ml
from mcmc_lab import model as M


def _ar1(phi, m, n, seed):
    rng = np.random.default_rng(seed)
    x = np.empty((m, n))
    x[:, 0] = rng.standard_normal(m) / math.sqrt(1 - phi ** 2)
    e = rng.standard_normal((m, n))
    for t in range(1, n):
        x[:, t] = phi * x[:, t - 1] + e[:, t]
    return x


# ---------------------------------------------------------------- R1 diagnostics
def test_rhat_iid_and_shifted():
    x = np.random.default_rng(1).standard_normal((4, 1000))
    assert ml.split_rhat(x) < 1.01
    y = x.copy()
    y[0] += 1.0                       # one chain stuck one sd away
    assert ml.split_rhat(y) > 1.05    # reference: 1.09; the recommended alarm level is 1.01


def test_folded_rhat_catches_scale_difference():
    rng = np.random.default_rng(2)
    x = rng.standard_normal((4, 1000))
    x[3] *= 3.0                       # same location, different scale: bulk R-hat misses it
    assert ml.split_rhat(x) > 1.05


def test_rhat_catches_within_chain_trend():
    x = np.random.default_rng(3).standard_normal((4, 1000)) + np.linspace(0, 2, 1000)
    assert ml.split_rhat(x) > 1.1      # only SPLIT chains see this


def test_ess_iid_and_ar1():
    iid = np.random.default_rng(4).standard_normal((4, 2000))
    assert ml.ess_bulk(iid) == pytest.approx(8000, rel=0.15)
    ar = _ar1(0.8, 4, 5000, 5)
    theory = 20000 * (1 - 0.8) / (1 + 0.8)        # about 2,222
    assert ml.ess_bulk(ar) == pytest.approx(theory, rel=0.25)


# ---------------------------------------------------------------- R2-R3 samplers
SIGMA = np.array([[1.0, 0.9], [0.9, 1.0]])
PREC = np.linalg.inv(SIGMA)


def _gauss(x):
    x = np.asarray(x, float)
    return -0.5 * x @ PREC @ x, -PREC @ x


def test_hmc_recovers_correlated_gaussian():
    res = ml.hmc(_gauss, np.zeros(2), 6000, 0.25, 12, np.random.default_rng(6))
    d = res.draws[500:]
    assert 0.6 < res.accept_rate <= 1.0 and res.n_divergent == 0
    assert np.abs(d.mean(axis=0)).max() < 0.1
    assert np.allclose(np.cov(d.T), SIGMA, atol=0.12)


def test_hmc_divergences_reported_for_absurd_step():
    res = ml.hmc(_gauss, np.zeros(2), 200, 5.0, 20, np.random.default_rng(7))
    assert res.n_divergent > 100 and res.accept_rate < 0.2


def test_rwm_normal():
    res = ml.rwm(lambda x: -0.5 * float(x @ x), np.zeros(1), 30000, 2.4, np.random.default_rng(8))
    d = res.draws[1000:, 0]
    assert abs(d.mean()) < 0.1 and d.var() == pytest.approx(1.0, rel=0.12)
    assert 0.3 < res.accept_rate < 0.6


# ---------------------------------------------------------------- R4 model
@pytest.mark.parametrize("centred", [False, True])
def test_gradient_matches_finite_differences(survey, centred):
    rng = np.random.default_rng(9)
    th = rng.normal(size=3 + survey.J) * 0.5
    lp, g = M.logp_and_grad(th, survey, centred)
    eps = 1e-6
    fd = np.array([(M.logp_and_grad(th + eps * e, survey, centred)[0] - M.logp_and_grad(th - eps * e, survey, centred)[0])
                   / (2 * eps) for e in np.eye(th.size)])
    assert np.abs(fd - g).max() < 1e-4 * max(1.0, np.abs(g).max())


def test_parameterisations_are_the_same_model(survey):
    """Same posterior: densities differ by the Jacobian of alpha = mu + tau * z, i.e. J * log_tau."""
    rng = np.random.default_rng(10)
    mu, beta, ltau = 0.3, -0.5, math.log(0.4)
    z = rng.standard_normal(survey.J)
    alpha = mu + math.exp(ltau) * z
    lp_nc, _ = M.logp_and_grad(np.r_[mu, beta, ltau, z], survey, False)
    lp_c, _ = M.logp_and_grad(np.r_[mu, beta, ltau, alpha], survey, True)
    lp_nc2, _ = M.logp_and_grad(np.r_[mu + 0.1, beta, ltau, z], survey, False)
    lp_c2, _ = M.logp_and_grad(np.r_[mu + 0.1, beta, ltau, alpha + 0.1], survey, True)
    assert (lp_c - lp_nc) == pytest.approx(lp_c2 - lp_nc2, abs=1e-8)
    assert (lp_c - lp_nc) == pytest.approx(-survey.J * ltau, abs=1e-8)


# ---------------------------------------------------------------- R5 SBC
def _conjugate(scale_factor):
    def prior(rng):
        return np.array([rng.normal(0, 1)])

    def sim(th, rng):
        return rng.normal(th[0], 1, size=5)

    def post(y, n, rng):
        v = 1 / (1 + y.size)
        return rng.normal(v * y.sum(), math.sqrt(v) * scale_factor, size=(n, 1))
    return prior, sim, post


def test_sbc_uniform_for_exact_posterior_and_not_for_overconfident():
    from scipy import stats
    for factor, expect_uniform in [(1.0, True), (0.5, False)]:
        prior, sim, post = _conjugate(factor)
        r = ml.sbc_ranks(prior, sim, post, 1000, 99, np.random.default_rng(11))
        assert r.shape == (1000, 1) and r.min() >= 0 and r.max() <= 99
        obs, _ = np.histogram(r[:, 0], bins=np.linspace(0, 100, 11))
        p = stats.chisquare(obs).pvalue
        assert (p > 0.001) if expect_uniform else (p < 1e-6)
