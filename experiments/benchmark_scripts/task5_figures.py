"""Generate Task 5 runtime, speedup, and efficiency SVG figures."""

from __future__ import annotations

import csv
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "experiments" / "benchmark_data" / "task5_benchmarks.csv"
OUTPUT = ROOT / "experiments" / "figures"
COLOURS = ["#0072B2", "#D55E00", "#009E73", "#777777"]


def load_medians(
    data_path: Path = DATA,
) -> dict[tuple[str, int, int], float]:
    samples: dict[tuple[str, int, int], list[float]] = {}
    with data_path.open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = row["algorithm"], int(row["elements"]), int(row["workers"])
            samples.setdefault(key, []).append(int(row["total_ns"]) / 1_000_000)
    return {key: statistics.median(values) for key, values in samples.items()}


def line_chart(
    destination: Path,
    title: str,
    subtitle: str,
    series: dict[str, list[tuple[int, float]]],
    y_label: str,
    y_maximum: float | None = None,
) -> None:
    width, height = 920, 570
    left, right, top, bottom = 100, 35, 90, 90
    plot_width = width - left - right
    plot_height = height - top - bottom
    x_values = sorted({x for points in series.values() for x, _ in points})
    values = [value for points in series.values() for _, value in points]
    maximum = y_maximum or max(values) * 1.1

    def x_position(value: int) -> float:
        return left + x_values.index(value) * plot_width / max(1, len(x_values) - 1)

    def y_position(value: float) -> float:
        return top + plot_height * (1 - value / maximum)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{title}</title>',
        f'<desc id="desc">{subtitle}</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<text x="{left}" y="38" font-family="Arial" font-size="24" font-weight="700">'
        f'{title}</text>',
        f'<text x="{left}" y="64" font-family="Arial" font-size="14" fill="#555">'
        f'{subtitle}</text>',
    ]
    for tick in range(6):
        value = maximum * tick / 5
        y = y_position(value)
        parts.extend(
            [
                f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
                'stroke="#ddd"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" '
                f'font-family="Arial" font-size="13">{value:.1f}</text>',
            ]
        )
    for value in x_values:
        parts.append(
            f'<text x="{x_position(value):.1f}" y="{top+plot_height+28}" '
            f'text-anchor="middle" font-family="Arial" font-size="14">{value}</text>'
        )
    for index, (label, points) in enumerate(series.items()):
        colour = COLOURS[index % len(COLOURS)]
        dash = ' stroke-dasharray="8 6"' if label == "Ideal" else ""
        coordinates = " ".join(
            f"{x_position(x):.1f},{y_position(y):.1f}" for x, y in points
        )
        parts.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{colour}" '
            f'stroke-width="3"{dash}/>'
        )
        for x, y in points:
            parts.append(
                f'<circle cx="{x_position(x):.1f}" cy="{y_position(y):.1f}" r="5" '
                f'fill="{colour}" stroke="#fff" stroke-width="2"/>'
            )
        legend_x = left + index * 190
        parts.extend(
            [
                f'<line x1="{legend_x}" y1="{height-24}" x2="{legend_x+28}" '
                f'y2="{height-24}" stroke="{colour}" stroke-width="4"{dash}/>',
                f'<text x="{legend_x+36}" y="{height-19}" font-family="Arial" '
                f'font-size="13">{label}</text>',
            ]
        )
    parts.extend(
        [
            f'<text x="{left+plot_width/2}" y="{height-52}" text-anchor="middle" '
            'font-family="Arial" font-size="15">Worker threads</text>',
            f'<text transform="translate(23 {top+plot_height/2}) rotate(-90)" '
            f'text-anchor="middle" font-family="Arial" font-size="15">{y_label}</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    medians = load_medians()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sizes = [100_000, 500_000, 2_000_000]
    workers = [1, 2, 4, 8]
    labels = {100_000: "100 thousand", 500_000: "500 thousand", 2_000_000: "2 million"}

    runtimes = {
        labels[size]: [
            (worker, medians[("Parallel", size, worker)]) for worker in workers
        ]
        for size in sizes
    }
    line_chart(
        OUTPUT / "task5_runtime.svg",
        "Task 5: concurrent merge-sort runtime",
        "Five-trial median; every result verified against the same sorted reference",
        runtimes,
        "Median runtime (milliseconds)",
    )

    speedups = {}
    efficiencies = {}
    for size in sizes:
        baseline = medians[("Sequential", size, 1)]
        speedups[labels[size]] = [
            (worker, baseline / medians[("Parallel", size, worker)])
            for worker in workers
        ]
        efficiencies[labels[size]] = [
            (worker, baseline / medians[("Parallel", size, worker)] / worker)
            for worker in workers
        ]
    speedups["Ideal"] = [(worker, float(worker)) for worker in workers]
    line_chart(
        OUTPUT / "task5_speedup.svg",
        "Task 5: speedup versus worker count",
        "Speedup = median sequential time / median concurrent time",
        speedups,
        "Speedup",
        y_maximum=8.5,
    )
    line_chart(
        OUTPUT / "task5_efficiency.svg",
        "Task 5: parallel efficiency",
        "Efficiency = speedup / worker count; values above 1 reflect measurement variation",
        efficiencies,
        "Parallel efficiency",
        y_maximum=1.2,
    )
    print(f"Generated three Task 5 SVG figures in {OUTPUT}")


if __name__ == "__main__":
    main()
