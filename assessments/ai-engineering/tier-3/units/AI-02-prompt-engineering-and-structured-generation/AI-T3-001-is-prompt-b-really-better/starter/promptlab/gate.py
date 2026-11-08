"""Fill in every function. See README section D.1. DEFAULT_GATE is a starting point you may change."""
from __future__ import annotations

import numpy as np

DEFAULT_GATE = {"level": 0.95, "n_boot": 1000, "tolerance": 0.04, "min_slice_items": 20}


def evaluate_prompt(mock, prompt: str, items: list[dict], seeds: list[int]) -> np.ndarray:
    raise NotImplementedError("R1: boolean matrix (n_items, n_seeds); reject duplicate seeds")


def paired_bootstrap(old: np.ndarray, new: np.ndarray, n_boot: int = 1000, level: float = 0.95, seed: int = 0) -> dict:
    raise NotImplementedError("R2: item-clustered paired bootstrap of the accuracy difference")


def required_items(sd_diff: float, delta: float, alpha: float = 0.05, power: float = 0.8) -> int:
    raise NotImplementedError("R3: items needed to detect a paired difference delta")


def check_leakage(prompt: str, items: list[dict]) -> list[str]:
    raise NotImplementedError("R4: ids of evaluation items whose text appears in the prompt")


def regression_gate(old: np.ndarray, new: np.ndarray, slices: dict[str, np.ndarray], cfg: dict | None = None,
                    seed: int = 0) -> dict:
    raise NotImplementedError("R5: decide ship / block / inconclusive with reasons and statistics")


def operating_characteristics(make_pair, gate, trials: int, seed: int = 0) -> dict:
    raise NotImplementedError("R6: simulate the gate to estimate its block, ship and inconclusive rates")
