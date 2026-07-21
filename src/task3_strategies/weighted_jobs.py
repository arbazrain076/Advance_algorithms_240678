"""Bottom-up dynamic programming for weighted job scheduling."""

from bisect import bisect_right
from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Job:
    identifier: str
    start: float
    end: float
    profit: float

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("job identifier must not be empty")
        if not all(math.isfinite(value) for value in (self.start, self.end, self.profit)):
            raise ValueError("job values must be finite")
        if self.end <= self.start:
            raise ValueError("job end must be later than its start")
        if self.profit < 0:
            raise ValueError("job profit must not be negative")


@dataclass(frozen=True, slots=True)
class DPState:
    jobs_considered: int
    job_identifier: str
    compatible_prefix: int
    include_profit: float
    exclude_profit: float
    chosen_profit: float
    decision: str


@dataclass(frozen=True, slots=True)
class ScheduleResult:
    maximum_profit: float
    selected_jobs: tuple[Job, ...]
    states: tuple[DPState, ...]


def weighted_job_schedule(jobs: Iterable[Job]) -> ScheduleResult:
    """Find a maximum-profit non-overlapping schedule in O(n log n) time."""

    ordered = _validate_and_order(jobs)
    if not ordered:
        return ScheduleResult(0.0, (), ())

    end_times = [job.end for job in ordered]
    compatible = [
        bisect_right(end_times, job.start, hi=index) - 1
        for index, job in enumerate(ordered)
    ]

    # optimum[i] represents the first i jobs; optimum[0] is the empty prefix.
    optimum = [0.0] * (len(ordered) + 1)
    take = [False] * len(ordered)
    states: list[DPState] = []

    for index, job in enumerate(ordered):
        prefix = compatible[index] + 1
        include_profit = job.profit + optimum[prefix]
        exclude_profit = optimum[index]
        # On ties, exclusion gives a stable solution with fewer unnecessary jobs.
        take[index] = include_profit > exclude_profit
        optimum[index + 1] = max(include_profit, exclude_profit)
        states.append(
            DPState(
                jobs_considered=index + 1,
                job_identifier=job.identifier,
                compatible_prefix=prefix,
                include_profit=include_profit,
                exclude_profit=exclude_profit,
                chosen_profit=optimum[index + 1],
                decision="include" if take[index] else "exclude",
            )
        )

    selected: list[Job] = []
    index = len(ordered) - 1
    while index >= 0:
        if take[index]:
            selected.append(ordered[index])
            index = compatible[index]
        else:
            index -= 1
    selected.reverse()
    return ScheduleResult(optimum[-1], tuple(selected), tuple(states))


def exhaustive_weighted_schedule(jobs: Iterable[Job]) -> ScheduleResult:
    """Exact O(2^n) reference solver for validating small experiments."""

    ordered = _validate_and_order(jobs)
    best_profit = 0.0
    best_selection: tuple[Job, ...] = ()

    for mask in range(1 << len(ordered)):
        selection = tuple(
            ordered[index] for index in range(len(ordered)) if mask & (1 << index)
        )
        if _is_compatible(selection):
            profit = sum(job.profit for job in selection)
            if profit > best_profit:
                best_profit = profit
                best_selection = selection
    return ScheduleResult(best_profit, best_selection, ())


def _validate_and_order(jobs: Iterable[Job]) -> list[Job]:
    ordered = sorted(jobs, key=lambda job: (job.end, job.start, job.identifier))
    identifiers = [job.identifier for job in ordered]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("job identifiers must be unique")
    return ordered


def _is_compatible(jobs: tuple[Job, ...]) -> bool:
    return all(left.end <= right.start for left, right in zip(jobs, jobs[1:]))
