"""Dijkstra shortest paths with an auditable execution trace."""

from dataclasses import dataclass
import heapq
import math
from types import MappingProxyType
from typing import Mapping

from .graph import Vertex, WeightedGraph


@dataclass(frozen=True, slots=True)
class DijkstraEvent:
    step: int
    action: str
    vertex: Vertex
    source: Vertex | None
    old_distance: float
    new_distance: float


@dataclass(frozen=True, slots=True)
class ShortestPathResult:
    source: Vertex
    distances: Mapping[Vertex, float]
    predecessors: Mapping[Vertex, Vertex | None]
    events: tuple[DijkstraEvent, ...]

    def path_to(self, target: Vertex) -> tuple[Vertex, ...]:
        """Reconstruct a path, returning an empty tuple when unreachable."""

        if target not in self.distances:
            raise KeyError(f"unknown target: {target!r}")
        if math.isinf(self.distances[target]):
            return ()
        path: list[Vertex] = []
        current: Vertex | None = target
        while current is not None:
            path.append(current)
            current = self.predecessors[current]
        path.reverse()
        return tuple(path)


def dijkstra(graph: WeightedGraph, source: Vertex) -> ShortestPathResult:
    """Compute non-negative single-source shortest paths in O((V + E) log V)."""

    if source not in graph.vertices:
        raise KeyError(f"unknown source: {source!r}")
    if any(edge.weight < 0 for edge in graph.edges()):
        raise ValueError("Dijkstra requires non-negative edge weights")

    distances = {vertex: math.inf for vertex in graph.vertices}
    predecessors: dict[Vertex, Vertex | None] = {vertex: None for vertex in graph.vertices}
    distances[source] = 0.0
    queue: list[tuple[float, int, Vertex]] = [(0.0, 0, source)]
    sequence = 1
    settled: set[Vertex] = set()
    events: list[DijkstraEvent] = []

    while queue:
        distance, _, vertex = heapq.heappop(queue)
        if vertex in settled or distance != distances[vertex]:
            continue
        settled.add(vertex)
        events.append(
            DijkstraEvent(
                step=len(events) + 1,
                action="settle",
                vertex=vertex,
                source=predecessors[vertex],
                old_distance=distance,
                new_distance=distance,
            )
        )

        for neighbour, weight in graph.neighbours(vertex):
            candidate = distance + weight
            if candidate < distances[neighbour]:
                previous = distances[neighbour]
                distances[neighbour] = candidate
                predecessors[neighbour] = vertex
                heapq.heappush(queue, (candidate, sequence, neighbour))
                sequence += 1
                events.append(
                    DijkstraEvent(
                        step=len(events) + 1,
                        action="relax",
                        vertex=neighbour,
                        source=vertex,
                        old_distance=previous,
                        new_distance=candidate,
                    )
                )

    return ShortestPathResult(
        source=source,
        distances=MappingProxyType(distances),
        predecessors=MappingProxyType(predecessors),
        events=tuple(events),
    )
