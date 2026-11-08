"""staggered_did: difference-in-differences with staggered adoption (DS-T3-013)."""
from .estimators import aggregate_att, group_time_att, twfe_att
from .inference import cluster_bootstrap, pretrend_test
from .report import analyze, load_panel

__all__ = ["twfe_att", "group_time_att", "aggregate_att", "cluster_bootstrap", "pretrend_test", "analyze", "load_panel"]
