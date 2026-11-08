"""Deterministic synthetic daily cash-out volumes for POS/mobile-money agents (ML-T2-018, fictional)."""
import numpy as np

PROFILE = np.array([1.0, 1.05, 1.0, 1.1, 1.25, 1.3, 0.7])     # Monday..Sunday


def make_demand(n_agents=30, T=300, seed=2026):
    """Return Y (n_agents, T) in thousands of naira and cal = dict(dow, payday, eve), each of length T.
    Day 0 is a Monday; months are 30 days; payday window is day-of-month 24..27; `eve` marks public-holiday eves
    (known in advance). Each agent has its own market day, scale, and occasional closed days (zero volume)."""
    rng = np.random.default_rng(seed)
    t = np.arange(T)
    dow, dom = t % 7, t % 30
    payday = ((dom >= 24) & (dom <= 27)).astype(float)
    eve = np.zeros(T)
    eve[rng.choice(np.arange(10, T - 40), 8, replace=False)] = 1.0
    eve[T - 10] = 1.0
    base = np.exp(rng.normal(3.7, 0.7, n_agents))
    market = rng.integers(0, 7, n_agents)
    prof = PROFILE[None, :] * (1 + 0.6 * (np.arange(7)[None, :] == market[:, None]))
    mean = base[:, None] * prof[:, dow] * (1 + 0.001 * t)[None, :] * (1 + 0.7 * payday)[None, :] * (1 + 0.9 * eve)[None, :]
    Y = mean * np.exp(rng.normal(0, 0.3, mean.shape))
    Y[rng.random(Y.shape) < 0.02] = 0.0
    return Y, {"dow": dow, "payday": payday, "eve": eve}


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    Y, cal = make_demand(seed=a.seed)
    np.savetxt(os.path.join(a.out, "agent_cashout.csv"), np.vstack([cal["dow"], cal["payday"], cal["eve"], Y]).T, delimiter=",", fmt="%.4g",
               header=",".join(["dow", "payday", "eve"] + [f"agent_{i:02d}" for i in range(Y.shape[0])]), comments="")
