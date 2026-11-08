"""Fixed output schemas, constants and provided loaders (identical in the public starter)."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

TIDY_COLUMNS = ["item", "unit", "state", "zone", "period", "price", "status",
                "unit_qty", "unit_base", "price_per_base"]
PUBLISHED_COLUMNS = ["item", "period", "area", "published"]
RECONCILE_COLUMNS = ["item", "period", "area", "published", "state_mean", "mean_of_zone_means", "match"]
STATUSES = {"ok", "revised", "provisional", "not_collected", "not_available"}
MATCHES = {"state_mean", "mean_of_zone_means", "both", "neither"}

# Published averages are rounded to the kobo (2 dp) at each stage, and the national
# figure can carry two roundings, so a recomputed value within 1 kobo "matches".
TOLERANCE = 0.01

# Provided reference data: the 36 states plus FCT and their geopolitical zones.
STATE_ZONES = {
    "Benue": "North Central", "FCT": "North Central", "Kogi": "North Central", "Kwara": "North Central",
    "Nasarawa": "North Central", "Niger": "North Central", "Plateau": "North Central",
    "Adamawa": "North East", "Bauchi": "North East", "Borno": "North East", "Gombe": "North East",
    "Taraba": "North East", "Yobe": "North East",
    "Jigawa": "North West", "Kaduna": "North West", "Kano": "North West", "Katsina": "North West",
    "Kebbi": "North West", "Sokoto": "North West", "Zamfara": "North West",
    "Abia": "South East", "Anambra": "South East", "Ebonyi": "South East", "Enugu": "South East",
    "Imo": "South East",
    "Akwa Ibom": "South South", "Bayelsa": "South South", "Cross River": "South South", "Delta": "South South",
    "Edo": "South South", "Rivers": "South South",
    "Ekiti": "South West", "Lagos": "South West", "Ogun": "South West", "Ondo": "South West",
    "Osun": "South West", "Oyo": "South West",
}
ZONES = sorted(set(STATE_ZONES.values()))


@dataclass
class RawTable:
    """One bulletin table after its page-break continuations have been merged.

    number:  the table number printed in the title ("Table 3: ..." -> 3)
    item:    the item name from the title, exactly as printed
    unit:    the unit text after "Unit: ", exactly as printed
    periods: one "YYYY-MM" string per price column, left to right
    body:    one row per state or average row, in bulletin order, with columns
             ["label", "zone"] + periods. Cells are the raw text, untouched.
    """
    number: int
    item: str
    unit: str
    periods: list[str]
    body: pd.DataFrame = field(repr=False)


def load_raw(path: str | Path) -> pd.DataFrame:
    """Provided: read the bulletin as a grid of text, exactly as exported.

    Every cell is a str (blank cells are ""). Columns are numbered 0..n-1 and
    no row is treated as a header. Nothing is converted, stripped or dropped.
    """
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    width = max((len(r) for r in rows), default=0)
    rows = [r + [""] * (width - len(r)) for r in rows]
    return pd.DataFrame(rows, dtype=object)

