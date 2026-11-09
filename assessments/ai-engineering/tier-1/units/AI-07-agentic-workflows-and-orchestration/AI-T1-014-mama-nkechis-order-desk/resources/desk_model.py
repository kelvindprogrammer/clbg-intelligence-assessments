"""Deterministic rule-based mock 'language model' for AI-T1-014 (no network, no weights).

    model = DeskModel(fail_first=0)
    model.classify(text) -> {"intent": "order"|"complaint"|"other", "confidence": float}
    model.extract(text)  -> [{"item": str, "qty": int}, ...]      items in order of appearance
    model.calls          -> number of calls so far (classify + extract)

`fail_first=n` makes the first n calls raise TransientError (a timeout stand-in), then behave normally.
Names starting with an underscore are mock internals and must not be imported by a submission.
"""
import re

CATALOGUE = {"rice": 45000, "beans": 52000, "garri": 18000, "palm oil": 30000, "tomato paste": 9000}
COMPLAINT_WORDS = ("spoilt", "rotten", "refund", "late", "wrong", "short", "complain", "bad")
_ITEM = re.compile(r"(\d+)\s+(?:bags?|crates?|tins?|packs?|gallons?)\s+of\s+(palm oil|tomato paste|[a-z]+)", re.I)


class TransientError(Exception):
    """A retryable failure (timeout, 503)."""


class DeskModel:
    def __init__(self, fail_first: int = 0):
        self._fail = fail_first
        self.calls = 0

    def _tick(self):
        self.calls += 1
        if self._fail > 0:
            self._fail -= 1
            raise TransientError("model unavailable")

    def classify(self, text: str) -> dict:
        self._tick()
        low = text.lower()
        if any(w in low for w in COMPLAINT_WORDS):
            return {"intent": "complaint", "confidence": 0.9}
        if _ITEM.search(low) or re.search(r"\b(order|buy|send me)\b", low):
            return {"intent": "order", "confidence": 0.85}
        return {"intent": "other", "confidence": 0.6}

    def extract(self, text: str) -> list:
        self._tick()
        return [{"item": m.group(2).strip().lower(), "qty": int(m.group(1))} for m in _ITEM.finditer(text)]
