"""Run reproducible experiments for Task 3's three algorithmic paradigms."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
import random
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from task3_strategies import (
    Exam,
    ExamTimetabler,
    Job,
    Room,
    exhaustive_weighted_schedule,
    greedy_weighted_schedule,
    weighted_job_schedule,
)


@dataclass(frozen=True)
class StrategyMeasurement:
    experiment: str
    method: str
    size: int
    trial: int
    total_ns: int
    objective: float
    optimality_gap: float
    nodes_visited: int
    backtracks: int
    forward_prunes: int


def generate_jobs(size: int, seed: int) -> list[Job]:
    generator = random.Random(seed)
    jobs = []
    for index in range(size):
        start = generator.randint(0, size * 3)
        jobs.append(
            Job(
                identifier=f"J{index:03}",
                start=start,
                end=start + generator.randint(1, max(2, size // 3)),
                profit=generator.randint(1, 100),
            )
        )
    return jobs


def timed(action) -> tuple[object, int]:
    start = perf_counter_ns()
    result = action()
    return result, perf_counter_ns() - start


def dynamic_programming_experiment(trials: int) -> list[StrategyMeasurement]:
    rows: list[StrategyMeasurement] = []
    for size in (5, 10, 14, 16):
        for trial in range(1, trials + 1):
            jobs = generate_jobs(size, 24_0678 + size * 100 + trial)
            dynamic, dynamic_ns = timed(lambda: weighted_job_schedule(jobs))
            exhaustive, exhaustive_ns = timed(lambda: exhaustive_weighted_schedule(jobs))
            if dynamic.maximum_profit != exhaustive.maximum_profit:
                raise AssertionError("dynamic and exhaustive objectives differ")
            for method, result, elapsed in [
                ("Dynamic programming", dynamic, dynamic_ns),
                ("Exhaustive search", exhaustive, exhaustive_ns),
            ]:
                rows.append(
                    StrategyMeasurement(
                        "weighted_jobs",
                        method,
                        size,
                        trial,
                        elapsed,
                        result.maximum_profit,
                        0.0,
                        0,
                        0,
                        0,
                    )
                )
    return rows


def greedy_experiment(trials: int) -> list[StrategyMeasurement]:
    rows: list[StrategyMeasurement] = []
    for size in (10, 25, 50):
        for trial in range(1, trials + 1):
            jobs = generate_jobs(size, 48_1356 + size * 100 + trial)
            optimal = weighted_job_schedule(jobs)
            for rule in ("earliest_finish", "shortest_duration", "highest_weight"):
                result, elapsed = timed(lambda rule=rule: greedy_weighted_schedule(jobs, rule))
                rows.append(
                    StrategyMeasurement(
                        "weighted_greedy",
                        rule,
                        size,
                        trial,
                        elapsed,
                        result.maximum_profit,
                        optimal.maximum_profit - result.maximum_profit,
                        0,
                        0,
                        0,
                    )
                )
    return rows


def backtracking_experiment(trials: int) -> list[StrategyMeasurement]:
    rows: list[StrategyMeasurement] = []
    for size in (5, 6, 7, 8):
        # n exams in n - 1 single-room slots is deliberately infeasible.
        exams = [Exam(f"E{index}", 10) for index in range(size)]
        solver = ExamTimetabler(
            exams,
            conflicts=[],
            slots=size - 1,
            rooms=[Room("R1", 20)],
        )
        for trial in range(1, trials + 1):
            for method, use_pruning in [("Baseline", False), ("Pruned", True)]:
                result, elapsed = timed(lambda flag=use_pruning: solver.solve(flag))
                if result.solved:
                    raise AssertionError("resource-bottleneck instance should be infeasible")
                rows.append(
                    StrategyMeasurement(
                        "exam_timetabling",
                        method,
                        size,
                        trial,
                        elapsed,
                        0.0,
                        0.0,
                        result.nodes_visited,
                        result.backtracks,
                        result.forward_prunes,
                    )
                )
    return rows


def run_experiments(trials: int) -> list[StrategyMeasurement]:
    return (
        dynamic_programming_experiment(trials)
        + greedy_experiment(trials)
        + backtracking_experiment(trials)
    )


def write_results(rows: list[StrategyMeasurement], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def print_summary(rows: list[StrategyMeasurement]) -> None:
    print("Task 3 experiment summary")
    print("-" * 78)
    for row in rows:
        if row.trial != 1:
            continue
        milliseconds = row.total_ns / 1_000_000
        if row.experiment == "weighted_greedy":
            detail = f"gap={row.optimality_gap:.0f}"
        elif row.experiment == "exam_timetabling":
            detail = f"nodes={row.nodes_visited}"
        else:
            detail = f"profit={row.objective:.0f}"
        print(
            f"{row.experiment:18} {row.method:19} n={row.size:2} "
            f"{milliseconds:9.3f} ms  {detail}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "experiments" / "benchmark_data" / "task3_experiments.csv",
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
