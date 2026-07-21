"""Greedy weighted-interval heuristics and automatic counterexample search."""

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Literal

from .weighted_jobs import Job, ScheduleResult, weighted_job_schedule


GreedyRule = Literal["earliest_finish", "shortest_duration", "highest_weight"]


@dataclass(frozen=True, slots=True)
class GreedyComparison:
    rule: GreedyRule
    greedy: ScheduleResult
    optimal: ScheduleResult

    @property
    def optimality_gap(self) -> float:
        return self.optimal.maximum_profit - self.greedy.maximum_profit

    @property
    def is_optimal(self) -> bool:
        return self.optimality_gap == 0


def greedy_weighted_schedule(
    jobs: Iterable[Job],
    rule: GreedyRule = "earliest_finish",
) -> ScheduleResult:
    """Construct a feasible schedule using one locally ranked choice rule."""

    jobs = list(jobs)
    _require_unique_identifiers(jobs)
    key_functions: dict[GreedyRule, Callable[[Job], tuple[float, ...]]] = {
        "earliest_finish": lambda job: (job.end, job.start, -job.profit),
        "shortest_duration": lambda job: (
            job.end - job.start,
            job.end,
            -job.profit,
        ),
        "highest_weight": lambda job: (-job.profit, job.end, job.start),
    }
    try:
        key = key_functions[rule]
    except KeyError as error:
        raise ValueError(f"unknown greedy rule: {rule}") from error

    selected: list[Job] = []
    for candidate in sorted(jobs, key=key):
        if all(
            candidate.end <= chosen.start or chosen.end <= candidate.start
            for chosen in selected
        ):
            selected.append(candidate)
    selected.sort(key=lambda job: (job.end, job.start, job.identifier))
    return ScheduleResult(
        maximum_profit=sum(job.profit for job in selected),
        selected_jobs=tuple(selected),
        states=(),
    )


def compare_greedy(
    jobs: Iterable[Job],
    rule: GreedyRule = "earliest_finish",
) -> GreedyComparison:
    jobs = list(jobs)
    return GreedyComparison(
        rule=rule,
        greedy=greedy_weighted_schedule(jobs, rule),
        optimal=weighted_job_schedule(jobs),
    )


def find_counterexample(rule: GreedyRule) -> GreedyComparison:
    """Exhaustively find a small instance on which ``rule`` is suboptimal."""

    # This finite search is intentionally small enough to replay during an oral defence.
    templates = [
        (start, end, profit)
        for start in range(4)
        for end in range(start + 1, 6)
        for profit in (2, 4, 7)
    ]
    for size in (2, 3, 4):
        for candidate_templates in combinations(templates, size):
            jobs = [
                Job(f"J{index + 1}", start, end, profit)
                for index, (start, end, profit) in enumerate(candidate_templates)
            ]
            comparison = compare_greedy(jobs, rule)
            if not comparison.is_optimal:
                return comparison
    raise RuntimeError(f"no counterexample found for {rule}")


def _require_unique_identifiers(jobs: list[Job]) -> None:
    identifiers = [job.identifier for job in jobs]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("job identifiers must be unique")
