"""Generate Task 2 runtime charts and step-by-step SVG timelines."""

from __future__ import annotations

import csv
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from task2_graphs import (
    WeightedGraph,
    bellman_ford,
    dijkstra,
    prim_minimum_spanning_forest,
)


DATA = ROOT / "experiments" / "benchmark_data" / "task2_benchmarks.csv"
OUTPUT = ROOT / "experiments" / "figures"
COLOURS = {
    "Dijkstra": "#0072B2",
    "Bellman-Ford": "#D55E00",
    "Prim": "#009E73",
}


def escape(value: object) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_timeline(
    destination: Path,
    title: str,
    subtitle: str,
    rows: list[tuple[str, str, str]],
    colour: str,
) -> None:
    width = 980
    row_height = 58
    height = 120 + row_height * len(rows)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(subtitle)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="65" y="38" font-family="Arial" font-size="24" font-weight="700" '
        f'fill="#222">{escape(title)}</text>',
        f'<text x="65" y="64" font-family="Arial" font-size="14" fill="#555">'
        f'{escape(subtitle)}</text>',
        f'<line x1="90" y1="96" x2="90" y2="{height-35}" stroke="{colour}" '
        'stroke-width="4"/>',
    ]
    for index, (heading, detail, metric) in enumerate(rows, 1):
        y = 96 + (index - 1) * row_height
        parts.extend(
            [
                f'<circle cx="90" cy="{y}" r="16" fill="{colour}"/>',
                f'<text x="90" y="{y+5}" text-anchor="middle" font-family="Arial" '
                f'font-size="13" font-weight="700" fill="#fff">{index}</text>',
                f'<text x="125" y="{y-2}" font-family="Arial" font-size="16" '
                f'font-weight="700" fill="#222">{escape(heading)}</text>',
                f'<text x="125" y="{y+20}" font-family="Arial" font-size="14" '
                f'fill="#555">{escape(detail)}</text>',
                f'<rect x="735" y="{y-23}" width="190" height="36" rx="8" '
                'fill="#f3f5f7"/>',
                f'<text x="830" y="{y}" text-anchor="middle" font-family="Arial" '
                f'font-size="14" fill="#222">{escape(metric)}</text>',
            ]
        )
    parts.append("</svg>")
    destination.write_text("\n".join(parts), encoding="utf-8")


def load_runtime_medians() -> dict[tuple[str, str, int], float]:
    groups: dict[tuple[str, str, int], list[float]] = {}
    with DATA.open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = row["algorithm"], row["graph_type"], int(row["vertices"])
            groups.setdefault(key, []).append(int(row["total_ns"]) / 1_000_000)
    return {key: statistics.median(values) for key, values in groups.items()}


