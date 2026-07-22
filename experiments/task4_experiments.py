"""Evaluate bin-packing quality and runtime for Task 4."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
import random
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from task4_heuristics import (
    BinCapacity,
    Item,
    best_fit_decreasing,
    exact_branch_and_bound,
    local_search,
    resource_lower_bound,
    validate_packing,
)


CAPACITY = BinCapacity(100, 100, 100)
SMALL_SIZES = (8, 10, 12)
LARGE_SIZES = (25, 50, 100)


@dataclass(frozen=True)
class PackingMeasurement:
    method: str
    items: int
    trial: int
    bins: int
    lower_bound: int
    optimality_gap: int
    total_ns: int
    evaluated_moves: int
    accepted_moves: int


def generate_items(size: int, seed: int) -> list[Item]:
    generator = random.Random(seed)
    return [
        Item(
            f"I{index:03}",
            generator.randint(10, 70),
            generator.randint(10, 70),
            generator.randint(10, 70),
        )
        for index in range(size)
    ]


def timed(action) -> tuple[object, int]:
    start = perf_counter_ns()
    result = action()
    return result, perf_counter_ns() - start


def evaluate_instance(
    items: list[Item],
    trial: int,
    include_exact: bool,
) -> list[PackingMeasurement]:
    lower_bound = resource_lower_bound(items, CAPACITY)
    greedy, greedy_ns = timed(lambda: best_fit_decreasing(items, CAPACITY))
    improved, local_ns = timed(lambda: local_search(items, CAPACITY, greedy))
    methods = [
        ("Greedy", greedy, greedy_ns),
        ("Local search", improved, local_ns),
    ]
    optimum = -1
    if include_exact:
        exact, exact_ns = timed(lambda: exact_branch_and_bound(items, CAPACITY))
        optimum = exact.bin_count
        methods.append(("Exact", exact, exact_ns))

    rows = []
    for name, result, elapsed in methods:
        if not validate_packing(result, items, CAPACITY):
            raise AssertionError(f"{name} returned an infeasible packing")
        rows.append(
            PackingMeasurement(
                method=name,
                items=len(items),
                trial=trial,
                bins=result.bin_count,
                lower_bound=lower_bound,
                optimality_gap=result.bin_count - optimum if optimum >= 0 else -1,
                total_ns=elapsed,
                evaluated_moves=result.evaluated_moves,
                accepted_moves=result.accepted_moves,
            )
        )
    return rows


def run_experiments(trials: int) -> list[PackingMeasurement]:
    rows: list[PackingMeasurement] = []
    for size in SMALL_SIZES + LARGE_SIZES:
        for trial in range(1, trials + 1):
            items = generate_items(size, 24_0678 + size * 100 + trial)
            rows.extend(evaluate_instance(items, trial, size in SMALL_SIZES))
    return rows


def write_results(rows: list[PackingMeasurement], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def print_summary(rows: list[PackingMeasurement]) -> None:
    print("Task 4 heuristic evaluation (trial 1)")
    print("-" * 86)
    for row in rows:
        if row.trial != 1:
            continue
        gap = "n/a" if row.optimality_gap < 0 else str(row.optimality_gap)
        print(
            f"{row.method:12} n={row.items:3} bins={row.bins:3} "
            f"lower={row.lower_bound:3} gap={gap:>3} "
            f"time={row.total_ns / 1_000_000:9.3f} ms"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "experiments" / "data" / "task4_experiments.csv",
    )
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    measurements = run_experiments(arguments.trials)
    write_results(measurements, arguments.output)
    print_summary(measurements)
    print(f"\nRaw measurements written to {arguments.output}")
