"""Provided plumbing: download daily NASA POWER data for the cities in resources/cities.csv.

    python -m climate_story.fetch --out data/raw            # 1991-01-01 to 2024-12-31
    python -m climate_story.fetch --out data/raw --city Kano

Uses the public NASA POWER daily point API (no key needed). Each city is one request
of about 400 KB. The files are written exactly as POWER returns them, header included:
parsing them is your job (R1). Do not commit the downloaded files; commit the
download log (data/raw/FETCH_LOG.csv), which records the URL, time and SHA-256.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import time
import urllib.request
from pathlib import Path

API = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = "T2M_MAX,PRECTOTCORR"


def _cities(path: Path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def url_for(lat: float, lon: float, start: str = "19910101", end: str = "20241231") -> str:
    return (f"{API}?parameters={PARAMS}&community=AG&longitude={lon}&latitude={lat}"
            f"&start={start}&end={end}&format=CSV")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--cities", default=None, help="defaults to resources/cities.csv next to the package")
    ap.add_argument("--city", default=None)
    a = ap.parse_args(argv)
    here = Path(__file__).resolve()
    cities_file = Path(a.cities) if a.cities else next(p / "resources" / "cities.csv" for p in here.parents
                                                         if (p / "resources" / "cities.csv").is_file())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    log = out / "FETCH_LOG.csv"
    new = not log.exists()
    with log.open("a", newline="", encoding="utf-8") as lf:
        w = csv.writer(lf)
        if new:
            w.writerow(["city", "url", "fetched_utc", "sha256", "bytes"])
        for c in _cities(cities_file):
            if a.city and c["city"] != a.city:
                continue
            u = url_for(float(c["lat"]), float(c["lon"]))
            with urllib.request.urlopen(u, timeout=120) as r:
                body = r.read()
            dest = out / f"{c['city'].replace(' ', '_')}.csv"
            dest.write_bytes(body)
            w.writerow([c["city"], u, dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                        hashlib.sha256(body).hexdigest(), len(body)])
            print(f"{c['city']}: {len(body):,} bytes -> {dest}")
            time.sleep(1.0)  # be polite to a free public service
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
