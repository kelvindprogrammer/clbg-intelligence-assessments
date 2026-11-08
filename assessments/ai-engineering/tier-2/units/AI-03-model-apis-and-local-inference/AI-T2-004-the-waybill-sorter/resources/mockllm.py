"""Deterministic mock of a hosted classification model with rate limits, outages and batch-position decay.

No network, no key, no cost. Time is virtual: `complete()` advances `clock` by the call latency.

The task the mock "performs": given a numbered list of waybill descriptions, reply with
    {"labels": ["fashion", "documents", ...]}      (one label per line, in order)

Behaviour you must engineer around (documented here, tuned in the constructor):
  * Sliding-window limits. A request sent at virtual time t counts against the provider for 60 s:
    it expires once now >= t + 60 - 1e-6. A request is rejected with RateLimitError (not billed, not
    counted) if it would make the number of live requests exceed `rpm`, or the live PROMPT tokens
    (plus this request's) exceed `tpm`. `retry_after` is the exact wait that would make it admissible.
    Every rejection increments `violations`.
  * Outages. Calls made while an `outages` window [t0, t1) is open raise ServerError after 0.5 s.
  * Malformed replies. A fixed, hash-chosen fraction `malformed_rate` of calls returns truncated JSON
    (billed, like a real provider).
  * Quality. The label at position p (0-based) inside a batch is correct with probability
    max(floor, acc - decay * max(0, p - free)). Which items are wrong is a deterministic hash of
    (seed, provider name, normalised text, p), so reruns are identical.
  * Billing. Prices are kobo per 1,000 tokens; tokens are whitespace words. `billed_kobo` accumulates.
  * Latency. base_s + per_token_s * (prompt + completion tokens).
"""
from __future__ import annotations

import hashlib
import json
import re

LABELS = ["electronics", "perishables", "documents", "fashion", "building_materials"]
INSTRUCTION = ("You are a freight clerk. Classify each numbered waybill description into exactly one of: "
               + ", ".join(LABELS) + ". Reply only with JSON of the form {\"labels\": [...]} "
               "with one label per line, in order.")
SLACK = 1e-6


def norm(text: str) -> str:
    """Cache/truth key: lowercase, collapse whitespace, strip ' .,;:!?' from both ends."""
    return " ".join(text.lower().split()).strip(" .,;:!?")


def build_prompt(texts) -> str:
    return INSTRUCTION + "\n" + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))


def n_tokens(text: str) -> int:
    return len(text.split())


class VirtualClock:
    def __init__(self, start: float = 0.0):
        self.t = float(start)

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("negative sleep")
        self.t += seconds


class ProviderError(Exception):
    pass


class RateLimitError(ProviderError):
    def __init__(self, retry_after: float):
        super().__init__(f"429 retry after {retry_after:.3f}s")
        self.retry_after = float(retry_after)


class ProviderTimeout(ProviderError):
    pass


class ServerError(ProviderError):
    pass


class Response:
    def __init__(self, text, prompt_tokens, completion_tokens):
        self.text, self.prompt_tokens, self.completion_tokens = text, prompt_tokens, completion_tokens


class MockProvider:
    def __init__(self, name, truth, clock, rpm=20, tpm=2500, price_in=20.0, price_out=60.0,
                 base_s=1.5, per_token_s=0.01, acc=0.985, decay=0.02, free=3, floor=0.6,
                 outages=(), malformed_rate=0.03, seed=0):
        self.name, self.truth, self.clock = name, truth, clock
        self.rpm, self.tpm = rpm, tpm
        self.price_in, self.price_out = price_in, price_out
        self.base_s, self.per_token_s = base_s, per_token_s
        self._acc, self._decay, self._free, self._floor = acc, decay, free, floor
        self.outages = [tuple(o) for o in outages]
        self.malformed_rate, self.seed = malformed_rate, seed
        self._live: list[tuple[float, int]] = []
        self.violations = 0
        self.billed_kobo = 0.0
        self.n_calls = 0           # accepted calls
        self.n_rejected = 0

    # -- helpers --------------------------------------------------------
    def _u(self, *parts) -> float:
        h = hashlib.sha256("|".join(map(str, (self.seed, self.name) + parts)).encode()).hexdigest()
        return int(h[:12], 16) / float(16 ** 12)

    def _p_correct(self, p: int) -> float:
        return max(self._floor, self._acc - self._decay * max(0, p - self._free))

    def _in_outage(self, t: float) -> bool:
        return any(a <= t < b for a, b in self.outages)

    # -- API ------------------------------------------------------------
    def complete(self, prompt: str, max_tokens: int = 256) -> Response:
        now = self.clock.now()
        if self._in_outage(now):
            self.clock.t += 0.5
            raise ServerError(f"503 from {self.name}")
        ptoks = n_tokens(prompt)
        live = [(t, k) for t, k in self._live if t + 60 - now > SLACK]
        self._live = live
        wait = 0.0
        if len(live) + 1 > self.rpm:
            wait = max(wait, live[len(live) - self.rpm][0] + 60 - now)
        total = sum(k for _, k in live) + ptoks
        i = 0
        while total > self.tpm and i < len(live):
            total -= live[i][1]
            wait = max(wait, live[i][0] + 60 - now)
            i += 1
        if wait > 0:
            self.violations += 1
            self.n_rejected += 1
            self.clock.t += 0.05
            raise RateLimitError(wait + SLACK)
        self._live.append((now, ptoks))
        self.n_calls += 1
        lines = re.findall(r"^\d+\.\s*(.*)$", prompt, re.M)
        labels = []
        for p, line in enumerate(lines):
            k = norm(line)
            true = self.truth.get(k, LABELS[0])
            if self._u("q", k, p) < self._p_correct(p):
                labels.append(true)
            else:
                others = [x for x in LABELS if x != true]
                labels.append(others[int(self._u("w", k, p) * len(others))])
        text = json.dumps({"labels": labels})
        if self._u("m", self.n_calls, prompt) < self.malformed_rate:
            text = text[: max(1, len(text) // 2)]
        ctoks = n_tokens(text)
        self.billed_kobo += (ptoks * self.price_in + ctoks * self.price_out) / 1000
        self.clock.t += self.base_s + self.per_token_s * (ptoks + ctoks)
        return Response(text, ptoks, ctoks)
