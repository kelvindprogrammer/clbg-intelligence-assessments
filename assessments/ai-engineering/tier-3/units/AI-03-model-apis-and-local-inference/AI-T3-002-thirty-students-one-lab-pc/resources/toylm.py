"""A tiny language model with planted quantisation outliers, a workload generator and a serving cost model.

The model: logits = A[x] @ B  with A (V x d) and B (d x V).  It is built by factorising the log-transition
matrix of a synthetic Markov chain over V "syllables" (rank d), so fp perplexity on text sampled from the chain
is close to the chain's entropy.  Then `outlier_channels` feature channels are rescaled: column j of A is
multiplied by s and row j of B divided by s.  The function is IDENTICAL in floating point, but the weights now
contain large outliers, the situation that wrecks naive low-bit quantisation of real transformers.

Everything is synthetic and deterministic.  Nothing is downloaded.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def make_model(seed: int = 0, vocab: int = 48, rank: int = 24, outlier_channels: int = 3, outlier_scale: float = 30.0):
    rng = np.random.default_rng(seed)
    # clustered Markov chain: syllables belong to 6 groups; transitions favour a few groups
    grp = rng.integers(0, 6, vocab)
    aff = rng.gamma(0.4, 1.0, (6, 6))
    logit = aff[grp][:, grp] * 2.0 + rng.normal(0, 0.5, (vocab, vocab))
    P = np.exp(logit - logit.max(1, keepdims=True))
    P /= P.sum(1, keepdims=True)
    L = np.log(P)
    L = L - L.mean(1, keepdims=True)
    U, S, Vt = np.linalg.svd(L, full_matrices=False)
    A = U[:, :rank] * np.sqrt(S[:rank])
    B = np.sqrt(S[:rank])[:, None] * Vt[:rank]
    chans = rng.choice(rank, size=outlier_channels, replace=False) if outlier_channels else np.array([], int)
    for j in chans:
        A[:, j] *= outlier_scale
        B[j, :] /= outlier_scale
    return {"A": A.astype(np.float64), "B": B.astype(np.float64), "P": P, "outliers": sorted(int(j) for j in chans)}


def sample_tokens(model, n: int = 4000, seed: int = 1):
    rng = np.random.default_rng(seed)
    P = model["P"]
    cdf = np.cumsum(P, axis=1)
    x = np.empty(n, dtype=int)
    x[0] = rng.integers(0, P.shape[0])
    u = rng.random(n)
    for i in range(1, n):
        x[i] = min(int(np.searchsorted(cdf[x[i - 1]], u[i])), P.shape[0] - 1)
    return x


def perplexity(A, B, tokens) -> float:
    """exp(mean next-token negative log-likelihood) of softmax(A[x] @ B)."""
    z = A[tokens[:-1]] @ B
    z = z - z.max(1, keepdims=True)
    lp = z - np.log(np.exp(z).sum(1, keepdims=True))
    return float(np.exp(-lp[np.arange(len(tokens) - 1), tokens[1:]].mean()))


@dataclass(frozen=True)
class CostModel:
    """Analytic serving cost of a decoder model on a CPU lab PC.  Times in seconds, memory in GB (1e9 bytes).

    step time for a decode step with b live sequences:   weight_bytes(bits) / bandwidth + b * per_seq_s(bits)
    prefill time of a request:                            prompt_tokens * prefill_s_per_token(bits)
    memory:                                               weight_bytes(bits) + b * kv_gb_per_seq
    """
    n_params: float = 3e9
    bandwidth_gbps: float = 50.0
    kv_gb_per_seq: float = 0.25
    mem_cap_gb: float = 8.0
    per_seq_s: tuple = (0.004, 0.004, 0.0048)        # for bits 16, 8, 4 (int4 pays an unpacking penalty)
    prefill_s_per_token: tuple = (0.003, 0.003, 0.0036)

    def _i(self, bits):
        return {16: 0, 8: 1, 4: 2}[bits]

    def weight_gb(self, bits):
        return self.n_params * bits / 8 / 1e9

    def step_s(self, b, bits):
        return self.weight_gb(bits) / self.bandwidth_gbps + b * self.per_seq_s[self._i(bits)]

    def prefill_s(self, prompt_tokens, bits):
        return prompt_tokens * self.prefill_s_per_token[self._i(bits)]

    def memory_gb(self, b, bits):
        return self.weight_gb(bits) + b * self.kv_gb_per_seq


def make_workload(seed: int = 0, n: int = 300, rate_per_s: float = 0.5, burst: float = 0.0):
    """Student chat requests: (arrival_s, prompt_tokens, output_tokens) sorted by arrival.
    Poisson arrivals at `rate_per_s`; with burst > 0 a fraction `burst` of requests arrive in 10 s lecture-end bursts."""
    rng = np.random.default_rng(seed)
    gaps = rng.exponential(1.0 / rate_per_s, n)
    t = np.cumsum(gaps)
    if burst > 0:
        k = int(burst * n)
        idx = rng.choice(n, k, replace=False)
        t[idx] = rng.choice(t[:: max(1, n // 6)], k) + rng.random(k) * 10
        t.sort()
    prompt = np.clip(rng.lognormal(3.9, 0.5, n), 10, 400).astype(int)
    out = np.clip(rng.lognormal(3.7, 0.6, n), 5, 300).astype(int)
    return [(float(a), int(p), int(o)) for a, p, o in zip(t, prompt, out)]
