"""The naive baseline (provided complete in the starter). You must beat it, not reuse it."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .io import REGISTER_COLUMNS, Panel


def naive_register(panel: Panel) -> pd.DataFrame:
    """What a hurried analyst might do: for each (state, commodity), correlate the raw price LEVEL
    with the raw 3-month rainfall total at lags 0-6, keep the lag with the smallest p-value,
    and call the pair 'supported' if that p < 0.05. No deflation, no deseasonalising, no
    correction for trying seven lags or 144 pairs."""
    rain = panel.rain.sort_values(["state", "month"]).copy()
    rain["r3"] = rain.groupby("state")["rain_mm"].transform(lambda s: s.rolling(3).sum())
    rows = []
    for i, ((s, c), g) in enumerate(sorted(panel.prices.groupby(["state", "commodity"]))):
        r = rain[rain["state"] == s].set_index("month")["r3"]
        best = None
        for L in range(7):
            x = r.shift(L).reindex(g["month"]).to_numpy()
            ok = np.isfinite(x)
            rho, p = stats.pearsonr(x[ok], g["price_ngn_per_kg"].to_numpy()[ok])
            if best is None or p < best[2]:
                best = (L, rho, p)
        L, rho, p = best
        rows.append({"hypothesis_id": f"NAIVE-{i + 1:03d}", "state": s, "commodity": c, "rain_feature": "rain_3m_total",
                     "lag_months": L, "effect": rho, "ci_low": rho, "ci_high": rho, "p_value": p, "q_value": p,
                     "status": "supported" if p < 0.05 else "not_supported",
                     "method": "naive: raw levels, best of 7 lags, p < 0.05", "follow_up": ""})
    return pd.DataFrame(rows, columns=REGISTER_COLUMNS)
