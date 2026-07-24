from __future__ import annotations

import multiprocessing
import random
import time

import pytest

from task5_concurrency import (
    SUPPORTED_WORKER_COUNTS,
    is_sorted,
    parallel_merge_sort,
    sequential_merge_sort,
)


@pytest.mark.parametrize(
    "values",
    [
        [],
        [42],
        [5, 5, 5, 5],
        [-5, 3, -1, 0, -5, 9],
        list(range(100)),
        list(range(100, -1, -1)),
    ],
)
def test_sequential_merge_sort_matches_sorted(values: list[int]) -> None:
    original = values.copy()
    actual = sequential_merge_sort(values)
    assert actual == sorted(values)
    assert is_sorted(actual)
    assert values == original


@pytest.mark.parametrize("workers", SUPPORTED_WORKER_COUNTS)
def test_parallel_edge_cases(workers: int) -> None:
    assert parallel_merge_sort([], workers) == []
    assert parallel_merge_sort([42], workers) == [42]


@pytest.mark.parametrize("workers", SUPPORTED_WORKER_COUNTS)
def test_parallel_workers_match_sorted(workers: int) -> None:
    generator = random.Random(240_678 + workers)
    values = [generator.randint(-1_000_000, 1_000_000) for _ in range(2_047)]
    expected = sorted(values)

    actual = parallel_merge_sort(values, worker_count=workers, threshold=128)

    assert actual == expected
    assert actual == sequential_merge_sort(values)
    assert is_sorted(actual)


def test_large_random_list_and_worker_cleanup() -> None:
    generator = random.Random(240_678)
    values = [generator.randint(-(1 << 31), (1 << 31) - 1) for _ in range(20_003)]
    before = {process.pid for process in multiprocessing.active_children()}

    actual = parallel_merge_sort(values, worker_count=4, threshold=1_000)

    assert actual == sorted(values)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        active = {
            process.pid
            for process in multiprocessing.active_children()
            if process.pid not in before
        }
        if not active:
            break
        time.sleep(0.05)
    assert not active


@pytest.mark.parametrize("workers", [0, 3, 16, True])
def test_worker_count_validation(workers: int) -> None:
    with pytest.raises(ValueError, match="worker_count"):
        parallel_merge_sort([2, 1], worker_count=workers)


@pytest.mark.parametrize("threshold", [0, -1, True, 1.5])
def test_threshold_validation(threshold: int) -> None:
    with pytest.raises(ValueError, match="threshold"):
        parallel_merge_sort([2, 1], threshold=threshold)


def test_none_is_rejected() -> None:
    with pytest.raises(TypeError):
        sequential_merge_sort(None)
    with pytest.raises(TypeError):
        parallel_merge_sort(None)
    with pytest.raises(TypeError):
        is_sorted(None)
