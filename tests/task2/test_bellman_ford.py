import math
import unittest

from task2_graphs import WeightedGraph, bellman_ford


class BellmanFordTests(unittest.TestCase):
    def test_negative_edges_without_cycle_produce_shortest_paths(self) -> None:
        graph = WeightedGraph()
        for source, target, weight in [
            ("S", "A", 4),
            ("S", "B", 5),
            ("A", "C", -2),
            ("B", "C", 3),
            ("C", "D", 2),
        ]:
            graph.add_edge(source, target, weight)

        result = bellman_ford(graph, "S")

        self.assertFalse(result.has_negative_cycle)
        self.assertEqual(result.distances["D"], 4)
        self.assertEqual(result.path_to("D"), ("S", "A", "C", "D"))
        self.assertTrue(all(event.new_distance < event.old_distance for event in result.events))

    def test_reachable_negative_cycle_is_returned_and_propagated(self) -> None:
        graph = WeightedGraph()
        for source, target, weight in [
            ("S", "A", 1),
            ("A", "B", 1),
            ("B", "C", -4),
            ("C", "A", 1),
            ("C", "D", 2),
        ]:
            graph.add_edge(source, target, weight)

        result = bellman_ford(graph, "S")

        self.assertTrue(result.has_negative_cycle)
        self.assertEqual(result.negative_cycle[0], result.negative_cycle[-1])
        cycle_edges = set(zip(result.negative_cycle, result.negative_cycle[1:]))
        self.assertEqual(cycle_edges, {("A", "B"), ("B", "C"), ("C", "A")})
        self.assertEqual(result.affected_vertices, frozenset({"A", "B", "C", "D"}))
        self.assertEqual(result.distances["D"], -math.inf)
        with self.assertRaisesRegex(ValueError, "negative cycle"):
            result.path_to("D")

    def test_unreachable_negative_cycle_does_not_affect_source_paths(self) -> None:
        graph = WeightedGraph()
        graph.add_edge("S", "T", 3)
        graph.add_edge("X", "Y", -2)
        graph.add_edge("Y", "X", -2)

        result = bellman_ford(graph, "S")

        self.assertFalse(result.has_negative_cycle)
        self.assertTrue(math.isinf(result.distances["X"]))
        self.assertEqual(result.path_to("X"), ())

    def test_early_exit_and_unknown_vertices(self) -> None:
        graph = WeightedGraph()
        graph.add_edge("A", "B", 1)
        graph.add_vertex("C")
        result = bellman_ford(graph, "A")

        self.assertLess(result.completed_passes, len(graph) - 1 + 1)
        with self.assertRaises(KeyError):
            result.path_to("missing")
        with self.assertRaises(KeyError):
            bellman_ford(graph, "missing")


if __name__ == "__main__":
    unittest.main()
