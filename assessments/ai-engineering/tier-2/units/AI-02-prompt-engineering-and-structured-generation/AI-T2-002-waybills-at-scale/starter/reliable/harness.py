"""Fill in every function. See README section D.1. The numeric defaults below are a starting point, not a recommendation."""
from __future__ import annotations

DEFAULT_CFG = {
    "policy": {"max_attempts": 4, "base_delay": 1.0, "factor": 2.0, "max_delay": 8.0, "deadline": 30.0},
    "max_repairs": 2,
    "repair_mode": "feedback",      # "feedback" appends the errors to the prompt; "fresh" re-asks unchanged
    "refusal_retries": 1,
    "max_calls": 6,
    "screen_injection": True,
}


def build_prompt(doc: str, errors: list[str] | None = None) -> str:
    raise NotImplementedError("R1: instruction, schema, fenced document, optional rejection feedback")


def call_with_retries(llm, prompt: str, policy: dict, clock) -> dict:
    raise NotImplementedError("R2: retry only transient failures, with backoff and a deadline")


def check_record(text: str, source: str) -> tuple[dict | None, list[str]]:
    raise NotImplementedError("R3: refusal, parse, schema and grounding checks")


def extract_record(llm, doc: str, cfg: dict, clock) -> dict:
    raise NotImplementedError("R4: the full per-document pipeline")


def run_batch(llm, docs: list[dict], cfg: dict, clock) -> dict:
    raise NotImplementedError("R5: run all documents and summarise outcome, cost and latency")


def choose_config(llm_factory, docs: list[dict], min_ok_rate: float) -> dict:
    raise NotImplementedError("R6: cheapest config meeting the success bar on the development documents")
