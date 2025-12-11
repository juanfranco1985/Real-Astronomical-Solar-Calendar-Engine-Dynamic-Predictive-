from __future__ import annotations

from functools import lru_cache
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.calendar.compare import compare_calendars

app = FastAPI(title="Astronomical Solar Calendar API", version="1.0.0")


@lru_cache(maxsize=8)
def get_calendar(year: int, ephemeris_path: Optional[str] = None) -> pd.DataFrame:
    return compare_calendars(year, ephemeris_path=ephemeris_path)


@app.get("/solar/day")
def solar_day(date: str, ephemeris_path: Optional[str] = None):
    try:
        target_date = pd.Timestamp(date, tz="UTC").normalize()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date: {exc}") from exc
    year = target_date.year
    cal = get_calendar(year, ephemeris_path)
    row = cal.loc[cal["date"] == target_date]
    if row.empty:
        raise HTTPException(status_code=404, detail="Date not in calendar range")
    return row.iloc[0].to_dict()


@app.get("/solar/year")
def solar_year(year: int, ephemeris_path: Optional[str] = None):
    cal = get_calendar(year, ephemeris_path)
    return cal.to_dict(orient="records")
