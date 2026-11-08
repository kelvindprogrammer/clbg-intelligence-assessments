"""The quarterly report built with the house style. CHARTS is fixed by the brief."""
from __future__ import annotations

CHARTS = ("channel_value", "provider_failures", "agents_by_zone", "fraud_reports", "channel_share")


def make_chart(name: str, data_dir):
    """R9: build one chart from CHARTS inside theme() and return the matplotlib Figure."""
    raise NotImplementedError("R9: implement make_chart")


def build_report(data_dir, out_dir):
    """R9: write <name>.png for every chart in CHARTS into out_dir and return the list of paths."""
    raise NotImplementedError("R9: implement build_report")
