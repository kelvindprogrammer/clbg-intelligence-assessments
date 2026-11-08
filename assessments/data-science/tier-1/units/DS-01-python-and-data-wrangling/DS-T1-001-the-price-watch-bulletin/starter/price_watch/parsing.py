"""Cell-level parsing (requirements R1-R4).

Each function takes ONE raw text value from the bulletin and returns a clean Python value.
Write and test these first: everything else is built on them.
"""
from __future__ import annotations

from .schema import STATE_ZONES, ZONES  # noqa: F401  (you will need these)


def parse_price(cell: str) -> tuple[float, str]:
    """R1: parse one price cell into (value, status).

    status is one of "ok", "revised", "provisional", "not_collected", "not_available".
    Missing cells return float("nan") as the value. Surrounding whitespace is ignored.
    Values may or may not use thousands separators. Anything that is not a valid price
    cell (including an empty cell, a negative number, or stray text) raises ValueError.
    See README section D for the bulletin's notation.
    """
    raise NotImplementedError("R1: implement parse_price")


def parse_periods(year_cells: list[str], month_cells: list[str]) -> list[str | None]:
    """R2: turn a table's two header rows into one period label per column.

    year_cells and month_cells are the two header rows, cell for cell, same length.
    Return a list of the same length: "YYYY-MM" for every column that has a month
    label, and None for every other column (for example "State" and "Zone").
    The year is printed only above the first month of that year (a merged cell).
    Month labels may be abbreviated ("Sep"), four-letter ("Sept") or full ("September").
    Raise ValueError for an unknown month label or a month with no year before it.
    """
    raise NotImplementedError("R2: implement parse_periods")


def classify_label(label: str) -> tuple[str, str]:
    """R3: classify the first cell of a table body row.

    Return one of:
      ("state", <canonical state name from STATE_ZONES>)
      ("zone_average", <zone name from ZONES>)
      ("national_average", "National")
    State labels may carry a footnote marker such as " (a)", and the FCT is printed in
    more than one way. Raise ValueError for a label you cannot classify with certainty.
    """
    raise NotImplementedError("R3: implement classify_label")


def parse_unit(unit: str) -> tuple[float, str]:
    """R4: parse a unit description into (quantity, base_unit).

    base_unit is "kg", "litre" or "piece". Grams convert to kg and millilitres or
    centilitres to litres, so "500 g" -> (0.5, "kg") and "crate of 30" -> (30.0, "piece").
    Trailing words such as "bag" or "tin" do not change the quantity. Raise ValueError
    for a unit you cannot parse.
    """
    raise NotImplementedError("R4: implement parse_unit")
