"""rainprice: rainfall-anomaly and food-price exploration for DS-T2-007.

Fixed contract: `build_register(panel, ...) -> DataFrame` with REGISTER_COLUMNS.
Everything else in your package is your own design.
"""
from .io import REGISTER_COLUMNS, STATUSES, Panel, load_panel, score_register, validate_register
from .baseline import naive_register
from .register import build_register

__all__ = ["REGISTER_COLUMNS", "STATUSES", "Panel", "load_panel", "score_register", "validate_register",
           "naive_register", "build_register"]
