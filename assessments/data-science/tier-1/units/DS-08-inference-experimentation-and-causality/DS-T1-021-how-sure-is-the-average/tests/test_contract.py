"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
SHA = "8f1a969ced3c653d9782d97e23b3f5eed3412f6f02da580e4edb8862aec3af30"


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA, "agent_transactions.csv was modified"


def test_loads_and_shape():
    from interval_lab import load_transactions
    df = load_transactions(DATA)
    assert list(df.columns) == ["txn_id", "region", "agent_id", "amount_ngn"]
    assert df["region"].nunique() == 6 and df["txn_id"].is_unique


def test_api_present():
    import interval_lab as il
    for name in ["t_interval", "bootstrap_ci", "diff_means_ci_bootstrap", "required_n", "coverage", "summarise_regions"]:
        assert callable(getattr(il, name)), name


def test_signatures():
    import interval_lab as il
    assert list(inspect.signature(il.bootstrap_ci).parameters) == ["x", "stat", "level", "n_boot", "seed"]
    assert list(inspect.signature(il.coverage).parameters) == ["sampler", "true_value", "interval_fn", "n", "reps", "seed"]
