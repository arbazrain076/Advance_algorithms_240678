"""Benchmark Dijkstra, Bellman-Ford, and Prim on sparse and dense graphs."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import math
from pathlib import Path
import random
import statistics
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from task2_graphs import (
    WeightedGraph,
    bellman_ford,
    dijkstra,
    prim_minimum_spanning_forest,
)


SIZES = (50, 100, 200)
DENSITIES = {"sparse": 0.05, "dense": 0.35}


@dataclass(frozen=True)
class GraphMeasurement:
    algorithm: str
    graph_type: str
    vertices: int
    edges: int
    actual_density: float
    trial: int
    total_ns: int
    complexity_units: float
    ns_per_complexity_unit: float
    trace_events: int


def generate_graph(vertices: int, density: float, seed: int) -> WeightedGraph:
    """Generate a reproducible directed graph with non-negative weights."""

    if vertices < 2:
        raise ValueError("vertices must be at least two")
    if not 0 < density <= 1:
        raise ValueError("density must be in (0, 1]")

    generator = random.Random(seed)
    graph = WeightedGraph(directed=True)
    for vertex in range(vertices):
        graph.add_vertex(vertex)

    # A bidirectional backbone makes every vertex reachable from vertex zero.
    for vertex in range(vertices - 1):
        graph.add_edge(vertex, vertex + 1, generator.randint(1, 50))
        graph.add_edge(vertex + 1, vertex, generator.randint(1, 50))

    target_edges = max(graph.edge_count, round(density * vertices * (vertices - 1)))
    candidates = [
        (source, target)
        for source in range(vertices)
        for target in range(vertices)
        if source != target and graph.weight(source, target) is None
    ]
    generator.shuffle(candidates)
    for source, target in candidates[: target_edges - graph.edge_count]:
        graph.add_edge(source, target, generator.randint(1, 100))
    return graph


def time_call(action) -> tuple[object, int]:
    start = perf_counter_ns()
    result = action()
    return result, perf_counter_ns() - start


def run_trial(
    graph: WeightedGraph,
    graph_type: str,
    trial: int,
) -> list[GraphMeasurement]:
    vertices = len(graph)
    edges = graph.edge_count
    density = edges / (vertices * (vertices - 1))
    undirected = graph.as_undirected()

    algorithms = [
        (
            "Dijkstra",
            lambda: dijkstra(graph, 0),
            (vertices + edges) * math.log2(vertices),
        ),
        (
            "Bellman-Ford",
            lambda: bellman_ford(graph, 0),
            vertices * edges,
        ),
        (
            "Prim",
            lambda: prim_minimum_spanning_forest(undirected),
            (vertices + undirected.edge_count) * math.log2(vertices),
        ),
    ]

    rows: list[GraphMeasurement] = []
    for name, action, units in algorithms:
        result, elapsed = time_call(action)
        rows.append(
            GraphMeasurement(
                algorithm=name,
                graph_type=graph_type,
                vertices=vertices,
                edges=edges if name != "Prim" else undirected.edge_count,
                actual_density=density,
                trial=trial,
                total_ns=elapsed,
                complexity_units=units,
                ns_per_complexity_unit=elapsed / units,
                trace_events=len(result.events),
            )
        )
    return rows


def run_benchmark(trials: int) -> list[GraphMeasurement]:
    rows: list[GraphMeasurement] = []
    for vertices in SIZES:
        for graph_type, density in DENSITIES.items():
            for trial in range(1, trials + 1):
                graph = generate_graph(
                    vertices,
                    density,
                    seed=24_0678 + vertices * 100 + trial,
                )
                rows.extend(run_trial(graph, graph_type, trial))
    return rows


def write_results(rows: list[GraphMeasurement], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def print_summary(rows: list[GraphMeasurement]) -> None:
    groups: dict[tuple[str, str, int], list[GraphMeasurement]] = {}
    for row in rows:
        groups.setdefault((row.algorithm, row.graph_type, row.vertices), []).append(row)

    print("Median wall-clock time and observed constant-factor proxy")
    print("-" * 88)
    for key, samples in sorted(groups.items()):
        algorithm, graph_type, vertices = key
        milliseconds = statistics.median(row.total_ns for row in samples) / 1_000_000
        constant = statistics.median(row.ns_per_complexity_unit for row in samples)
        print(
            f"{algorithm:12} {graph_type:6} V={vertices:3} "
            f"time={milliseconds:9.3f} ms  ns/unit={constant:9.3f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "experiments" / "benchmark_data" / "task2_benchmarks.csv",
    )
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    measurements = run_benchmark(arguments.trials)
    write_results(measurements, arguments.output)
    print_summary(measurements)
    print(f"\nRaw measurements written to {arguments.output}")
