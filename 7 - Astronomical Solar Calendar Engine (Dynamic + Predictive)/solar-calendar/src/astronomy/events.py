from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
from skyfield import almanac
from skyfield.api import Loader

EPHEMERIS_ENV = "EPHEMERIS_PATH"


@dataclass
class EphemerisContext:
    eph: object
    ts: object
    source: Path


def resolve_ephemeris_path(ephemeris_path: str | Path | None = None) -> Path:
    """
    Resolve ephemeris path from argument, environment variable, or default location.
    """
    candidates = [
        ephemeris_path,
        os.getenv(EPHEMERIS_ENV),
        Path(__file__).resolve().parents[2] / "data" / "ephemeris" / "de421.bsp",
    ]
    for candidate in candidates:
        if candidate:
            path = Path(candidate).expanduser()
            if path.exists():
                return path
    raise FileNotFoundError(
        "Ephemeris file not found. Set EPHEMERIS_PATH or place de421.bsp under data/ephemeris/."
    )


def load_ephemeris(ephemeris_path: str | Path | None = None) -> EphemerisContext:
    """
    Load ephemeris and timescale using Skyfield Loader.
    """
    ephemeris_file = resolve_ephemeris_path(ephemeris_path)
    loader = Loader(str(ephemeris_file.parent))
    eph = loader(ephemeris_file.name)
    ts = loader.timescale()
    return EphemerisContext(eph=eph, ts=ts, source=ephemeris_file)


def compute_solar_events(year: int, ephemeris_path: str | Path | None = None) -> Dict[str, pd.Timestamp]:
    """
    Compute equinoxes and solstices for a given year (UTC).
    Returns dict with keys: march_equinox, june_solstice, september_equinox, december_solstice.
    """
    ctx = load_ephemeris(ephemeris_path)
    t0 = ctx.ts.utc(year, 1, 1)
    t1 = ctx.ts.utc(year, 12, 31, 23, 59, 59)
    seasons_fn = almanac.seasons(ctx.eph)
    times, events = almanac.find_discrete(t0, t1, seasons_fn)
    # Skyfield 1.53+ removed SEASON_* constants; map indices for both old/new versions.
    default_labels = ["march_equinox", "june_solstice", "september_equinox", "december_solstice"]
    if hasattr(almanac, "SEASON_SPRING"):
        labels = {
            almanac.SEASON_SPRING: default_labels[0],
            almanac.SEASON_SUMMER: default_labels[1],
            almanac.SEASON_AUTUMN: default_labels[2],
            almanac.SEASON_WINTER: default_labels[3],
        }
    else:
        # Newer Skyfield returns event indices 0-3 in the order of SEASON_EVENTS.
        labels = {i: default_labels[i] for i in range(len(default_labels))}
    results: Dict[str, pd.Timestamp] = {}
    for t, e in zip(times, events):
        label = labels[int(e)]
        dt = t.utc_datetime().replace(tzinfo=timezone.utc)
        results[label] = pd.Timestamp(dt)
    if len(results) != 4:
        missing = set(labels.values()) - set(results)
        raise ValueError(f"Missing events for {year}: {missing}")
    return results


def compute_year_with_padding(year: int, ephemeris_path: str | Path | None = None) -> Tuple[Dict[str, pd.Timestamp], Dict[str, pd.Timestamp]]:
    """
    Compute events for a given year plus the previous year to obtain the prior December solstice.
    Returns (current_year_events, previous_year_events).
    """
    current = compute_solar_events(year, ephemeris_path)
    previous = compute_solar_events(year - 1, ephemeris_path)
    return current, previous
