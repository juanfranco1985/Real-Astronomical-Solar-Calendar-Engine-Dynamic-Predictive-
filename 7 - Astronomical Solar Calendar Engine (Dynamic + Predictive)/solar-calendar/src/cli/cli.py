from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from src.analysis.multiyear import compute_and_store_years
from src.calendar.compare import compare_calendars, deviation_stats
from src.calendar.solar_engine import build_solar_calendar
from src.visualize.animations import solar_progress_animation
from src.visualize.plots import plot_declination_curve, plot_deviation_curve
from src.visualize.polar_wheel import polar_wheel

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Astronomical Solar Calendar Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    compute = sub.add_parser("compute-year", help="Compute solar calendar for a year")
    compute.add_argument("--year", type=int, required=True)
    compute.add_argument("--out", type=Path, required=True, help="Output CSV path")
    compute.add_argument("--ephemeris", type=str, help="Path to ephemeris file")

    compare = sub.add_parser("compare-year", help="Compute real vs fixed calendar comparison")
    compare.add_argument("--year", type=int, required=True)
    compare.add_argument("--out", type=Path, default=None, help="Optional output CSV path")
    compare.add_argument("--plots", type=Path, default=None, help="Directory to save plots")
    compare.add_argument("--ephemeris", type=str, help="Path to ephemeris file")

    multi = sub.add_parser("multi-year", help="Compute multiple years of calendars")
    multi.add_argument("--start", type=int, required=True)
    multi.add_argument("--end", type=int, required=True)
    multi.add_argument("--out", type=Path, required=True, help="Output directory")
    multi.add_argument("--ephemeris", type=str, help="Path to ephemeris file")

    serve = sub.add_parser("serve", help="Run FastAPI server via uvicorn")
    serve.add_argument("--host", type=str, default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)

    return parser.parse_args()


def handle_compute_year(args: argparse.Namespace):
    df = build_solar_calendar(args.year, ephemeris_path=args.ephemeris)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    console.print(f"[green]Saved calendar[/green] → {args.out}")


def handle_compare_year(args: argparse.Namespace):
    df = compare_calendars(args.year, ephemeris_path=args.ephemeris)
    stats = deviation_stats(df)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out, index=False)
        console.print(f"[green]Saved comparison CSV[/green] → {args.out}")
    console.print(f"[yellow]Mean abs deviation:[/yellow] {stats['mean_abs_error']:.3f} days")
    if args.plots:
        args.plots.mkdir(parents=True, exist_ok=True)
        plot_deviation_curve(df, args.plots)
        plot_declination_curve(df, args.plots)
        polar_wheel(df, args.plots)
        solar_progress_animation(df, args.plots)
        console.print(f"[green]Plots written to[/green] {args.plots}")


def handle_multi_year(args: argparse.Namespace):
    years = range(args.start, args.end + 1)
    paths = compute_and_store_years(years, out_dir=args.out, ephemeris_path=args.ephemeris)
    console.print(f"[green]Generated {len(paths)} calendars[/green] under {args.out}")


def handle_serve(args: argparse.Namespace):
    import uvicorn

    uvicorn.run("src.api.server:app", host=args.host, port=args.port, reload=True)


def main():
    args = parse_args()
    if args.command == "compute-year":
        handle_compute_year(args)
    elif args.command == "compare-year":
        handle_compare_year(args)
    elif args.command == "multi-year":
        handle_multi_year(args)
    elif args.command == "serve":
        handle_serve(args)
    else:
        raise SystemExit("Unknown command")


if __name__ == "__main__":
    main()
