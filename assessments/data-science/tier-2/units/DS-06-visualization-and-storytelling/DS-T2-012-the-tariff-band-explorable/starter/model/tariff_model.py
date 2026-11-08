"""The household energy-cost model behind the explorable (the contract).

You design the model, but `monthly_cost` must keep this signature and return these keys,
because the tests check its behaviour (monotonicity, edge cases, validation).
Mirror the same logic in your explorable's JavaScript, or generate the explorable's data from it.
"""
from __future__ import annotations

RETURN_KEYS = ("grid_kwh", "grid_cost_ngn", "backup_kwh", "backup_cost_ngn", "unserved_kwh",
               "total_cost_ngn", "effective_ngn_per_kwh")


def load_tariffs(path) -> dict[str, float]:
    """Read data/tariffs.csv and return {band: NGN per kWh} for bands A-E."""
    raise NotImplementedError("R1: implement load_tariffs")


def monthly_cost(household: dict, scenario: dict) -> dict:
    """R2: one household's monthly electricity cost under one policy scenario.

    household: {"demand_kwh": float >= 0 (monthly), "band": "A".."E", "supply_hours": 0..24 (grid hours per day)}
    scenario:  {"tariffs": {band: NGN/kWh}, "backup_ngn_per_kwh": float >= 0, "backup_share": 0..1
                (the share of demand not met by the grid that the household covers with a generator or other backup)}

    Returns a dict with exactly RETURN_KEYS. Raise ValueError for an unknown band or out-of-range inputs.
    """
    raise NotImplementedError("R2: implement monthly_cost")
