"""Sequential and process-based parallel merge sort for Task 5."""

from .parallel_merge_sort import (
    SUPPORTED_WORKER_COUNTS,
    is_sorted,
    parallel_merge_sort,
    sequential_merge_sort,
)

__all__ = [
    "SUPPORTED_WORKER_COUNTS",
    "is_sorted",
    "parallel_merge_sort",
    "sequential_merge_sort",
]
