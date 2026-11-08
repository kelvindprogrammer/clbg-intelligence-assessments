"""Quantisation, serving simulation and a recommendation for the lab-PC study. Signatures are fixed."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class QTensor:
    """Quantised tensor. `q` holds int8 codes, `scale` one float per block (so `scale.size` = number of blocks).
    Layout of `q` and `scale` is yours, as long as dequantize() reverses it."""
    q: np.ndarray
    scale: np.ndarray
    bits: int
    shape: tuple
    axis: int | None
    group: int | None


@dataclass
class SimResult:
    latencies: list          # completion - arrival, in the ORDER OF THE INPUT requests
    makespan: float          # last completion - first arrival
    throughput_tok_s: float  # total output tokens / makespan
    p50: float
    p95: float               # numpy percentile, linear interpolation


def quantize(w, bits: int, axis: int | None = None, group: int | None = None) -> QTensor:
    """R1: symmetric round-to-nearest quantisation. See README for the exact block definition."""
    raise NotImplementedError("R1: quantize")


def dequantize(qt: QTensor) -> np.ndarray:
    """R1: back to float with the original shape."""
    raise NotImplementedError("R1: dequantize")


def qbytes(qt: QTensor) -> int:
    """R1: storage in bytes: ceil(codes * bits / 8) plus 2 bytes (fp16) per scale."""
    raise NotImplementedError("R1: qbytes")


def quantize_model(model, bits: int, scheme: str):
    """R2: return (A_hat, B_hat, total_bytes). bits=16 means unquantised fp16 (arrays unchanged, 2 bytes each).
    Schemes: 'tensor', 'channel', 'group<g>' (e.g. 'group8'); axes per matrix are defined in the README."""
    raise NotImplementedError("R2: quantize_model")


def ppl_ratio(model, bits: int, scheme: str, tokens) -> float:
    """R2: perplexity of the quantised model divided by that of the fp model, on `tokens`."""
    raise NotImplementedError("R2: ppl_ratio")


def simulate(requests, policy: str, max_batch: int, max_wait_s: float, bits: int, cm) -> SimResult:
    """R3: event simulation of 'static' or 'continuous' batching. requests = [(arrival, prompt, output), ...]."""
    raise NotImplementedError("R3: simulate")


def max_load_multiplier(requests, config: dict, cm, slo_p95_s: float, multipliers=(1, 1.5, 2, 3, 4, 6, 8, 12)) -> float:
    """R4: largest m in `multipliers` such that compressing all arrival times by 1/m keeps p95 <= slo
    (stop at the first failure; 0 if even m=1 fails)."""
    raise NotImplementedError("R4: max_load_multiplier")


def recommend(model, requests, cm, slo_p95_s: float, max_ppl_ratio: float, tokens) -> dict:
    """R5: search configurations and return the best as a dict with at least the keys
    bits, scheme, policy, max_batch, max_wait_s, p95_s, ppl_ratio, memory_gb, capacity."""
    raise NotImplementedError("R5: recommend")