def write_runtime_chart(destination: Path, graph_type: str) -> None:
    medians = load_runtime_medians()
    width, height = 900, 560
    left, right, top, bottom = 90, 35, 90, 85
    plot_width = width - left - right
    plot_height = height - top - bottom
    sizes = [50, 100, 200]
    values = [
        medians[(algorithm, graph_type, size)]
        for algorithm in COLOURS
        for size in sizes
    ]
    maximum = max(values) * 1.1

    def x_position(size: int) -> float:
        return left + sizes.index(size) * plot_width / (len(sizes) - 1)

    def y_position(value: float) -> float:
        return top + plot_height * (1 - value / maximum)

    title = f"Task 2: {graph_type} graph runtime"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{title}</title>',
        '<desc id="desc">Five-trial median wall-clock runtime; lower is better.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="38" font-family="Arial" font-size="24" font-weight="700" '
        f'fill="#222">{title}</text>',
        f'<text x="{left}" y="64" font-family="Arial" font-size="14" fill="#555">'
        'Five trials; median wall-clock runtime; lower is better</text>',
    ]
    for tick in range(6):
        value = maximum * tick / 5
        y = y_position(value)
        parts.extend(
            [
                f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
                'stroke="#dddddd"/>',
                f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" '
                f'font-family="Arial" font-size="13" fill="#444">{value:.1f} ms</text>',
            ]
        )
    for size in sizes:
        x = x_position(size)
        parts.append(
            f'<text x="{x:.1f}" y="{top+plot_height+28}" text-anchor="middle" '
            f'font-family="Arial" font-size="14" fill="#333">{size}</text>'
        )
    for index, (algorithm, colour) in enumerate(COLOURS.items()):
        points = [
            (size, medians[(algorithm, graph_type, size)]) for size in sizes
        ]
        coordinates = " ".join(
            f"{x_position(size):.1f},{y_position(value):.1f}" for size, value in points
        )
        parts.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{colour}" '
            'stroke-width="3"/>'
        )
        for size, value in points:
            parts.append(
                f'<circle cx="{x_position(size):.1f}" cy="{y_position(value):.1f}" '
                f'r="5" fill="{colour}" stroke="#fff" stroke-width="2"/>'
            )
        legend_x = left + index * 210
        parts.extend(
            [
                f'<line x1="{legend_x}" y1="{height-24}" x2="{legend_x+28}" '
                f'y2="{height-24}" stroke="{colour}" stroke-width="4"/>',
                f'<text x="{legend_x+36}" y="{height-19}" font-family="Arial" '
                f'font-size="13" fill="#222">{algorithm}</text>',
            ]
        )
    parts.extend(
        [
            f'<text x="{left+plot_width/2}" y="{height-50}" text-anchor="middle" '
            'font-family="Arial" font-size="15">Vertices</text>',
            f'<text transform="translate(22 {top+plot_height/2}) rotate(-90)" '
            'text-anchor="middle" font-family="Arial" font-size="15">'
            'Median runtime (milliseconds)</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(parts), encoding="utf-8")


def dijkstra_demo() -> None:
    graph = WeightedGraph()
    for source, target, weight in [
        ("KTM", "BKT", 12),
        ("KTM", "PKR", 200),
        ("BKT", "DHK", 18),
        ("DHK", "PKR", 145),
    ]:
        graph.add_edge(source, target, weight)
    result = dijkstra(graph, "KTM")
    rows = []
    for event in result.events:
        if event.action == "settle":
            rows.append(
                (
                    f"Settle {event.vertex}",
                    "Shortest distance is now final",
                    f"distance = {event.new_distance:g}",
                )
            )
        else:
            old = "infinity" if event.old_distance == float("inf") else f"{event.old_distance:g}"
            rows.append(
                (
                    f"Relax {event.source} to {event.vertex}",
                    f"Improve tentative distance from {old}",
                    f"new = {event.new_distance:g}",
                )
            )
    write_timeline(
        OUTPUT / "task2_dijkstra_trace.svg",
        "Dijkstra execution trace",
        "Directed transport network from KTM; only successful relaxations are shown",
        rows,
        COLOURS["Dijkstra"],
    )


def prim_demo() -> None:
    graph = WeightedGraph(directed=False)
    for source, target, weight in [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
    ]:
        graph.add_edge(source, target, weight)
    result = prim_minimum_spanning_forest(graph)
    rows = []
    for event in result.events:
        if event.action == "start_component":
            rows.append((f"Start at {event.vertex}", "Create the first tree component", "weight = 0"))
        else:
            rows.append(
                (
                    f"Select {event.source} to {event.vertex}",
                    "Cheapest edge crossing the current cut",
                    f"total = {event.running_weight:g}",
                )
            )
    write_timeline(
        OUTPUT / "task2_prim_trace.svg",
        "Prim minimum spanning tree trace",
        "Each chosen edge is the cheapest edge crossing the visited/unvisited cut",
        rows,
        COLOURS["Prim"],
    )


def bellman_ford_demo() -> None:
    graph = WeightedGraph()
    for source, target, weight in [
        ("S", "A", 1),
        ("A", "B", 1),
        ("B", "C", -4),
        ("C", "A", 1),
        ("C", "D", 2),
    ]:
        graph.add_edge(source, target, weight)
    result = bellman_ford(graph, "S")
    cycle = " -> ".join(map(str, result.negative_cycle))
    rows = [
        (
            f"Pass {event.pass_number}: relax {event.source} to {event.target}",
            "A lower distance was discovered",
            f"new = {event.new_distance:g}",
        )
        for event in result.events
    ]
    rows.append(
        (
            "Extra relaxation remains possible",
            f"Cycle witness: {cycle}",
            f"affected = {len(result.affected_vertices)}",
        )
    )
    write_timeline(
        OUTPUT / "task2_bellman_ford_trace.svg",
        "Bellman-Ford negative-cycle trace",
        "A reachable negative cycle keeps lowering distances after V - 1 passes",
        rows,
        COLOURS["Bellman-Ford"],
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_runtime_chart(OUTPUT / "task2_runtime_sparse.svg", "sparse")
    write_runtime_chart(OUTPUT / "task2_runtime_dense.svg", "dense")
    dijkstra_demo()
    prim_demo()
    bellman_ford_demo()
    print(f"Generated five Task 2 SVG figures in {OUTPUT}")


if __name__ == "__main__":
    main()
