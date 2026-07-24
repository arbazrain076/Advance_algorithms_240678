"""Sequential and process-based parallel merge sort implementations.

The parallel implementation uses spawned worker processes rather than threads,
so CPU-bound sorting work can execute outside Python's global interpreter lock.
Sorted runs are merged in parallel rounds; the final round naturally contains
one merge and therefore remains the serial span of the algorithm.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import Iterable, Sequence, TypeVar


T = TypeVar("T")
SUPPORTED_WORKER_COUNTS = (1, 2, 4, 8)
DEFAULT_THRESHOLD = 50_000


def _merge_into(
    source: Sequence[T],
    destination: list[T | None],
    left: int,
    middle: int,
    right: int,
) -> None:
    first = left
    second = middle
    output = left

    while first < middle and second < right:
        if source[first] <= source[second]:
            destination[output] = source[first]
            first += 1
        else:
            destination[output] = source[second]
            second += 1
        output += 1

    while first < middle:
        destination[output] = source[first]
        first += 1
        output += 1

    while second < right:
        destination[output] = source[second]
        second += 1
        output += 1


def sequential_merge_sort(values: Iterable[T]) -> list[T]:
    """Return a sorted copy of *values* using bottom-up merge sort."""

    if values is None:
        raise TypeError("values must not be None")

    source = list(values)
    length = len(source)
    if length < 2:
        return source

    destination: list[T | None] = [None] * length
    width = 1
    while width < length:
        for left in range(0, length, 2 * width):
            middle = min(left + width, length)
            right = min(left + 2 * width, length)
            _merge_into(source, destination, left, middle, right)
        source, destination = destination, source
        width *= 2

    return list(source)


def _merge_pair(pair: tuple[list[T], list[T]]) -> list[T]:
    left, right = pair
    merged: list[T] = []
    merged_extend = merged.extend
    first = 0
    second = 0

    while first < len(left) and second < len(right):
        if left[first] <= right[second]:
            merged.append(left[first])
            first += 1
        else:
            merged.append(right[second])
            second += 1

    if first < len(left):
        merged_extend(left[first:])
    if second < len(right):
        merged_extend(right[second:])
    return merged


def _partition(values: list[T], partitions: int) -> list[list[T]]:
    quotient, remainder = divmod(len(values), partitions)
    chunks: list[list[T]] = []
    start = 0
    for index in range(partitions):
        stop = start + quotient + (1 if index < remainder else 0)
        chunks.append(values[start:stop])
        start = stop
    return chunks


def _validate_worker_count(worker_count: int) -> None:
    if isinstance(worker_count, bool) or worker_count not in SUPPORTED_WORKER_COUNTS:
        supported = ", ".join(str(value) for value in SUPPORTED_WORKER_COUNTS)
        raise ValueError(f"worker_count must be one of: {supported}")


def _validate_threshold(threshold: int) -> None:
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError("threshold must be a positive integer")


def parallel_merge_sort(
    values: Iterable[T],
    worker_count: int = 4,
    threshold: int = DEFAULT_THRESHOLD,
) -> list[T]:
    """Return a process-based parallel merge-sort result.

    Inputs at or below *threshold* use the sequential implementation to avoid
    process-startup and serialization overhead. Larger inputs are divided into
    contiguous runs, sorted by a spawned process pool, and merged in parallel
    rounds. ``spawn`` is selected explicitly for Windows-safe behaviour.
    """

    if values is None:
        raise TypeError("values must not be None")
    _validate_worker_count(worker_count)
    _validate_threshold(threshold)

    items = list(values)
    if len(items) < 2 or len(items) <= threshold:
        return sequential_merge_sort(items)

    partition_count = min(len(items), max(2, worker_count))
    chunks = _partition(items, partition_count)
    context = get_context("spawn")

    with ProcessPoolExecutor(
        max_workers=worker_count,
        mp_context=context,
    ) as executor:
        runs = list(executor.map(sequential_merge_sort, chunks, chunksize=1))
        while len(runs) > 1:
            pairs = [
                (runs[index], runs[index + 1])
                for index in range(0, len(runs) - 1, 2)
            ]
            merged = list(executor.map(_merge_pair, pairs, chunksize=1))
            if len(runs) % 2:
                merged.append(runs[-1])
            runs = merged

    return runs[0]


def is_sorted(values: Sequence[T]) -> bool:
    """Return whether values are in non-decreasing order."""

    if values is None:
        raise TypeError("values must not be None")
    return all(values[index - 1] <= values[index] for index in range(1, len(values)))
