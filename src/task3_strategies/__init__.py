"""Algorithmic strategy implementations for Task 3."""

from .weighted_jobs import (
    Job,
    ScheduleResult,
    exhaustive_weighted_schedule,
    weighted_job_schedule,
)
from .weighted_greedy import (
    GreedyComparison,
    compare_greedy,
    find_counterexample,
    greedy_weighted_schedule,
)

__all__ = [
    "GreedyComparison",
    "Job",
    "ScheduleResult",
    "compare_greedy",
    "exhaustive_weighted_schedule",
    "find_counterexample",
    "greedy_weighted_schedule",
    "weighted_job_schedule",
]
