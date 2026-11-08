"""auditkit: group-wise error audit and model card for ML-T1-024."""
from .metrics import bootstrap_gap_ci, calibration_by_group, disparity, group_metrics
from .card import model_card
