"""Deterministic mock of a hosted model API (no network, no key, no cost).

Every call consumes ONE event from `script`; when the script is exhausted the
provider behaves as "ok". Time is virtual: nothing ever really sleeps.

Events (strings):
  "ok"          valid JSON reply  {"intent": ..., "reply": ...}
  "fence"       the same JSON wrapped in a ```json ... ``` markdown fence
  "malformed"   a reply cut off mid-JSON (still billed: the model produced it)
  "rate:<s>"    RateLimitError with retry_after=<s> seconds (not billed)
  "timeout"     ProviderTimeout (not billed, but the call took `timeout_s`)
  "server"      ServerError (HTTP 5xx, not billed)
  "bad"         BadRequestError (HTTP 400, never worth retrying)
  "cut"         (stream=True only) two chunks, then the stream breaks
Prices are in kobo per 1,000 tokens. Token counts are whitespace words.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

INTENTS = ["balance_enquiry", "airtime_topup", "transfer_failed", "card_block", "loan_status"]


class VirtualClock:
    def __init__(self, start: float = 0.0):
        self.t = float(start)
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("negative sleep")
        self.sleeps.append(seconds)
        self.t += seconds


class ProviderError(Exception):
    pass


class RateLimitError(ProviderError):
    def __init__(self, retry_after: float):
        super().__init__(f"429 retry after {retry_after}s")
        self.retry_after = float(retry_after)


class ProviderTimeout(ProviderError):
    pass


class ServerError(ProviderError):
    pass


class BadRequestError(ProviderError):
    pass


@dataclass
class Response:
    text: str
    prompt_tokens: int
    completion_tokens: int


def n_tokens(text: str) -> int:
    return len(text.split())


class MockProvider:
    def __init__(self, script=None, clock: VirtualClock | None = None,
                 price_in: float = 30.0, price_out: float = 90.0,
                 latency_s: float = 0.4, timeout_s: float = 10.0):
        self.script = list(script or [])
        self.clock = clock or VirtualClock()
        self.price_in, self.price_out = price_in, price_out
        self.latency_s, self.timeout_s = latency_s, timeout_s
        self.calls: list[tuple[float, str]] = []      # (virtual time, event)

    def _event(self) -> str:
        return self.script.pop(0) if self.script else "ok"

    @staticmethod
    def _good_json(prompt: str) -> str:
        h = int(hashlib.sha256(prompt.encode()).hexdigest(), 16)
        intent = INTENTS[h % len(INTENTS)]
        return json.dumps({"intent": intent, "reply": f"Noted: {intent.replace('_', ' ')}."})

    def complete(self, prompt: str, max_tokens: int = 64, stream: bool = False):
        ev = self._event()
        self.calls.append((self.clock.now(), ev))
        if ev == "bad":
            self.clock.t += 0.05
            raise BadRequestError("400 invalid request")
        if ev == "timeout":
            self.clock.t += self.timeout_s
            raise ProviderTimeout("no reply")
        if ev == "server":
            self.clock.t += 0.1
            raise ServerError("503")
        if ev.startswith("rate:"):
            self.clock.t += 0.05
            raise RateLimitError(float(ev.split(":")[1]))
        good = self._good_json(prompt)
        text = {"ok": good, "fence": "```json\n" + good + "\n```",
                "malformed": good[: len(good) // 2], "cut": good}.get(ev, good)
        self.clock.t += self.latency_s
        if stream:
            return self._stream(text, ev == "cut")
        return Response(text, n_tokens(prompt), n_tokens(text))

    def _stream(self, text: str, cut: bool):
        chunks = [text[i:i + 8] for i in range(0, len(text), 8)]
        for i, c in enumerate(chunks):
            if cut and i == 2:
                raise ProviderTimeout("stream broke")
            yield c
