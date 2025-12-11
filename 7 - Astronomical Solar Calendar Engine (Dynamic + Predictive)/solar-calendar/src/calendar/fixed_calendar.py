from __future__ import annotations

from typing import List

import pandas as pd


def _fixed_centers(year: int) -> List[pd.Timestamp]:
    centers = [
        pd.Timestamp(year=year - 1, month=12, day=21, tz="UTC"),
        pd.Timestamp(year=year, month=3, day=21, tz="UTC"),
        pd.Timestamp(year=year, month=6, day=21, tz="UTC"),
        pd.Timestamp(year=year, month=9, day=21, tz="UTC"),
        pd.Timestamp(year=year, month=12, day=21, tz="UTC"),
    ]
    return centers


def build_fixed_calendar(year: int) -> pd.DataFrame:
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", tz="UTC", freq="D")
    centers = _fixed_centers(year)
    labels = ["winter", "spring", "summer", "autumn", "winter"]

    rows = []
    for date in dates:
        for center, label in zip(centers, labels):
            start = center - pd.Timedelta(days=45)
            end = center + pd.Timedelta(days=45)
            if start <= date <= end:
                distance = (date - center).days
                solar_index = distance + 46
                phase = "approach" if solar_index < 46 else ("peak" if solar_index == 46 else "decline")
                rows.append(
                    {
                        "date": date.normalize(),
                        "fixed_season": label,
                        "fixed_index": solar_index,
                        "fixed_distance": distance,
                        "fixed_phase": phase,
                        "fixed_progress": (solar_index - 1) / 89.0,
                    }
                )
                break
    return pd.DataFrame(rows)
