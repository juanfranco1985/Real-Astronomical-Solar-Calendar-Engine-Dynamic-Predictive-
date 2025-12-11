from __future__ import annotations

import numpy as np
import pandas as pd


def drift_over_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return daily deviation curve with rolling mean for a single year.
    """
    subset = df[["date", "deviation", "abs_deviation"]].copy()
    subset["rolling_mean"] = subset["deviation"].rolling(window=15, center=True, min_periods=5).mean()
    return subset


def average_seasonal_drift(df: pd.DataFrame) -> pd.DataFrame:
    """
    Average deviation by solar_index across multiple years.
    """
    grouped = df.groupby("solar_index")["deviation"].agg(["mean", "std", "count"]).reset_index()
    grouped.rename(columns={"mean": "avg_deviation", "std": "std_deviation", "count": "samples"}, inplace=True)
    return grouped


def trend_rate_per_century(df: pd.DataFrame) -> float:
    """
    Estimate drift rate in days/century using linear regression on year vs mean deviation.
    """
    df["year"] = pd.to_datetime(df["date"]).dt.year
    yearly = df.groupby("year")["deviation"].mean().reset_index()
    if len(yearly) < 2:
        return 0.0
    coeffs = np.polyfit(yearly["year"], yearly["deviation"], 1)
    slope_per_year = coeffs[0]
    return float(slope_per_year * 100)


def event_movement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Track day-of-year positions of equinoxes/solstices relative to fixed model.
    """
    events = df[df["phase"] == "peak"].copy()
    events["day_of_year"] = pd.to_datetime(events["date"]).dt.dayofyear
    summary = events.groupby("event_name")["day_of_year"].agg(["mean", "std", "min", "max"]).reset_index()
    return summary
