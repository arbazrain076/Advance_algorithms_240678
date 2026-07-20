"""Weighted graph models and transport-network algorithms for Task 2."""

from .dijkstra import DijkstraEvent, ShortestPathResult, dijkstra
from .graph import Edge, WeightedGraph

__all__ = [
    "DijkstraEvent",
    "Edge",
    "ShortestPathResult",
    "WeightedGraph",
    "dijkstra",
]
