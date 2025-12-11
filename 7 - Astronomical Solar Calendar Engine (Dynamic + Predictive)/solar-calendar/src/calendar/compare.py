from __future__ import annotations

import pandas as pd

from .fixed_calendar import build_fixed_calendar
from .solar_engine import build_solar_calendar


def compare_calendars(year: int, ephemeris_path: str | None = None) -> pd.DataFrame:
    real_df = build_solar_calendar(year, ephemeris_path=ephemeris_path)
    fixed_df = build_fixed_calendar(year)
    merged = real_df.merge(fixed_df, on="date", how="left")
    merged["deviation"] = merged["solar_index"] - merged["fixed_index"]
    merged["abs_deviation"] = merged["deviation"].abs()
    merged["drift_trend"] = merged["deviation"].rolling(window=15, center=True, min_periods=5).mean()
    return merged


def deviation_stats(df: pd.DataFrame) -> dict:
    return {
        "mean_abs_error": float(df["abs_deviation"].mean()),
        "max_abs_deviation": float(df["abs_deviation"].max()),
        "min_deviation": float(df["deviation"].min()),
        "max_deviation": float(df["deviation"].max()),
    }
