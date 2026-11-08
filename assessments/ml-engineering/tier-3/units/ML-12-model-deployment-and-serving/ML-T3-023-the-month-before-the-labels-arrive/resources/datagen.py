"""Deterministic rollout test bench for a new credit-scoring model (fictional agent-banking lender; no real customers).

    python datagen.py --out DIR --seed 2026      # writes a small preview of candidates and one rollout log

The bench simulates a *candidate* model replacing a *champion*. Each day the controller sees only noisy observations and
answers "hold", "advance" or "rollback". The hidden truth (a candidate's real effect) is used only to score harm.
"""
import argparse
import json
import os

import numpy as np

STAGES = (0.0, 0.02, 0.10, 0.50, 1.0)       # stage 0 is shadow: the candidate scores traffic but decides nothing
PARAMS = dict(daily_requests=3000, seg_share=(0.75, 0.25), base_default=(0.08, 0.14), base_approval=(0.55, 0.45),
              label_lag=7, stages=STAGES, slo_ms=300.0, champ_p95=120.0, horizon=60, approval_shift=0.04)
KINDS = ("good", "neutral", "bad", "segment_bad", "slow")
HARMFUL = ("bad", "segment_bad", "slow")
MIX = (0.35, 0.15, 0.20, 0.20, 0.10)


def make_candidates(n, seed, mix=MIX, approval_shift=0.04):
    """List of hidden candidate descriptions. eff_s is the relative change in default rate among approved loans in
    segment s (0 = established customers, 1 = new-to-credit); app_s is the change in approval rate (absolute)."""
    rng = np.random.default_rng(seed)
    out = []
    for kind in rng.choice(KINDS, n, p=np.asarray(mix) / np.sum(mix)):
        j = rng.normal(0, 0.02, 2)
        if kind == "good":
            eff, app, lat = (-0.12 + j[0], -0.12 + j[1]), (rng.normal(0, 0.004), rng.normal(0, 0.004)), 125.0
        elif kind == "neutral":
            eff, app, lat = (j[0], j[1]), (rng.normal(0, 0.004), rng.normal(0, 0.004)), 125.0
        elif kind == "bad":
            loud = float(rng.random() < 0.5)         # half of the harmful models leave no trace in the approval rate
            eff, app, lat = (0.18 + j[0], 0.18 + j[1]), (loud * approval_shift, loud * approval_shift), 125.0
        elif kind == "segment_bad":
            loud = float(rng.random() < 0.5)
            eff, app, lat = (-0.10 + j[0], 0.40 + j[1]), (0.0, loud * 1.5 * approval_shift), 125.0
        else:   # slow
            eff, app, lat = (-0.10 + j[0], -0.10 + j[1]), (0.0, 0.0), 380.0 + 40 * rng.random()
        out.append(dict(kind=str(kind), eff=tuple(map(float, eff)), app=tuple(map(float, app)), p95=float(lat)))
    return out


class ScheduleController:
    """Baseline: advance every `days` days regardless of evidence. Never rolls back."""

    def __init__(self, info, days=4):
        self.days = days

    def decide(self, obs):
        return "advance" if obs["days_in_stage"] >= self.days else "hold"


