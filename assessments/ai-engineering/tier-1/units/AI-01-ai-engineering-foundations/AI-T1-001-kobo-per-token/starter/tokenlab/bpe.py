"""Fill in every function. See README section D.1 for the exact rules (tie-breaking matters)."""
from __future__ import annotations

END = "</w>"


def train_bpe(corpus: list[str], num_merges: int) -> list[tuple[str, str]]:
    raise NotImplementedError("R1: learn up to num_merges merges from whitespace-split words")


def encode(text: str, merges: list[tuple[str, str]]) -> list[str]:
    raise NotImplementedError("R2: apply the merges, in learned order, to every word")


def decode(tokens: list[str]) -> str:
    raise NotImplementedError("R3: invert encode for whitespace-normalised text")


def build_vocab(corpus: list[str], merges: list[tuple[str, str]]) -> dict[str, int]:
    raise NotImplementedError("R4: base symbols sorted, then merged tokens in merge order")


def token_cost(text: str, merges: list[tuple[str, str]], kobo_per_1k_tokens: int) -> int:
    raise NotImplementedError("R5: integer kobo, rounded up")


def fertility(texts: list[str], merges: list[tuple[str, str]]) -> float:
    raise NotImplementedError("R6: tokens per whitespace-separated word over all texts")
