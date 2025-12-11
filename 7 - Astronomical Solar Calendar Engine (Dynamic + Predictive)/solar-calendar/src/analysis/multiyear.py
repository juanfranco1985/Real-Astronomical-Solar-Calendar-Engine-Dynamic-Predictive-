from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from src.calendar.compare import compare_calendars


def compute_and_store_years(
    years: Iterable[int],
    out_dir: str | Path = "data/processed/solar_calendars",
    ephemeris_path: str | None = None,
) -> List[Path]:
    """
    Generate real vs fixed calendars for multiple years and store as CSV.
    """
    output_paths: List[Path] = []
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    for year in years:
        df = compare_calendars(year, ephemeris_path=ephemeris_path)
        output_path = out_dir_path / f"solar_calendar_{year}.csv"
        df.to_csv(output_path, index=False)
        output_paths.append(output_path)
    return output_paths


def load_multi_year(out_dir: str | Path) -> pd.DataFrame:
    csvs = sorted(Path(out_dir).glob("solar_calendar_*.csv"))
    frames = [pd.read_csv(csv) for csv in csvs]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
