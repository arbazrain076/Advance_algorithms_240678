"""Algorithmic strategy implementations for Task 3."""

from .exam_timetabling import (
    Exam,
    ExamTimetabler,
    Placement,
    Room,
    TimetableResult,
)
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
    "Exam",
    "ExamTimetabler",
    "GreedyComparison",
    "Job",
    "Placement",
    "Room",
    "ScheduleResult",
    "TimetableResult",
    "compare_greedy",
    "exhaustive_weighted_schedule",
    "find_counterexample",
    "greedy_weighted_schedule",
    "weighted_job_schedule",
]
