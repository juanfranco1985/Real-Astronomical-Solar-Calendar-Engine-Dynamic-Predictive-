from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def plot_deviation_curve(df: pd.DataFrame, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    _ensure_dir(out_dir)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["date"], df["deviation"], label="Deviation (real - fixed)", color="#1f77b4")
    ax.plot(df["date"], df["drift_trend"], label="Drift trend", color="#d62728", linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_ylabel("Days")
    ax.set_title("Solar Drift vs Fixed Gregorian Centers")
    ax.legend()
    ax.grid(alpha=0.3)
    output = out_dir / "deviation_curve.png"
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def plot_declination_curve(df: pd.DataFrame, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    _ensure_dir(out_dir)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["solar_index"], df["declination_deg"], color="#2ca02c")
    ax.set_xlabel("Solar Day Index (1-90 repeated)")
    ax.set_ylabel("Declination (deg)")
    ax.set_title("Solar Declination Across the Year")
    ax.grid(alpha=0.3)
    output = out_dir / "declination_curve.png"
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def plot_heatmap_multi_year(df: pd.DataFrame, out_dir: str | Path, value: str = "deviation") -> Path:
    out_dir = Path(out_dir)
    _ensure_dir(out_dir)
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["doy"] = pd.to_datetime(df["date"]).dt.dayofyear
    pivot = df.pivot_table(index="year", columns="doy", values=value, aggfunc="mean")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, cmap="coolwarm", center=0, ax=ax)
    ax.set_title(f"Multi-year {value} heatmap")
    ax.set_xlabel("Day of Year")
    ax.set_ylabel("Year")
    output = out_dir / f"heatmap_{value}.png"
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output
