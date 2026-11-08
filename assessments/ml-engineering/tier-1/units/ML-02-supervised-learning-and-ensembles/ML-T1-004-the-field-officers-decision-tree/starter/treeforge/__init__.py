"""treeforge: a CART classifier from scratch for ML-T1-004."""
from .split import best_split, gini
from .tree import DecisionTree, depth_sweep, export_rules

__all__ = ["gini", "best_split", "DecisionTree", "export_rules", "depth_sweep"]
