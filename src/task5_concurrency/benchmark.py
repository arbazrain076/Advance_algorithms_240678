"""Reproducible benchmark for sequential and process-based parallel merge sort."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import random
import time
from typing import Iterable, Sequence

from .parallel_merge_sort import (
    DEFAULT_THRESHOLD,
    SUPPORTED_WORKER_COUNTS,
    is_sorted,
    parallel_merge_sort,
    sequential_merge_sort,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "experiments" / "benchmark_data" / "task5_benchmarks.csv"
FULL_SIZES = (100_000, 500_000, 2_000_000)
QUICK_SIZES = (1_000, 10_000)
CSV_FIELDS = (
    "algorithm",
    "elements",
    "workers",
    "trial",
    "total_ns",
    "correct",
    "checksum",
)


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    algorithm: str
    elements: int
    workers: int
    trial: int
    total_ns: int
    correct: bool
    checksum: int


def generate_values(size: int, seed: int) -> list[int]:
    """Generate deterministic signed 64-bit values."""

    if size < 0:
        raise ValueError("size must not be negative")
    generator = random.Random(seed)
    return [generator.getrandbits(64) - (1 << 63) for _ in range(size)]


def signed_array_checksum(values: Iterable[int]) -> int:
    """Return a stable signed 32-bit checksum for a sequence of integers."""

    result = 1
    for value in values:
        unsigned = value & ((1 << 64) - 1)
        element_hash = (unsigned ^ (unsigned >> 32)) & 0xFFFFFFFF
        result = (31 * result + element_hash) & 0xFFFFFFFF
    return result if result < (1 << 31) else result - (1 << 32)


def _configurations() -> list[tuple[str, int]]:
    return [("Sequential", 1)] + [
        ("Parallel", workers) for workers in SUPPORTED_WORKER_COUNTS
    ]


def _rotated_configurations(trial: int) -> list[tuple[str, int]]:
    configurations = _configurations()
    offset = (trial - 1) % len(configurations)
    if offset:
        configurations = configurations[-offset:] + configurations[:-offset]
    return configurations


def run_benchmark(
    sizes: Sequence[int],
    trials: int,
    threshold: int = DEFAULT_THRESHOLD,
) -> list[BenchmarkResult]:
    """Benchmark every required worker count and validate every sorted result."""

    if trials < 1:
        raise ValueError("trials must be positive")
    if any(size < 0 for size in sizes):
        raise ValueError("sizes must not contain negative values")

    results: list[BenchmarkResult] = []
    for size in sizes:
        values = generate_values(size, 240_678 + size)
        reference = sorted(values)

        for trial in range(1, trials + 1):
            for algorithm, workers in _rotated_configurations(trial):
                started = time.perf_counter()
                if algorithm == "Sequential":
                    actual = sequential_merge_sort(values)
                else:
                    actual = parallel_merge_sort(
                        values,
                        worker_count=workers,
                        threshold=threshold,
                    )
                elapsed_ns = max(
                    1,
                    int((time.perf_counter() - started) * 1_000_000_000),
                )
                correct = actual == reference and is_sorted(actual)
                if not correct:
                    raise RuntimeError(
                        f"incorrect {algorithm} result with {workers} worker(s)"
                    )
                results.append(
                    BenchmarkResult(
                        algorithm=algorithm,
                        elements=size,
                        workers=workers,
                        trial=trial,
                        total_ns=elapsed_ns,
                        correct=True,
                        checksum=signed_array_checksum(actual),
                    )
                )
    return results


def performance_metrics(
    results: Iterable[BenchmarkResult],
) -> dict[tuple[int, int, int], tuple[float, float]]:
    """Return ``(speedup, efficiency)`` for every parallel result."""

    rows = list(results)
    baselines = {
        (row.elements, row.trial): row.total_ns
        for row in rows
        if row.algorithm == "Sequential"
    }
    metrics: dict[tuple[int, int, int], tuple[float, float]] = {}
    for row in rows:
        if row.algorithm != "Parallel":
            continue
        baseline = baselines[(row.elements, row.trial)]
        speedup = baseline / row.total_ns
        metrics[(row.elements, row.workers, row.trial)] = (
            speedup,
            speedup / row.workers,
        )
    return metrics


def write_csv(results: Iterable[BenchmarkResult], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in results:
            writer.writerow(
                {
                    "algorithm": row.algorithm,
                    "elements": row.elements,
                    "workers": row.workers,
                    "trial": row.trial,
                    "total_ns": row.total_ns,
                    "correct": str(row.correct).lower(),
                    "checksum": row.checksum,
                }
            )


def warm_up(threshold: int) -> None:
    values = generate_values(50_000, 240_678)
    for _ in range(2):
        sequential_merge_sort(values)
        parallel_merge_sort(
            values,
            worker_count=4,
            threshold=min(threshold, 10_000),
        )


def print_summary(results: Iterable[BenchmarkResult]) -> None:
    rows = list(results)
    metrics = performance_metrics(rows)
    print("Task 5 process-based merge-sort benchmark")
    print("-" * 92)
    for row in rows:
        if row.trial != 1:
            continue
        detail = ""
        if row.algorithm == "Parallel":
            speedup, efficiency = metrics[(row.elements, row.workers, row.trial)]
            detail = f" speedup={speedup:6.3f} efficiency={efficiency:6.3f}"
        print(
            f"{row.algorithm:10} workers={row.workers} n={row.elements:9d} "
            f"time={row.total_ns / 1_000_000:9.3f} ms "
            f"correct={str(row.correct).lower()}{detail}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--quick", action="store_true")
    arguments = parser.parse_args()
    if arguments.trials < 1:
        parser.error("--trials must be positive")
    if arguments.threshold < 1:
        parser.error("--threshold must be positive")
    return arguments


def main() -> None:
    arguments = parse_args()
    sizes = QUICK_SIZES if arguments.quick else FULL_SIZES
    warm_up(arguments.threshold)
    results = run_benchmark(sizes, arguments.trials, arguments.threshold)
    write_csv(results, arguments.output)
    print_summary(results)
    print(f"\nRaw measurements written to {arguments.output.resolve()}")


if __name__ == "__main__":
    main()
