"""Relocate-and-swap local search for multi-dimensional bin packing."""

from itertools import combinations
from typing import Iterable

from .bin_packing import (
    BinCapacity,
    Item,
    PackingResult,
    best_fit_decreasing,
    bin_loads,
    validate_packing,
)


def local_search(
    items: Iterable[Item],
    capacity: BinCapacity,
    initial: PackingResult | None = None,
    max_passes: int = 100,
) -> PackingResult:
    """Improve a feasible packing using bin-emptying relocations and swaps."""

    items = list(items)
    if max_passes <= 0:
        raise ValueError("max_passes must be positive")
    initial = initial or best_fit_decreasing(items, capacity)
    if not validate_packing(initial, items, capacity):
        raise ValueError("initial packing is infeasible or does not match the items")

    bins = [list(group) for group in initial.bins]
    counters = {"evaluated": 0, "accepted": 0}

    for _ in range(max_passes):
        improved = False
        # Empty lightly populated bins first; their items are easier to relocate.
        target_order = sorted(
            range(len(bins)),
            key=lambda index: (
                len(bins[index]),
                sum(
                    load / limit
                    for load, limit in zip(
                        bin_loads(bins[index]),
                        capacity.dimensions,
                    )
                ),
            ),
        )
        for target in target_order:
            relocated = _relocate_entire_bin(bins, target, capacity, counters)
            if relocated is not None:
                bins = relocated
                counters["accepted"] += 1
                improved = True
                break
        if improved:
            continue

        if _first_improving_swap(bins, capacity, counters):
            counters["accepted"] += 1
            continue
        break

    return PackingResult(
        bins=tuple(tuple(group) for group in bins),
        method="relocate_swap_local_search",
        evaluated_moves=counters["evaluated"],
        accepted_moves=counters["accepted"],
    )


def _relocate_entire_bin(
    bins: list[list[Item]],
    target: int,
    capacity: BinCapacity,
    counters: dict[str, int],
) -> list[list[Item]] | None:
    if len(bins) <= 1:
        return None
    candidate = [list(group) for index, group in enumerate(bins) if index != target]
    moving = sorted(
        bins[target],
        key=lambda item: -max(
            demand / limit
            for demand, limit in zip(item.demand, capacity.dimensions)
        ),
    )

    def place(position: int) -> bool:
        if position == len(moving):
            return True
        item = moving[position]
        seen_loads: set[tuple[float, float, float]] = set()
        for group in candidate:
            load = bin_loads(group)
            if load in seen_loads:
                continue
            seen_loads.add(load)
            counters["evaluated"] += 1
            if _fits(load, item, capacity):
                group.append(item)
                if place(position + 1):
                    return True
                group.pop()
        return False

    return candidate if place(0) else None


def _first_improving_swap(
    bins: list[list[Item]],
    capacity: BinCapacity,
    counters: dict[str, int],
) -> bool:
    current_score = _imbalance(bins, capacity)
    for left_index, right_index in combinations(range(len(bins)), 2):
        left = bins[left_index]
        right = bins[right_index]
        for left_item in tuple(left):
            for right_item in tuple(right):
                counters["evaluated"] += 1
                left_position = left.index(left_item)
                right_position = right.index(right_item)
                left[left_position], right[right_position] = right_item, left_item
                feasible = _bin_fits(left, capacity) and _bin_fits(right, capacity)
                if feasible and _imbalance(bins, capacity) + 1e-12 < current_score:
                    return True
                left[left_position], right[right_position] = left_item, right_item
    return False


def _imbalance(bins: list[list[Item]], capacity: BinCapacity) -> float:
    if not bins:
        return 0.0
    score = 0.0
    for group in bins:
        shares = [
            load / limit
            for load, limit in zip(bin_loads(group), capacity.dimensions)
        ]
        mean = sum(shares) / len(shares)
        score += sum((share - mean) ** 2 for share in shares)
    return score


def _fits(
    load: tuple[float, float, float],
    item: Item,
    capacity: BinCapacity,
) -> bool:
    return all(
        used + demand <= limit + 1e-9
        for used, demand, limit in zip(load, item.demand, capacity.dimensions)
    )


def _bin_fits(group: list[Item], capacity: BinCapacity) -> bool:
    return all(
        load <= limit + 1e-9
        for load, limit in zip(bin_loads(group), capacity.dimensions)
    )
