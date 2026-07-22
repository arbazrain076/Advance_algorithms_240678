"""Exact branch-and-bound reference for small bin-packing instances."""

import math
from typing import Iterable

from .bin_packing import (
    BinCapacity,
    Item,
    PackingResult,
    best_fit_decreasing,
    bin_loads,
)


def exact_branch_and_bound(
    items: Iterable[Item],
    capacity: BinCapacity,
) -> PackingResult:
    """Return an optimal packing; intended only for small evaluation instances."""

    items = list(items)
    incumbent = best_fit_decreasing(items, capacity)
    if not items:
        return PackingResult((), "exact_branch_and_bound", evaluated_moves=1)

    ordered = sorted(
        items,
        key=lambda item: (
            -max(
                demand / limit
                for demand, limit in zip(item.demand, capacity.dimensions)
            ),
            -sum(item.demand),
            item.identifier,
        ),
    )
    lower_bound = max(
        math.ceil(
            sum(item.demand[dimension] for item in ordered)
            / capacity.dimensions[dimension]
            - 1e-12
        )
        for dimension in range(3)
    )
    best_bins = [list(group) for group in incumbent.bins]
    bins: list[list[Item]] = []
    loads: list[list[float]] = []
    nodes = 0

    def search(position: int) -> None:
        nonlocal best_bins, nodes
        nodes += 1
        if len(best_bins) == lower_bound:
            return
        if position == len(ordered):
            best_bins = [list(group) for group in bins]
            return
        if len(bins) >= len(best_bins):
            return

        item = ordered[position]
        seen_loads: set[tuple[float, float, float]] = set()
        for index, load in enumerate(loads):
            load_key = tuple(load)
            if load_key in seen_loads:
                continue
            seen_loads.add(load_key)
            if _fits(load, item, capacity):
                bins[index].append(item)
                for dimension, demand in enumerate(item.demand):
                    load[dimension] += demand
                search(position + 1)
                for dimension, demand in enumerate(item.demand):
                    load[dimension] -= demand
                bins[index].pop()

        # A new bin can improve the incumbent only if the new count stays below it.
        if len(bins) + 1 < len(best_bins):
            bins.append([item])
            loads.append(list(item.demand))
            search(position + 1)
            loads.pop()
            bins.pop()

    search(0)
    return PackingResult(
        bins=tuple(tuple(group) for group in best_bins),
        method="exact_branch_and_bound",
        evaluated_moves=nodes,
    )


def resource_lower_bound(
    items: Iterable[Item],
    capacity: BinCapacity,
) -> int:
    """Return the maximum dimension-wise volume lower bound."""

    items = list(items)
    if not items:
        return 0
    return max(
        math.ceil(
            sum(item.demand[dimension] for item in items)
            / capacity.dimensions[dimension]
            - 1e-12
        )
        for dimension in range(3)
    )


def _fits(
    load: list[float],
    item: Item,
    capacity: BinCapacity,
) -> bool:
    return all(
        used + demand <= limit + 1e-9
        for used, demand, limit in zip(load, item.demand, capacity.dimensions)
    )
