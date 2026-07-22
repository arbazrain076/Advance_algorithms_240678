"""Generate Task 4 quality, runtime, and utilisation SVG figures."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from task4_heuristics import best_fit_decreasing, local_search
from task4_heuristics.bin_packing import bin_loads
from task4_experiments import CAPACITY, generate_items


DATA = ROOT / "experiments" / "data" / "task4_experiments.csv"
OUTPUT = ROOT / "experiments" / "figures"
COLOURS = {"Greedy": "#0072B2", "Local search": "#D55E00", "Exact": "#009E73"}


def load_rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def median_series(
    rows: list[dict[str, str]],
    field: str,
) -> dict[str, list[tuple[int, float]]]:
    groups: dict[tuple[str, int], list[float]] = {}
    for row in rows:
        groups.setdefault((row["method"], int(row["items"])), []).append(float(row[field]))
    output: dict[str, list[tuple[int, float]]] = {}
    for (method, size), values in groups.items():
        output.setdefault(method, []).append((size, statistics.median(values)))
    for values in output.values():
        values.sort()
    return output


def line_chart(
    destination: Path,
    title: str,
    subtitle: str,
    series: dict[str, list[tuple[int, float]]],
    y_label: str,
    log_scale: bool = False,
) -> None:
    width, height = 920, 570
    left, right, top, bottom = 100, 35, 90, 90
    plot_width = width - left - right
    plot_height = height - top - bottom
    x_values = sorted({x for points in series.values() for x, _ in points})
    values = [value for points in series.values() for _, value in points]

    def x_position(value: int) -> float:
        if len(x_values) == 1:
            return left + plot_width / 2
        low, high = min(x_values), max(x_values)
        return left + (value - low) * plot_width / (high - low)

    if log_scale:
        low_power = math.floor(math.log10(max(min(values), 1e-9)))
        high_power = math.ceil(math.log10(max(values)))

        def y_position(value: float) -> float:
            ratio = (math.log10(max(value, 1e-9)) - low_power) / max(
                1, high_power - low_power
            )
            return top + plot_height * (1 - ratio)

        ticks = [
            (10**power, f"10^{power}")
            for power in range(low_power, high_power + 1)
        ]
    else:
        maximum = max(values) * 1.1 or 1

        def y_position(value: float) -> float:
            return top + plot_height * (1 - value / maximum)

        ticks = [(maximum * tick / 5, f"{maximum * tick / 5:.0f}") for tick in range(6)]

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
    for value, label in ticks:
        y = y_position(value)
        parts.extend(
            [
                f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
                'stroke="#ddd"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" '
                f'font-family="Arial" font-size="13">{label}</text>',
            ]
        )
    for value in x_values:
        parts.append(
            f'<text x="{x_position(value):.1f}" y="{top+plot_height+28}" '
            f'text-anchor="middle" font-family="Arial" font-size="14">{value}</text>'
        )
    for index, (label, points) in enumerate(series.items()):
        colour = COLOURS.get(label, "#333")
        coordinates = " ".join(
            f"{x_position(x):.1f},{y_position(y):.1f}" for x, y in points
        )
        parts.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{colour}" '
            'stroke-width="3"/>'
        )
        for x, y in points:
            parts.append(
                f'<circle cx="{x_position(x):.1f}" cy="{y_position(y):.1f}" r="5" '
                f'fill="{colour}" stroke="#fff" stroke-width="2"/>'
            )
        legend_x = left + index * 220
        parts.extend(
            [
                f'<line x1="{legend_x}" y1="{height-24}" x2="{legend_x+28}" '
                f'y2="{height-24}" stroke="{colour}" stroke-width="4"/>',
                f'<text x="{legend_x+36}" y="{height-19}" font-family="Arial" '
                f'font-size="13">{label}</text>',
            ]
        )
    parts.extend(
        [
            f'<text x="{left+plot_width/2}" y="{height-52}" text-anchor="middle" '
            'font-family="Arial" font-size="15">Items</text>',
            f'<text transform="translate(23 {top+plot_height/2}) rotate(-90)" '
            f'text-anchor="middle" font-family="Arial" font-size="15">{y_label}</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(parts), encoding="utf-8")


def utilisation_heatmap(destination: Path) -> None:
    items = generate_items(12, 24_0678 + 12 * 100 + 1)
    result = local_search(items, CAPACITY, best_fit_decreasing(items, CAPACITY))
    width, height = 800, 150 + 56 * len(result.bins)
    labels = ("CPU", "RAM", "Bandwidth")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Task 4: local-search resource utilisation</title>',
        '<desc id="desc">Resource share in every bin for the 12-item trial-one solution.</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<text x="85" y="38" font-family="Arial" font-size="24" font-weight="700">'
        'Task 4: local-search resource utilisation</text>',
        '<text x="85" y="64" font-family="Arial" font-size="14" fill="#555">'
        '12-item trial 1; darker cells represent fuller resource dimensions</text>',
    ]
    for dimension, label in enumerate(labels):
        parts.append(
            f'<text x="{250+dimension*160}" y="102" text-anchor="middle" '
            f'font-family="Arial" font-size="14" font-weight="700">{label}</text>'
        )
    for row, group in enumerate(result.bins):
        y = 118 + row * 56
        parts.append(
            f'<text x="155" y="{y+29}" text-anchor="end" font-family="Arial" '
            f'font-size="14">Bin {row+1} ({len(group)} items)</text>'
        )
        loads = bin_loads(group)
        for dimension, (load, limit) in enumerate(zip(loads, CAPACITY.dimensions)):
            share = min(1.0, load / limit)
            blue = int(245 - 145 * share)
            x = 175 + dimension * 160
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="150" height="42" rx="6" '
                    f'fill="rgb({blue},{blue},{255})" stroke="#777"/>',
                    f'<text x="{x+75}" y="{y+26}" text-anchor="middle" '
                    f'font-family="Arial" font-size="14">{share*100:.0f}%</text>',
                ]
            )
    parts.append("</svg>")
    destination.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    rows = load_rows()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    quality = median_series(rows, "bins")
    lower_groups: dict[int, list[float]] = {}
    for row in rows:
        lower_groups.setdefault(int(row["items"]), []).append(float(row["lower_bound"]))
    quality["Resource lower bound"] = [
        (size, statistics.median(values)) for size, values in sorted(lower_groups.items())
    ]
    line_chart(
        OUTPUT / "task4_solution_quality.svg",
        "Task 4: packing solution quality",
        "Five-trial median bin count; exact results are shown only for small instances",
        quality,
        "Bins used",
    )
    runtime = {
        method: [(size, value / 1_000_000) for size, value in points]
        for method, points in median_series(rows, "total_ns").items()
    }
    line_chart(
        OUTPUT / "task4_runtime.svg",
        "Task 4: quality versus computational cost",
        "Five-trial median wall-clock time; logarithmic axis",
        runtime,
        "Runtime in milliseconds (log scale)",
        log_scale=True,
    )
    utilisation_heatmap(OUTPUT / "task4_utilisation_heatmap.svg")
    print(f"Generated three Task 4 SVG figures in {OUTPUT}")


if __name__ == "__main__":
    main()
