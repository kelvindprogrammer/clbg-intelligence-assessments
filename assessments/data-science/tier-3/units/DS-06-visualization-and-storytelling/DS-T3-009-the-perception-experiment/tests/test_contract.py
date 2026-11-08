"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect
from pathlib import Path

import pandas as pd
import pytest

pytestmark = pytest.mark.contract
OBSERVER_SHA256 = "0d75eb667d083a893e83e898f5b0be455e3ec795ad8d5ad894a5725d73e77ea9"


def test_observer_unmodified():
    import perception_lab.observer as obs
    assert hashlib.sha256(Path(obs.__file__).read_bytes()).hexdigest() == OBSERVER_SHA256, "observer.py was modified"


def test_simulate_responses_adds_judgements():
    from perception_lab import simulate_responses
    d = pd.DataFrame({"participant": [0, 0, 1, 1], "encoding": ["bar_common", "circle_area"] * 2, "true_pct": [50.0, 50.0, 80.0, 20.0]})
    out = simulate_responses(d, seed=1)
    assert "judged_pct" in out and out["judged_pct"].between(1, 100).all() and "judged_pct" not in d


def test_public_api_signatures():
    import perception_lab as pl
    assert pl.ENCODINGS == ("bar_common", "bar_unaligned", "pie_angle", "circle_area")
    assert list(inspect.signature(pl.make_design).parameters)[:4] == ["n_participants", "ratios", "repeats", "seed"]
    assert list(inspect.signature(pl.analyze).parameters) == ["responses", "B", "seed"]
    for name in ["render_stimulus", "displayed_ratio", "lie_factor", "log_abs_error", "ranking_recovery_rate"]:
        assert callable(getattr(pl, name)), name
