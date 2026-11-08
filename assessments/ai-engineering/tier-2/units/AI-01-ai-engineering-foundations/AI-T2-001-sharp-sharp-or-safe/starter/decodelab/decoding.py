"""Fill in every function. See README section D.1 for exact semantics."""
from __future__ import annotations

import numpy as np

BOS, EOS = 0, 1
DEFAULT_CFG = {"temperature": 1.0, "top_k": 0, "top_p": 1.0, "repetition_penalty": 1.0}


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    raise NotImplementedError("R1: stable softmax with temperature; temperature 0 is one-hot argmax")


def filter_top_k(probs: np.ndarray, k: int) -> np.ndarray:
    raise NotImplementedError("R2: keep the k most probable tokens, renormalise")


def filter_top_p(probs: np.ndarray, p: float) -> np.ndarray:
    raise NotImplementedError("R3: keep the smallest prefix of sorted tokens with mass >= p, renormalise")


def apply_repetition_penalty(logits: np.ndarray, generated: list[int], penalty: float) -> np.ndarray:
    raise NotImplementedError("R4: penalise tokens already generated")


def generate(lm, seed: int, cfg: dict | None = None, max_len: int = 20) -> list[int]:
    raise NotImplementedError("R5: sample ids until <eos> or max_len")


def sequence_logprob(lm, ids: list[int]) -> float:
    raise NotImplementedError("R6: log-probability of ids followed by <eos> under temperature 1")


def beam_search(lm, width: int, max_len: int = 20) -> list[int]:
    raise NotImplementedError("R7: highest-logprob sequence found by beam search")


def evaluate_config(lm, cfg: dict, seeds: list[int], max_len: int = 20) -> dict:
    raise NotImplementedError("R8: valid_rate, unique_rate, repeat_rate over one sample per seed")


def choose_decoding(lm, seeds: list[int], min_valid: float, min_unique: float) -> dict:
    raise NotImplementedError("R9: choose a config that meets both bars, with a justified preference")
