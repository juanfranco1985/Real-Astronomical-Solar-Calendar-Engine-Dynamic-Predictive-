import os
from pathlib import Path

import pandas as pd
import pytest

from src.calendar.solar_engine import build_solar_calendar

EPHEMERIS = os.getenv("EPHEMERIS_PATH", Path(__file__).resolve().parents[1] / "data" / "ephemeris" / "de421.bsp")


pytestmark = pytest.mark.skipif(
    not Path(EPHEMERIS).exists(),
    reason="Ephemeris file not available; set EPHEMERIS_PATH or place de421.bsp in data/ephemeris",
)


def test_calendar_has_full_year():
    df = build_solar_calendar(2022, ephemeris_path=EPHEMERIS)
    assert len(df) == 365 or len(df) == 366
    assert {"season", "solar_index", "declination_deg"}.issubset(df.columns)


def test_day_indices_range():
    df = build_solar_calendar(2022, ephemeris_path=EPHEMERIS)
    assert df["solar_index"].between(1, 90).all()
