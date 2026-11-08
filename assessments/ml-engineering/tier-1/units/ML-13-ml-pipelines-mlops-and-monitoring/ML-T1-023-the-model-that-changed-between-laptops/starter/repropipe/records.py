"""Provided: the Run record and the code-version constant. Do not change field names."""
from dataclasses import dataclass, field

import numpy as np

CODE_VERSION = "repropipe-1"


@dataclass
class Run:
    run_id: str
    config: dict
    data_fp: str
    config_fp: str
    code_version: str
    coef: np.ndarray
    intercept: float
    mean: np.ndarray
    scale: np.ndarray
    metrics: dict = field(default_factory=dict)
