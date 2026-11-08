"""fairlend: fairness metrics, mitigation and trade-off tools for ML-T2-029."""
from .metrics import fairness_report, reweighing_weights
from .thresholds import group_thresholds, tradeoff_curve
from .pipeline import select_and_mitigate
