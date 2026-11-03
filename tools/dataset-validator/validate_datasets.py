#!/usr/bin/env python3
"""Validate the dataset registry and check that synthetic data generators are deterministic.

Checks:
  1. shared/datasets/registry.yaml entries have the required fields and unique IDs,
     and every `verified: true` entry has a `verified_on` date.
  2. Entries whose verification is older than --max-age-days are reported as due
     for manual re-verification (a warning only; see the procedure in DATASET_REGISTRY.md).
  3. Each assessment's `resources.data_generator` runs twice with the same seed
     and produces byte-identical output. Generator contract:
         python <generator> --out <DIR> --seed <INT>

Usage: python tools/dataset-validator/validate_datasets.py [--skip-generators] [--only ID ...]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import clbgtools as ct  # noqa: E402

REQUIRED = ["id", "name", "provider", "url", "license", "format", "modality", "domain", "units", "verified"]


def tree_hash(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(f.relative_to(d).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-generators", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--max-age-days", type=int, default=365)
    args = ap.parse_args(argv)
    errors, warnings = [], []

    reg_path = ct.ROOT / "shared" / "datasets" / "registry.yaml"
    reg = ct.load_yaml(reg_path) if reg_path.exists() else []
    if isinstance(reg, dict):
        reg = reg.get("datasets", [])
    seen = set()
    for e in reg or []:
        for k in REQUIRED:
            if k not in e:
                errors.append(f"registry {e.get('id', '?')}: missing '{k}'")
        if e.get("id") in seen:
            errors.append(f"registry: duplicate id {e.get('id')}")
        seen.add(e.get("id"))
        if e.get("verified"):
            try:
                d = dt.date.fromisoformat(str(e.get("verified_on")))
                if (dt.date.today() - d).days > args.max_age_days:
                    warnings.append(f"registry {e['id']}: verification older than {args.max_age_days} days, re-verify")
            except ValueError:
                errors.append(f"registry {e.get('id')}: verified but 'verified_on' is not an ISO date")
    print(f"Registry: {len(reg or [])} datasets checked.")

    n_gen = 0
    if not args.skip_generators:
        for a in ct.load_assessments():
            if args.only and a.id not in args.only:
                continue
            gen = (a.meta.get("resources") or {}).get("data_generator")
            if not gen:
                continue
            n_gen += 1
            hashes = []
            for _ in range(2):
                with tempfile.TemporaryDirectory() as tmp:
                    proc = subprocess.run([sys.executable, gen, "--out", tmp, "--seed", "2026"], cwd=a.path,
                                          capture_output=True, text=True, timeout=600)
                    if proc.returncode != 0:
                        errors.append(f"{a.id}: generator failed: {proc.stderr.strip()[-500:]}")
                        break
                    if not any(Path(tmp).iterdir()):
                        errors.append(f"{a.id}: generator produced no files")
                        break
                    hashes.append(tree_hash(Path(tmp)))
            if len(hashes) == 2 and hashes[0] != hashes[1]:
                errors.append(f"{a.id}: generator is not deterministic for a fixed seed")
            elif len(hashes) == 2:
                print(f"  {a.id}: generator deterministic ({hashes[0][:12]})")

    for w in warnings:
        print("warning", w)
    for e in errors:
        print("ERROR  ", e)
    print(f"Generators checked: {n_gen}. {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
