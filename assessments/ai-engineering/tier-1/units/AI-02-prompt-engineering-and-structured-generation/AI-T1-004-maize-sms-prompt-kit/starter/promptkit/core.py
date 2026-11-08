"""Fill in every function. See README section D.1 for the exact rules."""
from __future__ import annotations


class PromptError(ValueError):
    """Raised for malformed templates, variables or budgets."""


class ParseError(ValueError):
    """Raised when no JSON object can be extracted from a model reply."""


def render(template: str, **variables) -> str:
    raise NotImplementedError("R1: strict {{name}} substitution, single pass")


def fence(text: str, tag: str = "FARMER") -> str:
    raise NotImplementedError("R2: neutralise embedded markers, then wrap in <<<TAG ... TAG>>>")


def select_shots(examples: list[dict], query: str, k: int) -> list[dict]:
    raise NotImplementedError("R3: k most similar examples, most similar last")


def build_prompt(instruction: str, shots: list[dict], query: str) -> str:
    raise NotImplementedError("R4: assemble instruction, shots and the fenced query")


def build_prompt_within(instruction: str, shots: list[dict], query: str, max_words: int) -> str:
    raise NotImplementedError("R5: drop the least similar shots until the prompt fits")


def extract_json(text: str) -> dict:
    raise NotImplementedError("R6: first balanced span that parses as a JSON object")


def validate(obj: dict, schema: dict) -> list[str]:
    raise NotImplementedError("R7: sorted list of error strings, empty when valid")


def triage(llm, message: str, examples: list[dict], schema: dict, instruction: str, k: int = 3) -> dict:
    raise NotImplementedError("R8: prompt, call, parse, validate; never raise on model misbehaviour")
