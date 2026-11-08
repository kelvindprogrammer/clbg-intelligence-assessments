"""multiverse: your multiverse analysis for DS-T3-003.

Only this entry point and the two files beside it are fixed (README D.2):

  multiverse/spec.yaml     the decision space you defend
  multiverse/results.csv   one row per universe in that space

Everything else (how you clean, model and summarise) is your design.
"""
from __future__ import annotations


def run_universe(choices: dict, data_dir=None) -> dict:
    """Run ONE universe end to end, from the raw files to the estimate.

    choices:  {decision_name: option} covering every decision in spec.yaml
    data_dir: directory holding enterprise_panel.csv, villages.csv and cpi_index.csv
              (default: resources/data found from the package location)

    Returns a dict with at least: estimate, se, ci_low, ci_high, p_value, n_obs.
    """
    raise NotImplementedError("R3: implement run_universe")
