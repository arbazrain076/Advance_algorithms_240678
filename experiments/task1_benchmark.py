"""Reproducible Task 1 wall-clock benchmark.

Run from the repository root:
    python experiments/task1_benchmark.py
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
import random
import statistics
import sys
from time import perf_counter_ns
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from task1_structures import AVLTree, BinarySearchTree, City, CityHashTable, MinHeap


SIZES = (100, 1_000, 10_000)
STRUCTURES = {
    "BST": BinarySearchTree,
    "AVL": AVLTree,
    "Min-Heap": MinHeap,
    "Hash Table": CityHashTable,
}


@dataclass(frozen=True)
class Measurement:
    structure: str
    input_order: str
    nodes: int
    operation: str
    trial: int
    operations: int
    total_ns: int
    ns_per_operation: float
    audit_metric: str
    audit_value: float


def generate_cities(size: int, seed: int) -> list[City]:
    """Create a deterministic synthetic dataset with unique searchable names."""

    generator = random.Random(seed)
    return [
        City(
            name=f"City {index:05d}",
            latitude=generator.uniform(-90, 90),
            longitude=generator.uniform(-180, 180),
            population=generator.randint(1_000, 10_000_000),
            distance=generator.uniform(0.1, 2_000),
        )
        for index in range(size)
    ]


def shuffled(items: Iterable[City], seed: int) -> list[City]:
    result = list(items)
    random.Random(seed).shuffle(result)
    return result


def measure(action: Callable[[], None], operations: int) -> tuple[int, float]:
    start = perf_counter_ns()
    action()
    elapsed = perf_counter_ns() - start
    return elapsed, elapsed / operations


def build(structure_name: str, cities: list[City]):
    structure = STRUCTURES[structure_name]()
    for city in cities:
        if structure_name == "Min-Heap":
            structure.push(city)
        else:
            structure.insert(city)
    return structure


def audit(structure_name: str, structure) -> tuple[str, float]:
    if structure_name in {"BST", "AVL"}:
        return "height", float(structure.height)
    if structure_name == "Hash Table":
        return "longest_chain", float(structure.statistics.longest_chain)
    return "heap_valid", float(structure.validate())


def run_trial(
    structure_name: str,
    ordered_cities: list[City],
    input_order: str,
    trial: int,
    seed: int,
) -> list[Measurement]:
    size = len(ordered_cities)
    output: list[Measurement] = []

    holder: dict[str, object] = {}

    def insert_all() -> None:
        holder["structure"] = build(structure_name, ordered_cities)

    elapsed, per_operation = measure(insert_all, size)
    structure = holder["structure"]
    metric, value = audit(structure_name, structure)
    output.append(
        Measurement(
            structure_name,
            input_order,
            size,
            "insert",
            trial,
            size,
            elapsed,
            per_operation,
            metric,
            value,
        )
    )

    query_count = min(size, 1_000)
    query_cities = random.Random(seed).sample(ordered_cities, query_count)

    def successful_search() -> None:
        for city in query_cities:
            structure.find(city.name)

    elapsed, per_operation = measure(successful_search, query_count)
    output.append(
        Measurement(
            structure_name,
            input_order,
            size,
            "successful_search",
            trial,
            query_count,
            elapsed,
            per_operation,
            metric,
            value,
        )
    )

    missing_names = [f"Missing {index:05d}" for index in range(query_count)]

    def unsuccessful_search() -> None:
        for name in missing_names:
            structure.find(name)

    elapsed, per_operation = measure(unsuccessful_search, query_count)
    output.append(
        Measurement(
            structure_name,
            input_order,
            size,
            "unsuccessful_search",
            trial,
            query_count,
            elapsed,
            per_operation,
            metric,
            value,
        )
    )

    delete_count = min(size // 10, 1_000)
    delete_cities = query_cities[:delete_count]

    def delete_sample() -> None:
        for city in delete_cities:
            if structure_name == "Min-Heap":
                structure.remove(city.name)
            else:
                structure.delete(city.name)

    elapsed, per_operation = measure(delete_sample, delete_count)
    output.append(
        Measurement(
            structure_name,
            input_order,
            size,
            "delete",
            trial,
            delete_count,
            elapsed,
            per_operation,
            metric,
            value,
        )
    )
    return output


def run_benchmark(trials: int) -> list[Measurement]:
    results: list[Measurement] = []
    for size in SIZES:
        cities = generate_cities(size, seed=24_0678 + size)
        for trial in range(1, trials + 1):
            trial_seed = 24_0678 + size * 10 + trial
            orders = {
                "random": shuffled(cities, trial_seed),
                "sorted": sorted(cities, key=lambda city: city.key),
            }
            for input_order, ordered_cities in orders.items():
                for structure_name in STRUCTURES:
                    results.extend(
                        run_trial(
                            structure_name,
                            ordered_cities,
                            input_order,
                            trial,
                            trial_seed,
                        )
                    )
    return results


def write_results(results: list[Measurement], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(results[0])))
        writer.writeheader()
        writer.writerows(asdict(result) for result in results)


def print_summary(results: list[Measurement]) -> None:
    groups: dict[tuple[str, str, int, str], list[float]] = {}
    for row in results:
        key = row.structure, row.input_order, row.nodes, row.operation
        groups.setdefault(key, []).append(row.ns_per_operation)

    print("Median nanoseconds per operation")
    print("-" * 78)
    for key, samples in sorted(groups.items()):
        structure, input_order, nodes, operation = key
        print(
            f"{structure:10} {input_order:6} n={nodes:5} "
            f"{operation:19} {statistics.median(samples):12.1f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5, help="repetitions per configuration")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "experiments" / "data" / "task1_benchmarks.csv",
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
