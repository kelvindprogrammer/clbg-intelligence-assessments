"""Contract tests: pass on the unmodified starter, offline."""
import inspect

import pandas as pd
import pytest

from conftest import CITIES

pytestmark = pytest.mark.contract


def test_cities_file():
    c = pd.read_csv(CITIES)
    assert list(c.columns) == ["city", "lat", "lon"]
    assert len(c) == 6 and c["city"].is_unique
    assert c["lat"].between(4, 14).all() and c["lon"].between(2.5, 15).all(), "all cities must be in Nigeria"


def test_fetch_builds_power_urls():
    from climate_story.fetch import url_for
    u = url_for(12.0, 8.52)
    assert u.startswith("https://power.larc.nasa.gov/api/temporal/daily/point?")
    assert "T2M_MAX" in u and "start=19910101" in u and "end=20241231" in u and "format=CSV" in u


def test_api_and_constants():
    import climate_story as cs
    assert cs.MIN_COVERAGE == 0.9 and cs.MIN_YEARS == 10
    assert list(inspect.signature(cs.annual_hot_days).parameters) == ["df", "threshold", "col", "min_coverage"]
    assert inspect.signature(cs.period_change).parameters["base"].default == (1991, 2005)
    assert inspect.signature(cs.period_change).parameters["recent"].default == (2010, 2024)
    sm = inspect.signature(cs.small_multiples).parameters
    assert sm["sharey"].default is True and sm["title"].kind is inspect.Parameter.KEYWORD_ONLY
