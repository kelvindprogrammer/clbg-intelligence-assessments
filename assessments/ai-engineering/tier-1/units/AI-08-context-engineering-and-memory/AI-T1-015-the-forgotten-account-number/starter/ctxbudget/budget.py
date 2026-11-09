"""Fill in every function. See README section D.1. A message is {"id", "role", "text", "pin"}; `system` is a string."""
from __future__ import annotations

OVERHEAD = 4  # tokens of framing the API adds around every message


def count_tokens(text: str) -> int:
    raise NotImplementedError("R1: count tokens with the rule given in the README")


def message_cost(msg: dict) -> int:
    raise NotImplementedError("R2: tokens of the text plus the per-message overhead")


def fit_window(system: str, messages: list[dict], budget: int, reply_reserve: int) -> dict:
    raise NotImplementedError("R3: keep pinned messages and the newest contiguous run that fits")


def compact(system: str, messages: list[dict], budget: int, reply_reserve: int, summariser) -> dict:
    raise NotImplementedError("R4: replace dropped history by one summary message inside the budget")


def facts_retained(context: list[dict], facts: list[str]) -> float:
    raise NotImplementedError("R5: fraction of facts still present in the context")


def budget_report(system: str, messages: list[dict], budget: int, reply_reserve: int) -> dict:
    raise NotImplementedError("R6: tokens by section and the free or missing space")
