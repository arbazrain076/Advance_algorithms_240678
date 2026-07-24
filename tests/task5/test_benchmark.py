from __future__ import annotations

import csv

import pytest

from experiments.benchmark_scripts import task5_figures
from task5_concurrency.benchmark import (
    CSV_FIELDS,
    BenchmarkResult,
    generate_values,
    performance_metrics,
    run_benchmark,
    write_csv,
)


def test_generation_is_deterministic_and_signed() -> None:
    first = generate_values(100, 240_678)
    second = generate_values(100, 240_678)
    assert first == second
    assert any(value < 0 for value in first)
    assert any(value >= 0 for value in first)


def test_benchmark_rows_cover_all_worker_counts() -> None:
    rows = run_benchmark((1_024,), trials=1, threshold=128)

    assert len(rows) == 5
    assert {row.algorithm for row in rows} == {"Sequential", "Parallel"}
    assert {
        row.workers for row in rows if row.algorithm == "Parallel"
    } == {1, 2, 4, 8}
    assert all(row.correct for row in rows)
    assert all(row.total_ns > 0 for row in rows)

    metrics = performance_metrics(rows)
    assert set(worker for _, worker, _ in metrics) == {1, 2, 4, 8}
    assert all(speedup > 0 and efficiency > 0 for speedup, efficiency in metrics.values())


def test_csv_structure_and_figure_reader_compatibility(tmp_path) -> None:
    rows = [
        BenchmarkResult("Sequential", 100, 1, 1, 1_000, True, 42),
        BenchmarkResult("Parallel", 100, 1, 1, 900, True, 42),
        BenchmarkResult("Parallel", 100, 2, 1, 600, True, 42),
        BenchmarkResult("Parallel", 100, 4, 1, 400, True, 42),
        BenchmarkResult("Parallel", 100, 8, 1, 300, True, 42),
    ]
    destination = tmp_path / "task5_validation.csv"
    write_csv(rows, destination)

    with destination.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        written = list(reader)

    assert tuple(reader.fieldnames or ()) == CSV_FIELDS
    assert len(written) == 5
    assert {row["correct"] for row in written} == {"true"}

    medians = task5_figures.load_medians(destination)
    assert medians[("Sequential", 100, 1)] == pytest.approx(0.001)
    assert medians[("Parallel", 100, 8)] == pytest.approx(0.0003)


@pytest.mark.parametrize("trials", [0, -1])
def test_benchmark_trial_validation(trials: int) -> None:
    with pytest.raises(ValueError, match="trials"):
        run_benchmark((10,), trials=trials)
