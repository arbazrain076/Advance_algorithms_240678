"""Bellman-Ford shortest paths with negative-cycle identification."""

from collections import deque
from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

from .graph import Vertex, WeightedGraph


@dataclass(frozen=True, slots=True)
class BellmanFordEvent:
    step: int
    pass_number: int
    source: Vertex
    target: Vertex
    old_distance: float
    new_distance: float


@dataclass(frozen=True, slots=True)
class BellmanFordResult:
    source: Vertex
    distances: Mapping[Vertex, float]
    predecessors: Mapping[Vertex, Vertex | None]
    negative_cycle: tuple[Vertex, ...]
    affected_vertices: frozenset[Vertex]
    events: tuple[BellmanFordEvent, ...]
    completed_passes: int

    @property
    def has_negative_cycle(self) -> bool:
        return bool(self.negative_cycle)

    def path_to(self, target: Vertex) -> tuple[Vertex, ...]:
        if target not in self.distances:
            raise KeyError(f"unknown target: {target!r}")
        if target in self.affected_vertices:
            raise ValueError("shortest path is undefined because a negative cycle can reach target")
        if math.isinf(self.distances[target]):
            return ()
        path: list[Vertex] = []
        current: Vertex | None = target
        while current is not None:
            path.append(current)
            current = self.predecessors[current]
        path.reverse()
        return tuple(path)


def bellman_ford(graph: WeightedGraph, source: Vertex) -> BellmanFordResult:
    """Compute shortest paths and identify reachable negative cycles in O(VE)."""

    vertices = graph.vertices
    if source not in vertices:
        raise KeyError(f"unknown source: {source!r}")

    edges = tuple(graph.edges())
    distances = {vertex: math.inf for vertex in vertices}
    predecessors: dict[Vertex, Vertex | None] = {vertex: None for vertex in vertices}
    distances[source] = 0.0
    events: list[BellmanFordEvent] = []
    completed_passes = 0

    for pass_number in range(1, len(vertices)):
        changed = False
        for edge in edges:
            if math.isinf(distances[edge.source]):
                continue
            candidate = distances[edge.source] + edge.weight
            if candidate < distances[edge.target]:
                previous = distances[edge.target]
                distances[edge.target] = candidate
                predecessors[edge.target] = edge.source
                changed = True
                events.append(
                    BellmanFordEvent(
                        step=len(events) + 1,
                        pass_number=pass_number,
                        source=edge.source,
                        target=edge.target,
                        old_distance=previous,
                        new_distance=candidate,
                    )
                )
        completed_passes = pass_number
        if not changed:
            break

    changed_vertices: set[Vertex] = set()
    witness: Vertex | None = None
    for edge in edges:
        if math.isinf(distances[edge.source]):
            continue
        if distances[edge.source] + edge.weight < distances[edge.target]:
            predecessors[edge.target] = edge.source
            changed_vertices.add(edge.target)
            witness = edge.target

    negative_cycle = _reconstruct_cycle(predecessors, witness, len(vertices))
    affected = _reachable_from(graph, changed_vertices)
    for vertex in affected:
        distances[vertex] = -math.inf

    return BellmanFordResult(
        source=source,
        distances=MappingProxyType(distances),
        predecessors=MappingProxyType(predecessors),
        negative_cycle=negative_cycle,
        affected_vertices=frozenset(affected),
        events=tuple(events),
        completed_passes=completed_passes,
    )


def _reconstruct_cycle(
    predecessors: Mapping[Vertex, Vertex | None],
    witness: Vertex | None,
    vertex_count: int,
) -> tuple[Vertex, ...]:
    if witness is None:
        return ()

    current = witness
    for _ in range(vertex_count):
        predecessor = predecessors[current]
        if predecessor is None:
            return ()
        current = predecessor

    reversed_cycle = [current]
    predecessor = predecessors[current]
    while predecessor is not None and predecessor != current:
        reversed_cycle.append(predecessor)
        predecessor = predecessors[predecessor]
    if predecessor is None:
        return ()
    reversed_cycle.append(current)
    reversed_cycle.reverse()
    return tuple(reversed_cycle)


def _reachable_from(graph: WeightedGraph, starts: set[Vertex]) -> set[Vertex]:
    visited = set(starts)
    queue = deque(starts)
    while queue:
        vertex = queue.popleft()
        for neighbour, _ in graph.neighbours(vertex):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return visited
