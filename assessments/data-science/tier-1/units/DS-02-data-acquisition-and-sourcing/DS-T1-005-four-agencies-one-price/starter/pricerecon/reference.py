"""R1: reference tables (markets, commodities, unit conversions)."""
from __future__ import annotations

from dataclasses import dataclass

CANONICAL_COLUMNS = ["source", "market_id", "commodity_id", "week_start", "price_ngn_per_kg", "flag"]
FLAGS = ("ok", "estimated", "missing")


class UnmappedLabel(ValueError):
    """A market, commodity or unit label that the reference tables do not know."""


def norm_label(s: str) -> str:
    """Normalise a label for lookup. Decide (and test) what differences must not matter."""
    raise NotImplementedError("R1: norm_label")


@dataclass
class Reference:
    markets: dict      # normalised alias -> market_id
    commodities: dict  # normalised alias -> commodity_id
    kg_per_unit: dict  # (commodity_id, normalised unit) -> float

    def market(self, label: str) -> str:
        """Canonical market_id for any known label; raise UnmappedLabel otherwise."""
        raise NotImplementedError("R1: Reference.market")

    def commodity(self, label: str) -> str:
        """Canonical commodity_id for any known label; raise UnmappedLabel otherwise."""
        raise NotImplementedError("R1: Reference.commodity")

    def kg(self, commodity_id: str, unit: str) -> float:
        """Kilograms per `unit` of this commodity from units.csv; raise UnmappedLabel if there is no factor."""
        raise NotImplementedError("R1: Reference.kg")


def load_reference(ref_dir) -> Reference:
    """Build a Reference from markets.csv, commodities.csv and units.csv in `ref_dir`. See README R1."""
    raise NotImplementedError("R1: load_reference")
