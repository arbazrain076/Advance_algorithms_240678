"""Generate dependency-free SVG charts from the Task 1 benchmark CSV."""

from __future__ import annotations

import csv
from pathlib import Path
import statistics
import math


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments" / "data" / "task1_benchmarks.csv"
OUTPUT = ROOT / "experiments" / "figures"
COLOURS = {
    "BST": "#0072B2",
    "AVL": "#D55E00",
    "Min-Heap": "#009E73",
    "Hash Table": "#CC79A7",
}


def load_medians() -> dict[tuple[str, str, int, str], float]:
    samples: dict[tuple[str, str, int, str], list[float]] = {}
    with DATA.open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = row["structure"], row["input_order"], int(row["nodes"]), row["operation"]
            samples.setdefault(key, []).append(float(row["ns_per_operation"]))
    return {key: statistics.median(values) for key, values in samples.items()}


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def line_chart(
    destination: Path,
    title: str,
    subtitle: str,
    series: dict[str, list[tuple[int, float]]],
) -> None:
    width, height = 960, 600
    left, right, top, bottom = 105, 35, 85, 85
    plot_width = width - left - right
    plot_height = height - top - bottom
    sizes = sorted({x for points in series.values() for x, _ in points})
    values = [value for points in series.values() for _, value in points]
    minimum_log = math.floor(math.log10(min(values)))
    maximum_log = math.ceil(math.log10(max(values)))
    if minimum_log == maximum_log:
        maximum_log += 1

    def x_position(value: int) -> float:
        return left + sizes.index(value) * plot_width / max(1, len(sizes) - 1)

    def y_position(value: float) -> float:
        ratio = (math.log10(value) - minimum_log) / (maximum_log - minimum_log)
        return top + plot_height * (1 - ratio)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(subtitle)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="35" font-family="Arial" font-size="24" font-weight="700" '
        f'fill="#222">{escape(title)}</text>',
        f'<text x="{left}" y="61" font-family="Arial" font-size="14" fill="#555">'
        f'{escape(subtitle)}</text>',
    ]

    for exponent in range(minimum_log, maximum_log + 1):
        value = 10**exponent
        y = y_position(value)
        label = f"{value / 1_000_000:g} ms" if value >= 1_000_000 else (
            f"{value / 1_000:g} us" if value >= 1_000 else f"{value:g} ns"
        )
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
                'stroke="#dddddd" stroke-width="1"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" '
                f'font-family="Arial" font-size="13" fill="#444">{label}</text>',
            ]
        )

    for size in sizes:
        x = x_position(size)
        elements.extend(
            [
                f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+plot_height}" '
                'stroke="#eeeeee" stroke-width="1"/>',
                f'<text x="{x:.1f}" y="{top+plot_height+28}" text-anchor="middle" '
                f'font-family="Arial" font-size="14" fill="#333">{size:,}</text>',
            ]
        )

    for label, points in series.items():
        colour = COLOURS.get(label.split(" - ")[0], "#333333")
        dash = ' stroke-dasharray="9 6"' if label.endswith("sorted") else ""
        coordinates = " ".join(
            f"{x_position(x):.1f},{y_position(y):.1f}" for x, y in sorted(points)
        )
        elements.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{colour}" '
            f'stroke-width="3" stroke-linejoin="round"{dash}/>'
        )
        for x, y in points:
            elements.append(
                f'<circle cx="{x_position(x):.1f}" cy="{y_position(y):.1f}" r="5" '
                f'fill="{colour}" stroke="#ffffff" stroke-width="2"/>'
            )

    legend_x = left
    legend_y = height - 25
    for index, label in enumerate(series):
        colour = COLOURS.get(label.split(" - ")[0], "#333333")
        dash = ' stroke-dasharray="9 6"' if label.endswith("sorted") else ""
        x = legend_x + index * 200
        elements.extend(
            [
                f'<line x1="{x}" y1="{legend_y-5}" x2="{x+28}" y2="{legend_y-5}" '
                f'stroke="{colour}" stroke-width="4"{dash}/>',
                f'<text x="{x+36}" y="{legend_y}" font-family="Arial" font-size="13" '
                f'fill="#222">{escape(label)}</text>',
            ]
        )

    elements.extend(
        [
            f'<text x="{left+plot_width/2:.1f}" y="{height-48}" text-anchor="middle" '
            'font-family="Arial" font-size="15" fill="#222">Dataset size (cities)</text>',
            f'<text transform="translate(24 {top+plot_height/2:.1f}) rotate(-90)" '
            'text-anchor="middle" font-family="Arial" font-size="15" fill="#222">'
            'Median time per operation (log scale)</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(elements), encoding="utf-8")


def main() -> None:
    medians = load_medians()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sizes = [100, 1_000, 10_000]

    for operation, filename, title in [
        ("insert", "task1_insert_random.svg", "Task 1: insertion performance"),
        (
            "successful_search",
            "task1_search_random.svg",
            "Task 1: successful city lookup",
        ),
        ("delete", "task1_delete_random.svg", "Task 1: deletion performance"),
    ]:
        series = {
            structure: [
                (size, medians[(structure, "random", size, operation)]) for size in sizes
            ]
            for structure in COLOURS
        }
        line_chart(
            OUTPUT / filename,
            title,
            "Five trials; random input; median wall-clock time; lower is better",
            series,
        )

    sensitivity = {
        f"{structure} - {order}": [
            (size, medians[(structure, order, size, "insert")]) for size in sizes
        ]
        for structure in ["BST", "AVL"]
        for order in ["random", "sorted"]
    }
    line_chart(
        OUTPUT / "task1_order_sensitivity.svg",
        "Task 1: tree sensitivity to insertion order",
        "Five trials; median wall-clock time; sorted input exposes the BST worst case",
        sensitivity,
    )
    print(f"Generated four SVG figures in {OUTPUT}")


if __name__ == "__main__":
    main()
