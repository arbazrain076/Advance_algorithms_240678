"""Problem model and greedy construction for multi-dimensional bin packing."""

from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Item:
    identifier: str
    cpu: float
    ram: float
    bandwidth: float

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("item identifier must not be empty")
        values = (self.cpu, self.ram, self.bandwidth)
        if not all(math.isfinite(value) and value > 0 for value in values):
            raise ValueError("item requirements must be finite and positive")

    @property
    def demand(self) -> tuple[float, float, float]:
        return self.cpu, self.ram, self.bandwidth


@dataclass(frozen=True, slots=True)
class BinCapacity:
    cpu: float
    ram: float
    bandwidth: float

    def __post_init__(self) -> None:
        values = (self.cpu, self.ram, self.bandwidth)
        if not all(math.isfinite(value) and value > 0 for value in values):
            raise ValueError("bin capacities must be finite and positive")

    @property
    def dimensions(self) -> tuple[float, float, float]:
        return self.cpu, self.ram, self.bandwidth


@dataclass(frozen=True, slots=True)
class PackingResult:
    bins: tuple[tuple[Item, ...], ...]
    method: str
    evaluated_moves: int = 0
    accepted_moves: int = 0

    @property
    def bin_count(self) -> int:
        return len(self.bins)


def best_fit_decreasing(
    items: Iterable[Item],
    capacity: BinCapacity,
) -> PackingResult:
    """Pack by dominant normalised demand and tightest feasible residual."""

    items = _validate_items(items, capacity)
    ordered = sorted(
        items,
        key=lambda item: (
            -_dominant_share(item, capacity),
            -sum(
                demand / limit
                for demand, limit in zip(item.demand, capacity.dimensions)
            ),
            item.identifier,
        ),
    )
    bins: list[list[Item]] = []
    loads: list[list[float]] = []

    for item in ordered:
        feasible_bins = [
            index
            for index, load in enumerate(loads)
            if _fits(load, item, capacity)
        ]
        if feasible_bins:
            chosen = min(
                feasible_bins,
                key=lambda index: _residual_score(loads[index], item, capacity),
            )
        else:
            bins.append([])
            loads.append([0.0, 0.0, 0.0])
            chosen = len(bins) - 1
        bins[chosen].append(item)
        for dimension, demand in enumerate(item.demand):
            loads[chosen][dimension] += demand

    return PackingResult(
        bins=tuple(tuple(bin_items) for bin_items in bins),
        method="best_fit_decreasing",
    )


def validate_packing(
    result: PackingResult,
    items: Iterable[Item],
    capacity: BinCapacity,
) -> bool:
    expected = list(items)
    packed = [item for bin_items in result.bins for item in bin_items]
    if len(packed) != len(expected):
        return False
    if {item.identifier for item in packed} != {item.identifier for item in expected}:
        return False
    if len({item.identifier for item in packed}) != len(packed):
        return False
    return all(
        all(
            sum(item.demand[dimension] for item in bin_items)
            <= capacity.dimensions[dimension] + 1e-9
            for dimension in range(3)
        )
        for bin_items in result.bins
    )


def bin_loads(
    bin_items: Iterable[Item],
) -> tuple[float, float, float]:
    items = tuple(bin_items)
    return tuple(
        sum(item.demand[dimension] for item in items)
        for dimension in range(3)
    )


def _validate_items(items: Iterable[Item], capacity: BinCapacity) -> list[Item]:
    items = list(items)
    identifiers = [item.identifier for item in items]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("item identifiers must be unique")
    for item in items:
        if any(
            demand > limit
            for demand, limit in zip(item.demand, capacity.dimensions)
        ):
            raise ValueError(f"item {item.identifier!r} cannot fit in an empty bin")
    return items


def _dominant_share(item: Item, capacity: BinCapacity) -> float:
    return max(
        demand / limit
        for demand, limit in zip(item.demand, capacity.dimensions)
    )


def _fits(load: list[float], item: Item, capacity: BinCapacity) -> bool:
    return all(
        used + demand <= limit + 1e-9
        for used, demand, limit in zip(load, item.demand, capacity.dimensions)
    )


def _residual_score(
    load: list[float],
    item: Item,
    capacity: BinCapacity,
) -> tuple[float, float]:
    residuals = [
        (limit - used - demand) / limit
        for used, demand, limit in zip(load, item.demand, capacity.dimensions)
    ]
    # Squared residual rewards tight multi-resource fits; max residual breaks ties.
    return sum(residual * residual for residual in residuals), max(residuals)
