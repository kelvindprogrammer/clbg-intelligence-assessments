"""Synthetic waybill descriptions with a known category. Fictional; deterministic given the seed.

    python resources/waybills.py --out DIR --seed 2026      # writes waybills.csv (text,label)
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

ITEMS = {
    "electronics": ["phone chargers", "laptop batteries", "solar inverter", "LED bulbs", "router boxes", "power banks", "car stereo", "CCTV camera set"],
    "perishables": ["fresh tomatoes", "smoked catfish", "yam tubers", "pepper baskets", "frozen chicken", "ripe plantain", "palm oil kegs", "ogbono packs"],
    "documents": ["signed contracts", "land title copies", "exam scripts", "CAC certificates", "bank statements", "visa applications", "school transcripts", "tender bids"],
    "fashion": ["ankara bales", "lace fabric", "leather sandals", "school uniforms", "aso oke sets", "wigs and braids", "men's agbada", "head ties"],
    "building_materials": ["cement bags", "roofing sheets", "iron rods", "floor tiles", "paint buckets", "PVC pipes", "plywood boards", "door frames"],
}
PREFIX = ["", "", "urgent: ", "fragile - ", "for Kano depot: ", "Ref 22: ", "customer says "]
SUFFIX = ["", "", ", 2 cartons", ", 40 units", " to Onitsha", " for Ibadan market", ", handle with care", " (partial)"]


def _variant(s: str, rng: random.Random) -> str:
    r = rng.random()
    if r < 0.25:
        s = s.upper()
    elif r < 0.4:
        s = s.title()
    s = s.replace(" ", "  ") if rng.random() < 0.2 else s
    return " " + s + rng.choice(["", "", ".", "!!", " ."]) if rng.random() < 0.2 else s + rng.choice(["", "", ".", "!!"])


def make_waybills(n: int = 600, seed: int = 2026, dup_rate: float = 0.35):
    """Return (texts, labels). About `dup_rate` of rows repeat an earlier description with different formatting."""
    rng = random.Random(seed)
    cats = sorted(ITEMS)
    base: list[tuple[str, str]] = []
    texts, labels, seen = [], [], set()
    while len(texts) < n:
        if base and rng.random() < dup_rate:
            t, lab = rng.choice(base)
        else:
            lab = rng.choice(cats)
            qty = rng.choice(["", "3 ", "12 ", "50 ", "a few "])
            t = rng.choice(PREFIX) + qty + rng.choice(ITEMS[lab]) + rng.choice(SUFFIX)
            key = " ".join(t.lower().split()).strip(" .,;:!?")
            if key in seen:
                continue
            seen.add(key)
            base.append((t, lab))
        texts.append(_variant(t, rng))
        labels.append(lab)
    return texts, labels


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    t, l = make_waybills(seed=a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "waybills.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label"])
        w.writerows(zip(t, l))
