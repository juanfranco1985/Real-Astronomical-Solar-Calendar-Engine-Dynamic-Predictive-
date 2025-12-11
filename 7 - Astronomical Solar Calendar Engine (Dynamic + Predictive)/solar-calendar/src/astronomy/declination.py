from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

import numpy as np
import pandas as pd

from .events import EphemerisContext, load_ephemeris


def _compute_declination_for_times(times, ctx: EphemerisContext) -> np.ndarray:
    earth = ctx.eph["earth"]
    sun = ctx.eph["sun"]
    astrometric = earth.at(times).observe(sun).apparent()
    declination = astrometric.radec()[1].degrees
    return declination


def declination_for_dates(
    dates: Iterable[pd.Timestamp] | pd.DatetimeIndex,
    ephemeris_path: str | None = None,
    ctx: EphemerisContext | None = None,
) -> List[float]:
    """
    Compute solar declination (deg) for each date at 12:00 UTC.
    """
    context = ctx or load_ephemeris(ephemeris_path)
    ts = context.ts
    # Normalize to UTC-aware datetimes and sample at midday UTC to reduce daily variation noise.
    timestamps = pd.to_datetime(list(dates), utc=True) + pd.Timedelta(hours=12)
    py_datetimes = timestamps.to_pydatetime().tolist()
    times = ts.from_datetimes(py_datetimes)
    return _compute_declination_for_times(times, context).tolist()
