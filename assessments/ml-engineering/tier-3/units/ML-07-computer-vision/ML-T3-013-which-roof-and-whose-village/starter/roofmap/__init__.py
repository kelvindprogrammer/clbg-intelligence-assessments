"""roofmap: label-efficient, village-robust roof-material classification (ML-T3-013)."""
from .features import encode, patch_dictionary
from .model import fit_roof_classifier
from .validation import cluster_bootstrap_ci, village_block_split

__all__ = ["village_block_split", "cluster_bootstrap_ci", "patch_dictionary", "encode", "fit_roof_classifier"]
