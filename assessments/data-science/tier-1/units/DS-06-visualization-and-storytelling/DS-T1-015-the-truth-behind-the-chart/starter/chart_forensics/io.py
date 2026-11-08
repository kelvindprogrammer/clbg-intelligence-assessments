"""Provided plumbing: load chart specs and their data. You do not need to change this file."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_spec(path) -> dict:
    """Read one chart spec (JSON) and remember which folder it came from."""
    path = Path(path)
    spec = json.loads(path.read_text(encoding="utf-8"))
    spec["_dir"] = str(path.parent)
    return spec


def load_data(spec: dict) -> pd.DataFrame:
    """Read the CSV named in spec["data"], in file order (the order is meaningful)."""
    return pd.read_csv(Path(spec["_dir"]) / spec["data"])


def load_gallery(folder) -> list[tuple[dict, pd.DataFrame]]:
    """Every (spec, data) pair in a gallery folder, sorted by chart id."""
    out = []
    for p in sorted(Path(folder).glob("*.json")):
        spec = load_spec(p)
        out.append((spec, load_data(spec)))
    return out
