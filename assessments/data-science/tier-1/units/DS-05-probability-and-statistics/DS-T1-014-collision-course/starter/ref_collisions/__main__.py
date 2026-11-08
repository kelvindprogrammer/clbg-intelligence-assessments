"""CLI (requirement R8): python -m ref_collisions <booking_refs.csv> --out <dir>."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from . import (ALPHABET, char_uniformity_pvalue, count_colliding_pairs, estimate_space_size,
               excess_collision_pvalue, expected_colliding_pairs, min_code_length)

DESIGNED_SPACE = len(ALPHABET) ** 6


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ref_collisions")
    ap.add_argument("refs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--network-per-day", type=int, default=120_000)
    ap.add_argument("--collision-risk", type=float, default=0.01)
    ap.add_argument("--guesses", type=int, default=10_000)
    ap.add_argument("--guess-risk", type=float, default=1e-3)
    args = ap.parse_args(argv)
    df = pd.read_csv(args.refs, dtype=str)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    days = {}
    for day, g in df.groupby("date"):
        codes = list(g["ref"])
        days[day] = {"n": len(codes), "pairs": count_colliding_pairs(codes),
                     "expected_pairs_designed": expected_colliding_pairs(len(codes), DESIGNED_SPACE),
                     "p_value_designed": excess_collision_pvalue(codes, DESIGNED_SPACE)}
    est = estimate_space_size(df["ref"])
    evidence = {
        "designed_space": DESIGNED_SPACE,
        "days": days,
        "pooled": {"n": est.n, "pairs": est.pairs, "n_hat": est.n_hat, "lower": est.lower, "upper": est.upper},
        "char_uniformity_pvalue": char_uniformity_pvalue(df["ref"]),
        "recommended_length": min_code_length(len(ALPHABET), args.network_per_day, args.collision_risk,
                                              guesses=args.guesses, guess_risk=args.guess_risk),
        "recommended_length_collision_only": min_code_length(len(ALPHABET), args.network_per_day, args.collision_risk),
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
