from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.astronomy.declination import declination_for_dates
from src.astronomy.events import compute_year_with_padding


SEASON_NAMES = {
    "march_equinox": "spring",
    "june_solstice": "summer",
    "september_equinox": "autumn",
    "december_solstice": "winter",
}


@dataclass
class SeasonWindow:
    name: str
    event_key: str
    event_time: pd.Timestamp
    start: pd.Timestamp
    end: pd.Timestamp


def build_season_windows(year: int, ephemeris_path: Optional[str] = None) -> List[SeasonWindow]:
    current, previous = compute_year_with_padding(year, ephemeris_path)
    windows: List[SeasonWindow] = []
    ordered = [
        ("winter", "december_solstice_prev", previous["december_solstice"]),
        ("spring", "march_equinox", current["march_equinox"]),
        ("summer", "june_solstice", current["june_solstice"]),
        ("autumn", "september_equinox", current["september_equinox"]),
        ("winter", "december_solstice", current["december_solstice"]),
    ]
    for name, key, event_time in ordered:
        start = event_time - pd.Timedelta(days=45)
        end = event_time + pd.Timedelta(days=45)
        windows.append(SeasonWindow(name=name, event_key=key, event_time=event_time, start=start, end=end))
    return windows


def classify_day(date: pd.Timestamp, windows: List[SeasonWindow]) -> SeasonWindow:
    for window in windows:
        if window.start <= date <= window.end:
            return window
    # If gaps exist between idealized 90-day windows (e.g., because 4×90=360),
    # fall back to the nearest event to avoid errors mid-year.
    nearest = min(windows, key=lambda w: abs((date - w.event_time).days))
    return nearest


def build_solar_calendar(year: int, ephemeris_path: Optional[str] = None) -> pd.DataFrame:
    """
    Construct the dynamic solar calendar for a target year.
    """
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", tz="UTC", freq="D")
    windows = build_season_windows(year, ephemeris_path)

    records: List[Dict] = []
    declinations = declination_for_dates(dates, ephemeris_path=ephemeris_path)

    for i, date in enumerate(dates):
        window = classify_day(date, windows)
        distance = (date - window.event_time).days
        solar_index = distance + 46  # day 46 is the event
        progress = (solar_index - 1) / 89.0
        if solar_index < 46:
            phase = "approach"
        elif solar_index == 46:
            phase = "peak"
        else:
            phase = "decline"
        records.append(
            {
                "date": date.normalize(),
                "season": window.name,
                "event_name": window.event_key,
                "solar_index": solar_index,
                "distance_to_center": distance,
                "phase": phase,
                "progress": progress,
                "declination_deg": declinations[i],
            }
        )
    return pd.DataFrame(records)
