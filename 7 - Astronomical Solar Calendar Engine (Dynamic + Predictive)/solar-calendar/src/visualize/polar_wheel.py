from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def polar_wheel(df: pd.DataFrame, out_dir: str | Path) -> Path:
    """
    Plot a polar comparison using a combined real/fixed dataframe (from compare_calendars).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    theta = 2 * np.pi * (pd.to_datetime(df["date"]).dt.dayofyear / 365.25)
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="polar")
    ax.plot(theta, df["solar_index"], label="Real solar index", color="#1f77b4")
    ax.plot(theta, df["fixed_index"], label="Fixed solar index", color="#ff7f0e", alpha=0.7)
    ax.set_title("Polar Solar Wheel (Real vs Fixed)")
    ax.set_rticks([0, 45, 90])
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    output = out_dir / "polar_wheel.png"
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return output
