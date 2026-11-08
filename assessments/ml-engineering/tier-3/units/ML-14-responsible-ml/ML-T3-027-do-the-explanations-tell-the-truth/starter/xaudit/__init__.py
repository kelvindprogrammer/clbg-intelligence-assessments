"""xaudit: attribution methods, faithfulness and shortcut audits for ML-T3-027."""
from .core import roc_auc, permutation_importance, shapley_sampling
from .faithfulness import deletion_curve, deletion_auc, agreement, stability
from .audit import shortcut_audit
