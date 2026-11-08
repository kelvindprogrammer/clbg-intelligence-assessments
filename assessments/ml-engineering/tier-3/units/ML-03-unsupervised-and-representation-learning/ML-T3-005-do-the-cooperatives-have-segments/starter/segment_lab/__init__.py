"""segment_lab: does a population have segments, and how many?"""
from .core import (Members, StructureReport, estimate_k, gap_statistic, load_members, null_samples,
                   prepare, stability)
from .simulate import simulate

__all__ = ["Members", "StructureReport", "estimate_k", "gap_statistic", "load_members", "null_samples",
           "prepare", "stability", "simulate"]