def run_rollout(factory, cand, seed, params=None):
    P = dict(PARAMS, **(params or {}))
    rng = np.random.default_rng(seed)
    stages, lag, H = P["stages"], P["label_lag"], P["horizon"]
    info = dict(stages=stages, label_lag=lag, slo_ms=P["slo_ms"], horizon=H)
    ctrl = factory(info)
    z = lambda: [np.zeros(2), np.zeros(2)]
    champ = {k: np.zeros(2) for k in ("n", "app", "n_m", "d_m")}
    cd = {k: np.zeros(2) for k in ("n", "app", "n_m", "d_m")}
    sh = {k: np.zeros(2) for k in ("n", "app")}
    pending = []                                # (mature_day, seg, who, approved, defaults)
    stage, dis, harm, outcome, last = 0, 0, 0.0, "stalled", H
    pk = np.array(P["base_default"])
    pc = pk * (1 + np.array(cand["eff"]))
    ak = np.array(P["base_approval"])
    ac = ak + np.array(cand["app"])
    for day in range(H):
        frac = stages[stage]
        lat_c = lat_k = None
        for s in range(2):
            n = rng.binomial(P["daily_requests"], P["seg_share"][s])
            nc = rng.binomial(n, frac)
            nk = n - nc
            appk, appc = rng.binomial(nk, ak[s]), rng.binomial(nc, ac[s])
            champ["n"][s] += nk
            champ["app"][s] += appk
            cd["n"][s] += nc
            cd["app"][s] += appc
            sh["n"][s] += nk
            sh["app"][s] += rng.binomial(nk, ac[s])
            pending.append((day + lag, s, "k", appk, rng.binomial(appk, pk[s])))
            pending.append((day + lag, s, "c", appc, rng.binomial(appc, pc[s])))
            harm += appc * max(0.0, pc[s] - pk[s])
            if cand["p95"] > P["slo_ms"]:
                harm += 0.02 * nc
        rest = []
        for m, s, who, a, d in pending:
            if m <= day:
                tgt = champ if who == "k" else cd
                tgt["n_m"][s] += a
                tgt["d_m"][s] += d
            else:
                rest.append((m, s, who, a, d))
        pending = rest
        lat_c = cand["p95"] * float(np.exp(rng.normal(0, 0.08)))
        lat_k = P["champ_p95"] * float(np.exp(rng.normal(0, 0.08)))
        obs = dict(day=day, stage=stage, days_in_stage=dis, frac=frac,
                   champ={k: v.tolist() for k, v in champ.items()}, cand={k: v.tolist() for k, v in cd.items()},
                   shadow={k: v.tolist() for k, v in sh.items()}, lat_cand=lat_c, lat_champ=lat_k)
        act = ctrl.decide(obs)
        if act not in ("hold", "advance", "rollback"):
            raise ValueError(f"invalid action {act!r}")
        dis += 1
        if act == "rollback":
            outcome, last = "rolled_back", day + 1
            break
        if act == "advance":
            if stage == len(stages) - 1:
                outcome, last = "promoted", day + 1
                break
            stage, dis = stage + 1, 0
    return dict(outcome=outcome, days=last, harm=float(harm), stage=stage)


def evaluate(factory, n=150, seed=2026, params=None, mix=MIX, approval_shift=0.04):
    """Score a controller on n hidden candidates. harm_ratio compares with the fixed-schedule baseline."""
    cands = make_candidates(n, seed, mix, approval_shift)
    rows = []
    for i, c in enumerate(cands):
        r = run_rollout(factory, c, seed * 1000 + i, params)
        b = run_rollout(ScheduleController, c, seed * 1000 + i, params)
        rows.append((c["kind"], r, b))
    kinds = np.array([k for k, _, _ in rows])
    harmful = np.isin(kinds, HARMFUL)
    good = kinds == "good"
    rolled = np.array([r["outcome"] == "rolled_back" for _, r, _ in rows])
    promoted = np.array([r["outcome"] == "promoted" for _, r, _ in rows])
    days = np.array([r["days"] for _, r, _ in rows])
    total = sum(r["harm"] for _, r, _ in rows)
    base = sum(b["harm"] for _, _, b in rows)
    return dict(caught=float(rolled[harmful].mean()) if harmful.any() else 1.0,
                harmful_promoted=float(promoted[harmful].mean()) if harmful.any() else 0.0,
                good_promoted=float(promoted[good].mean()) if good.any() else 1.0,
                good_median_days=float(np.median(days[good & promoted])) if (good & promoted).any() else float("inf"),
                harm=float(total), baseline_harm=float(base), harm_ratio=float(total / max(base, 1e-9)),
                per_kind={k: dict(n=int((kinds == k).sum()), rolled_back=float(rolled[kinds == k].mean()),
                                  promoted=float(promoted[kinds == k].mean())) for k in KINDS if (kinds == k).any()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "candidates_preview.json"), "w") as f:
        json.dump(make_candidates(10, a.seed), f, indent=1)
    r = run_rollout(ScheduleController, make_candidates(1, a.seed)[0], a.seed)
    with open(os.path.join(a.out, "baseline_rollout.json"), "w") as f:
        json.dump(r, f)


if __name__ == "__main__":
    main()
