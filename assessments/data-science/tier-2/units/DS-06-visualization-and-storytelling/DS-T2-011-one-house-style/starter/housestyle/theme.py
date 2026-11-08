"""Theme and annotation API. Signatures are the contract; the design is yours."""
from __future__ import annotations

from contextlib import contextmanager


@contextmanager
def theme():
    """R6: apply the house rcParams inside a with-block and restore the previous ones afterwards."""
    raise NotImplementedError("R6: implement theme")
    yield  # pragma: no cover


def annotate_source(target, text: str):
    """R7: add a text starting 'Source:' to the figure that owns `target` (a Figure or an Axes); return the Text."""
    raise NotImplementedError("R7: implement annotate_source")


def label_lines(ax, fmt: str = "{label}", pad: float = 0.01):
    """R7: replace the legend with a direct label near the last point of each labelled line, in its colour."""
    raise NotImplementedError("R7: implement label_lines")


def highlight(ax, label: str, muted: str = "#b8b8b8"):
    """R7: keep the line called `label` in colour and mute every other labelled line. Unknown label: ValueError."""
    raise NotImplementedError("R7: implement highlight")
