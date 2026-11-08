"""Write small synthetic files in NASA POWER's daily CSV layout, for offline tests.

Values are invented. Only the layout imitates POWER.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HEADER = """-BEGIN HEADER-
NASA/POWER Source Native Resolution Daily Data
Dates (month/day/year): {start} through {end} in LST
Location: latitude  {lat}   longitude {lon}
The value for missing source data that cannot be computed or is outside of the sources availability range: -999
parameter(s):
T2M_MAX         MERRA-2 Temperature at 2 Meters Maximum (C)
PRECTOTCORR     MERRA-2 Precipitation Corrected (mm/day)
-END HEADER-
"""


def synthetic_daily(years, seed=0, base=33.0, warming_per_year=0.05, amp=4.0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(f"{years[0]}-01-01", f"{years[1]}-12-31", freq="D")
    t = np.arange(len(dates))
    doy = dates.day_of_year.to_numpy()
    tmax = base + amp * np.cos((doy - 100) * 2 * np.pi / 365.25) + warming_per_year * (dates.year - years[0]) \
        + rng.normal(0, 1.5, len(dates))
    rain = np.clip(rng.gamma(0.4, 6, len(dates)) * (np.sin((doy - 120) * np.pi / 200) > 0), 0, None)
    return pd.DataFrame({"date": dates, "t2m_max": np.round(tmax, 2), "prectotcorr": np.round(rain, 2), "_t": t})


def write_power(path, daily: pd.DataFrame, layout: str = "doy", header: bool = True, missing_idx=()):
    d = daily.copy()
    tm = d["t2m_max"].to_numpy(float).copy()
    tm[list(missing_idx)] = -999.0
    d["t2m_max"] = tm
    if layout == "doy":
        body = pd.DataFrame({"YEAR": d.date.dt.year, "DOY": d.date.dt.day_of_year, "T2M_MAX": d.t2m_max, "PRECTOTCORR": d.prectotcorr})
    else:
        body = pd.DataFrame({"YEAR": d.date.dt.year, "MO": d.date.dt.month, "DY": d.date.dt.day, "T2M_MAX": d.t2m_max,
                             "PRECTOTCORR": d.prectotcorr})
    text = body.to_csv(index=False, lineterminator="\n")
    if header:
        text = HEADER.format(start=d.date.iloc[0].strftime("%m/%d/%Y"), end=d.date.iloc[-1].strftime("%m/%d/%Y"),
                             lat=12.0, lon=8.52) + text
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path
