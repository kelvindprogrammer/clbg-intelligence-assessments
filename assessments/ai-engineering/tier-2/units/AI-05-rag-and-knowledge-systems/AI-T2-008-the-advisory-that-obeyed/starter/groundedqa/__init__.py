"""groundedqa: hybrid retrieval, injection-safe grounded answering and evaluation for AI-T2-008."""
from .core import (DEFAULT_CFG, HybridRetriever, build_prompt, chunk_docs, evaluate, make_system, resolve_conflicts,
                   sanitize, sufficient, verify_answer)

__all__ = ["DEFAULT_CFG", "chunk_docs", "HybridRetriever", "sanitize", "resolve_conflicts", "sufficient", "build_prompt",
           "verify_answer", "make_system", "evaluate"]
