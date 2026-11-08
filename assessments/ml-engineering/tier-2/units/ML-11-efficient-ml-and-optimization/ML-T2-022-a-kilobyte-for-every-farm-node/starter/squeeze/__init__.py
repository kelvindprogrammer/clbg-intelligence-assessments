"""squeeze: quantise, prune and budget a small MLP for ML-T2-022."""
from .core import CompressedModel, accuracy, forward, float32_bytes
from .compression import compress, dequantize, layer_bytes, magnitude_prune, quantize_tensor

__all__ = ["CompressedModel", "accuracy", "forward", "float32_bytes",
           "quantize_tensor", "dequantize", "magnitude_prune", "layer_bytes", "compress"]
