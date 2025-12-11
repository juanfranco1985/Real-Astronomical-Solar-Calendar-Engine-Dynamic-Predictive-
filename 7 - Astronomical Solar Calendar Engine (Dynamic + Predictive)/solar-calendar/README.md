# Real Astronomical Solar Calendar Engine (Dynamic + Predictive)

A modular, production-ready data science and computational astronomy project that replaces the static Gregorian seasonal model with a physically accurate solar model based on real solstice and equinox events computed from JPL ephemerides via Skyfield. The engine builds dynamic 4×90‑day solar cycles, stores historical calendars, analyzes multi‑year drift, produces high-end visualizations, and exposes both CLI and FastAPI interfaces.

## Why a Solar Calendar?
- **Astronomical fidelity:** Seasons anchored on actual equinox/solstice instants (UTC) rather than fixed Gregorian dates.
- **Dynamic 4×90-day cycle:** Each season spans 90 days with the astronomical event at day 46, ensuring symmetric approach/peak/decline phases.
- **Predictive analytics:** Multi-year drift tracking, trend lines, and declination-derived insights.
- **Integration ready:** REST API and CLI for downstream systems and pipelines.

## Scientific Background
- **Equinoxes & solstices:** Defined by the Sun’s apparent ecliptic longitude (0°, 90°, 180°, 270°). Computed using Skyfield + JPL ephemerides (DE421+).
- **Axial tilt (obliquity ~23.44°):** Drives the annual declination swing of the Sun; responsible for seasonal insolation changes.
- **Orbital eccentricity (~0.0167):** Causes unequal lengths between perihelion and aphelion, shifting event timings year to year.
- **ΔT & timescales:** Event computations occur in TT/UTC. Small ΔT changes alter event instants by seconds; relevant for high-precision work.

## Dynamic Solar Cycle Model (4×90)
- Event-centered seasons: March Equinox, June Solstice, September Equinox, December Solstice.
- Each season = **90 days**, with the astronomical event as **day 46 (index 45)**.
- **Season start = event − 45 days**, **season end = event + 45 days**.
- Cross-year aware: windows that begin/end in adjacent years are handled seamlessly.

## Fixed vs Real Calendar
- **Real calendar:** Anchored on computed events.
- **Fixed calendar:** Anchored on static centers (Mar 21, Jun 21, Sep 21, Dec 21).
- Metrics per day: fixed vs real season/index, deviation (RealIndex − FixedIndex), yearly drift curves, mean absolute error.

## Project Layout
```
solar-calendar/
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── solar_calendars/
│   └── ephemeris/          # place de421.bsp (or newer) here
├── src/
│   ├── astronomy/
│   │   ├── events.py
│   │   └── declination.py
│   ├── calendar/
│   │   ├── solar_engine.py
│   │   ├── fixed_calendar.py
│   │   └── compare.py
│   ├── analysis/
│   │   ├── multiyear.py
│   │   └── trends.py
│   ├── api/
│   │   └── server.py
│   ├── cli/
│   │   └── cli.py
│   ├── visualize/
│   │   ├── plots.py
│   │   ├── polar_wheel.py
│   │   └── animations.py
│   └── main.py
├── notebooks/
│   ├── Exploration.ipynb
│   ├── MultiYear_Analysis.ipynb
│   └── DeclinationStudy.ipynb
├── tests/
├── requirements.txt
└── README.md
```

