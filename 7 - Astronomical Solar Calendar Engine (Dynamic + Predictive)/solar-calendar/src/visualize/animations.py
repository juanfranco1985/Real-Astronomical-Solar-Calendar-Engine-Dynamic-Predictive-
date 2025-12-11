from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation


def solar_progress_animation(df: pd.DataFrame, out_dir: str | Path, interval: int = 50) -> Path:
    """
    Build a simple animation showing solar index progression through the year.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(1, len(df))
    ax.set_ylim(df["solar_index"].min() - 5, df["solar_index"].max() + 5)
    line_real, = ax.plot([], [], color="#1f77b4", label="Real")
    line_fixed, = ax.plot([], [], color="#ff7f0e", label="Fixed", alpha=0.7)
    ax.set_xlabel("Day of Year")
    ax.set_ylabel("Solar Day Index")
    ax.legend()
    ax.grid(alpha=0.3)

    days = list(range(1, len(df) + 1))

    def init():
        line_real.set_data([], [])
        line_fixed.set_data([], [])
        return line_real, line_fixed

    def update(frame):
        line_real.set_data(days[:frame], df["solar_index"].values[:frame])
        line_fixed.set_data(days[:frame], df["fixed_index"].values[:frame])
        return line_real, line_fixed

    anim = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=interval)
    output = out_dir / "solar_progress.gif"
    anim.save(output, writer="pillow")
    plt.close(fig)
    return output
