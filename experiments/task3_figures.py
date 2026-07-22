"""Generate dependency-free SVG figures from Task 3 experiment results."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments" / "data" / "task3_experiments.csv"
OUTPUT = ROOT / "experiments" / "figures"
COLOURS = ["#0072B2", "#D55E00", "#009E73"]


def load_rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def line_chart(
    destination: Path,
    title: str,
    subtitle: str,
    series: dict[str, list[tuple[int, float]]],
    y_label: str,
    log_scale: bool,
) -> None:
    width, height = 920, 570
    left, right, top, bottom = 100, 35, 90, 90
    plot_width = width - left - right
    plot_height = height - top - bottom
    x_values = sorted({x for points in series.values() for x, _ in points})
    all_values = [value for points in series.values() for _, value in points]
    minimum = min(all_values)
    maximum = max(all_values)

    def x_position(value: int) -> float:
        return left + x_values.index(value) * plot_width / max(1, len(x_values) - 1)

    if log_scale:
        low = math.floor(math.log10(max(minimum, 1e-9)))
        high = math.ceil(math.log10(maximum))

        def y_position(value: float) -> float:
            ratio = (math.log10(max(value, 1e-9)) - low) / max(1, high - low)
            return top + plot_height * (1 - ratio)

        ticks = [(10**power, f"10^{power}") for power in range(low, high + 1)]
    else:
        high_value = maximum * 1.1 or 1

        def y_position(value: float) -> float:
            return top + plot_height * (1 - value / high_value)

        ticks = [
            (high_value * tick / 5, f"{high_value * tick / 5:.0f}")
            for tick in range(6)
        ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{title}</title>',
        f'<desc id="desc">{subtitle}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="38" font-family="Arial" font-size="24" font-weight="700" '
        f'fill="#222">{title}</text>',
        f'<text x="{left}" y="64" font-family="Arial" font-size="14" fill="#555">'
        f'{subtitle}</text>',
    ]
    for value, label in ticks:
        y = y_position(value)
        parts.extend(
            [
                f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
                'stroke="#dddddd"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" '
                f'font-family="Arial" font-size="13" fill="#444">{label}</text>',
            ]
        )
    for value in x_values:
        x = x_position(value)
        parts.append(
            f'<text x="{x:.1f}" y="{top+plot_height+28}" text-anchor="middle" '
            f'font-family="Arial" font-size="14">{value}</text>'
        )
    for index, (label, points) in enumerate(series.items()):
        colour = COLOURS[index % len(COLOURS)]
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
        legend_x = left + index * 235
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
            'font-family="Arial" font-size="15">Problem size</text>',
            f'<text transform="translate(23 {top+plot_height/2}) rotate(-90)" '
            f'text-anchor="middle" font-family="Arial" font-size="15">{y_label}</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(parts), encoding="utf-8")


def medians(
    rows: list[dict[str, str]],
    experiment: str,
    value_field: str,
) -> dict[str, list[tuple[int, float]]]:
    groups: dict[tuple[str, int], list[float]] = {}
    for row in rows:
        if row["experiment"] != experiment:
            continue
        key = row["method"], int(row["size"])
        groups.setdefault(key, []).append(float(row[value_field]))
    output: dict[str, list[tuple[int, float]]] = {}
    for (method, size), values in groups.items():
        output.setdefault(method, []).append((size, statistics.median(values)))
    for points in output.values():
        points.sort()
    return output


def main() -> None:
    rows = load_rows()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    runtime = medians(rows, "weighted_jobs", "total_ns")
    runtime_ms = {
        method: [(size, value / 1_000_000) for size, value in points]
        for method, points in runtime.items()
    }
    line_chart(
        OUTPUT / "task3_dp_vs_exhaustive.svg",
        "Task 3: DP versus exhaustive scheduling",
        "Five-trial median; logarithmic runtime axis; both methods return the same optimum",
        runtime_ms,
        "Median runtime in milliseconds (log scale)",
        True,
    )
    line_chart(
        OUTPUT / "task3_greedy_gap.svg",
        "Task 3: weighted greedy optimality gaps",
        "Five deterministic instances per size; median exact-profit minus greedy-profit",
        medians(rows, "weighted_greedy", "optimality_gap"),
        "Median optimality gap",
        False,
    )
    line_chart(
        OUTPUT / "task3_backtracking_nodes.svg",
        "Task 3: pruning the timetabling search",
        "Infeasible single-room instances; median explored placements; log scale",
        medians(rows, "exam_timetabling", "nodes_visited"),
        "Explored placements (log scale)",
        True,
    )
    print(f"Generated three Task 3 SVG figures in {OUTPUT}")


if __name__ == "__main__":
    main()