## Installation
1) Install Python 3.10+.  
2) Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```
3) Download an ephemeris file (e.g., `de421.bsp`) and place it in `data/ephemeris/`. You can override the path with `EPHEMERIS_PATH=/path/to/ephemeris.bsp`.

## Quickstart
Compute a solar calendar for 2025 and save to CSV:
```bash
python -m src.main compute-year --year 2025 --out data/processed/solar_calendars/solar_2025.csv
```
Compare real vs fixed seasons for 2025 and export deviation plots:
```bash
python -m src.main compare-year --year 2025 --out data/processed/solar_calendars/solar_2025_comparison.csv --plots out/plots
```
Run the API (FastAPI + Uvicorn):
```bash
uvicorn src.api.server:app --reload --port 8000
# GET http://localhost:8000/solar/day?date=2025-03-20
# GET http://localhost:8000/solar/year?year=2025
```

## Core Components
- **Astronomy (`src/astronomy`)**
  - `events.py`: precise equinox/solstice computation via Skyfield almanac; UTC timestamps returned as pandas-aware datetimes.
  - `declination.py`: solar declination computation per date/time using JPL ephemerides.
- **Calendar (`src/calendar`)**
  - `solar_engine.py`: builds the dynamic 4×90-day solar calendar with approach/peak/decline phases, season progress, and declination.
  - `fixed_calendar.py`: static Mar/Jun/Sep/Dec 21 centers for baseline comparison.
  - `compare.py`: deviation, drift line, MAE, merged outputs.
- **Analysis (`src/analysis`)**
  - `multiyear.py`: batch calendar generation and storage under `data/processed/solar_calendars/`.
  - `trends.py`: drift curves, event movement trends, rate-of-change estimates.
- **Visualizations (`src/visualize`)**
  - `plots.py`: deviation curves, declination vs solar day, drift heatmaps.
  - `polar_wheel.py`: polar visualization of real vs fixed seasons.
  - `animations.py`: simple year progression animation helper.
- **Interfaces**
  - CLI (`src/cli/cli.py`): argparse commands for single-year, multi-year, and compare workflows.
  - API (`src/api/server.py`): FastAPI endpoints for day/year solar metadata.

## Data Outputs
- Calendars stored as CSV in `data/processed/solar_calendars/`.
- Each calendar row includes: Gregorian date, season, solar index (1–90), distance to center, phase, progress, declination (deg), fixed season/index, deviation, and metadata.
- Example CSV headers:
```
date,season,solar_index,distance_to_center,phase,progress,declination_deg,fixed_season,fixed_index,deviation,event_name
```

## Accuracy & Considerations
- **Ephemeris:** Use DE421+; newer ephemerides (DE440) improve long-range accuracy.
- **ΔT:** High-precision users can supply ΔT adjustments via Skyfield’s timescale options.
- **Timezones:** Computations default to UTC; convert to local time as needed in downstream systems.
- **Leap seconds:** Skyfield handles leap seconds; timestamps returned as tz-aware UTC.

## Examples
- **Real vs Fixed Deviation Curve:** Shows how actual solar timing drifts relative to fixed Gregorian anchors through the year.
- **Polar Solar Wheel:** Visualizes 4×90-day cycles with real vs fixed centers.
- **Declination Curve:** Daily solar declination vs solar day index.
- **Heatmap:** Multi-year deviation magnitude (absolute drift) across decades.
- **Animation:** Season progression across the year with real/fixed overlays.

## API Reference
- `GET /solar/day?date=YYYY-MM-DD` → Solar metadata for a single day (real + fixed, declination, drift).
- `GET /solar/year?year=YYYY` → Full-year solar map with real/fixed calendars and drift.

## CLI Reference
```bash
python -m src.main compute-year --year 2025 --out data/processed/solar_calendars/solar_2025.csv
python -m src.main compare-year --year 2025 --plots out/plots
python -m src.main multi-year --start 1990 --end 2030 --out data/processed/solar_calendars/
python -m src.main serve --port 8000
```

## Testing
Basic tests are scaffolded in `tests/` (astronomy timing sanity, shape of calendar outputs). Run:
```bash
python -m pytest
```

## Notebook Starters
- `notebooks/Exploration.ipynb`: exploratory data analysis of a single year.
- `notebooks/MultiYear_Analysis.ipynb`: drift curves and rate-of-change across decades.
- `notebooks/DeclinationStudy.ipynb`: declination vs solar index with custom ephemerides.

## Docker (optional)
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV EPHEMERIS_PATH=/app/data/ephemeris/de421.bsp
EXPOSE 8000
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Next Steps
- Drop in your ephemeris file under `data/ephemeris/`.
- Generate a sample year (`compute-year`) and inspect the CSV + plots.
- Expand visual themes or add higher-order models (ΔT sensitivity, perihelion-aware drift).

