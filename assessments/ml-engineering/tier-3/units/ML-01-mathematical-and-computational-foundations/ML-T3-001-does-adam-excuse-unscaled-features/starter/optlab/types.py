from dataclasses import dataclass

import numpy as np


@dataclass
class Trace:
    """Result of one optimiser run. `evals` counts data passes (loss_grad = 1, hessian = d)."""
    w: np.ndarray
    f: float
    iters: int
    evals: float
    converged: bool
