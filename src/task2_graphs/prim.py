"""Prim minimum spanning forest with edge-selection trace events."""

from dataclasses import dataclass
import heapq

from .graph import Edge, Vertex, WeightedGraph


@dataclass(frozen=True, slots=True)
class PrimEvent:
    step: int
    action: str
    vertex: Vertex
    source: Vertex | None
    weight: float
    running_weight: float


@dataclass(frozen=True, slots=True)
class SpanningForestResult:
    edges: tuple[Edge, ...]
    total_weight: float
    components: tuple[frozenset[Vertex], ...]
    events: tuple[PrimEvent, ...]

    @property
    def is_spanning_tree(self) -> bool:
        """Return whether the result is one connected spanning tree."""

        return len(self.components) <= 1


def prim_minimum_spanning_forest(graph: WeightedGraph) -> SpanningForestResult:
    """Return a minimum spanning tree per connected component.

    Complexity is O((V + E) log V) with the adjacency list and binary heap.
    """

    if graph.directed:
        raise ValueError("Prim requires an undirected graph")

    visited: set[Vertex] = set()
    selected_edges: list[Edge] = []
    components: list[frozenset[Vertex]] = []
    events: list[PrimEvent] = []
    total_weight = 0.0
    sequence = 0

    for start in graph.vertices:
        if start in visited:
            continue

        component: set[Vertex] = set()
        queue: list[tuple[float, int, Vertex | None, Vertex]] = [
            (0.0, sequence, None, start)
        ]
        sequence += 1

        while queue:
            weight, _, source, vertex = heapq.heappop(queue)
            if vertex in visited:
                continue
            visited.add(vertex)
            component.add(vertex)

            if source is None:
                action = "start_component"
            else:
                selected_edges.append(Edge(source, vertex, weight))
                total_weight += weight
                action = "select_edge"

            events.append(
                PrimEvent(
                    step=len(events) + 1,
                    action=action,
                    vertex=vertex,
                    source=source,
                    weight=weight,
                    running_weight=total_weight,
                )
            )

            for neighbour, edge_weight in graph.neighbours(vertex):
                if neighbour not in visited:
                    heapq.heappush(
                        queue,
                        (edge_weight, sequence, vertex, neighbour),
                    )
                    sequence += 1

        components.append(frozenset(component))

    return SpanningForestResult(
        edges=tuple(selected_edges),
        total_weight=total_weight,
        components=tuple(components),
        events=tuple(events),
    )
