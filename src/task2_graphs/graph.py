"""Adjacency-list representation of a weighted transport network."""

from dataclasses import dataclass
import math
from typing import Hashable, Iterator


Vertex = Hashable


@dataclass(frozen=True, slots=True)
class Edge:
    source: Vertex
    target: Vertex
    weight: float


class WeightedGraph:
    """Weighted graph with directed edges by default."""

    def __init__(self, directed: bool = True) -> None:
        self.directed = directed
        self._adjacency: dict[Vertex, dict[Vertex, float]] = {}
        self._edge_count = 0

    def __len__(self) -> int:
        return len(self._adjacency)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    @property
    def vertices(self) -> tuple[Vertex, ...]:
        return tuple(self._adjacency)

    def add_vertex(self, vertex: Vertex) -> bool:
        """Add a vertex and return whether it was new."""

        self._require_hashable(vertex)
        if vertex in self._adjacency:
            return False
        self._adjacency[vertex] = {}
        return True

    def add_edge(self, source: Vertex, target: Vertex, weight: float) -> float | None:
        """Add or update an edge and return its previous weight if present."""

        self._validate_weight(weight)
        self.add_vertex(source)
        self.add_vertex(target)
        previous = self._adjacency[source].get(target)
        self._adjacency[source][target] = float(weight)
        if not self.directed:
            self._adjacency[target][source] = float(weight)
        if previous is None:
            self._edge_count += 1
        return previous

    def remove_edge(self, source: Vertex, target: Vertex) -> float | None:
        if source not in self._adjacency:
            return None
        previous = self._adjacency[source].pop(target, None)
        if previous is not None:
            if not self.directed:
                self._adjacency[target].pop(source, None)
            self._edge_count -= 1
        return previous

    def weight(self, source: Vertex, target: Vertex) -> float | None:
        return self._adjacency.get(source, {}).get(target)

    def neighbours(self, vertex: Vertex) -> tuple[tuple[Vertex, float], ...]:
        if vertex not in self._adjacency:
            raise KeyError(f"unknown vertex: {vertex!r}")
        return tuple(self._adjacency[vertex].items())

    def edges(self) -> Iterator[Edge]:
        seen: set[frozenset[Vertex]] = set()
        for source, neighbours in self._adjacency.items():
            for target, weight in neighbours.items():
                if not self.directed:
                    identity = frozenset((source, target))
                    if identity in seen:
                        continue
                    seen.add(identity)
                yield Edge(source, target, weight)

    def as_undirected(self, combine: str = "minimum") -> "WeightedGraph":
        """Project directed edges into an undirected graph.

        When reciprocal arcs differ, ``minimum`` keeps the cheaper connection.
        """

        if combine != "minimum":
            raise ValueError("only the 'minimum' combine policy is supported")
        result = WeightedGraph(directed=False)
        for vertex in self.vertices:
            result.add_vertex(vertex)
        for edge in self.edges():
            current = result.weight(edge.source, edge.target)
            if current is None or edge.weight < current:
                result.add_edge(edge.source, edge.target, edge.weight)
        return result

    @staticmethod
    def _validate_weight(weight: float) -> None:
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise TypeError("edge weight must be numeric")
        if not math.isfinite(weight):
            raise ValueError("edge weight must be finite")

    @staticmethod
    def _require_hashable(vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as error:
            raise TypeError("vertex must be hashable") from error
