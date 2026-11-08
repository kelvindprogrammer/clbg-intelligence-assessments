"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "4a13cb815c96ad49e66e7f9900539732686ef010ce6aa184d360404c364c945c"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "demand_points.csv was modified"


def test_loader_and_shape():
    from agentmap import load_points
    X = load_points(DATA)
    assert X.shape == (600, 2) and X.dtype == float


def test_public_api():
    import agentmap as am
    for name in ["kmeans_pp_init", "assign", "update_centers", "inertia", "kmeans", "silhouette_scores", "choose_k"]:
        assert callable(getattr(am, name)), name
    sig = inspect.signature(am.kmeans)
    assert sig.parameters["seed"].kind is inspect.Parameter.KEYWORD_ONLY
    assert {"centers", "labels", "inertia", "n_iter"} <= set(am.KMeansResult.__dataclass_fields__)


def test_no_sklearn_in_package():
    import agentmap.core as core
    src = inspect.getsource(core)
    assert "import sklearn" not in src and "from sklearn" not in src, "the package must be numpy only"
