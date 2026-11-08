import numpy as np


def conv_output_size(n, k, stride=1, pad=0):
    raise NotImplementedError("R1: output length of a sliding window; raise ValueError if the kernel does not fit")


def conv2d(img, kernel, stride=1, pad=0):
    raise NotImplementedError("R1: 2-D cross-correlation (no kernel flip), zero padding, given stride")


def maxpool2d(img, size, stride=None):
    raise NotImplementedError("R2: max pooling; stride defaults to size; partial windows are dropped")


def sobel_gradients(img):
    raise NotImplementedError("R3: (gx, gy) with Sobel kernels, same shape as img, zero padding, built on conv2d")
