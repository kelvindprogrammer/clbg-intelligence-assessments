import numpy as np

from .core import CompressedModel


def quantize_tensor(W, bits, per_channel=True):
    raise NotImplementedError("R1: symmetric integer quantisation; return (Q, scales)")


def dequantize(Q, scales):
    raise NotImplementedError("R1: Q * scales, broadcasting per output column when scales is a vector")


def magnitude_prune(Ws, sparsity):
    raise NotImplementedError("R2: zero the smallest-|w| fraction of ALL weights, globally")


def layer_bytes(shape, nnz, bits, n_scales):
    raise NotImplementedError("R3: min(dense, sparse) storage in bytes, plus scales and float32 biases")


def compress(Ws, bs, X_cal, y_cal, budget_ratio=0.20, max_drop=0.025):
    raise NotImplementedError("R4: choose bits and sparsity from calibration data; return a CompressedModel")
