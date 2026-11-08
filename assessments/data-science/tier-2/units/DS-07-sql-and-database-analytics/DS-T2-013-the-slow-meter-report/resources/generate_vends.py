"""Deterministic generator for the prepaid-meter vend database (DS-T2-013).

    python generate_vends.py --out DIR --seed 2026 [--meters 150 --vends 3000]
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
import sqlite3
from pathlib import Path

FEEDERS = [("Agbara 11kV", "Ikeja"), ("Eleyele 33kV", "Ibadan"), ("Trans-Amadi 11kV", "Port Harcourt"),
           ("Gwarinpa 11kV", "Abuja"), ("Sabon Gari 33kV", "Kano"), ("GRA Enugu 11kV", "Enugu")]


def build(out: Path, seed: int, meters: int = 150, vends: int = 3000) -> Path:
    rng = random.Random(seed)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "vends.db"
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE feeders(feeder_id INTEGER PRIMARY KEY, name TEXT NOT NULL, zone TEXT NOT NULL);
    CREATE TABLE meters(meter_id INTEGER PRIMARY KEY, feeder_id INTEGER NOT NULL REFERENCES feeders, band TEXT NOT NULL);
    CREATE TABLE vends(vend_id INTEGER PRIMARY KEY, meter_id INTEGER NOT NULL REFERENCES meters, vended_on TEXT NOT NULL, kwh REAL NOT NULL, amount_ngn INTEGER NOT NULL);
    """)
    for i, (n, z) in enumerate(FEEDERS, 1):
        con.execute("INSERT INTO feeders VALUES (?,?,?)", (i, n, z))
    for m in range(1, meters + 1):
        con.execute("INSERT INTO meters VALUES (?,?,?)", (m, rng.randint(1, len(FEEDERS)), rng.choice(["A", "B", "C", "D"])))
    active = list(range(1, meters - 9))  # last 10 meters never vend
    start = dt.date(2025, 6, 1)
    rows = []
    for _ in range(vends):
        m = rng.choice(active)
        # busy and quiet spells: some days have no vends for a feeder
        d = start + dt.timedelta(days=int(rng.triangular(0, 120, 30)))
        amt = rng.choice([1000, 2000, 2000, 3000, 5000, 5000, 10000, 20000])
        rows.append((m, d.isoformat(), round(amt / rng.uniform(55, 70), 2), amt))
    rows.sort(key=lambda r: rng.random())  # vend_id order unrelated to date
    con.executemany("INSERT INTO vends(meter_id, vended_on, kwh, amount_ngn) VALUES (?,?,?,?)", rows)
    con.commit()
    con.close()
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--meters", type=int, default=150)
    ap.add_argument("--vends", type=int, default=3000)
    a = ap.parse_args()
    print(build(Path(a.out), a.seed, a.meters, a.vends))
