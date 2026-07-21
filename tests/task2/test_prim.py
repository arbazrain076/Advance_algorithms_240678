import unittest

from task2_graphs import WeightedGraph, prim_minimum_spanning_forest


class PrimTests(unittest.TestCase):
    def test_connected_graph_returns_minimum_spanning_tree(self) -> None:
        graph = WeightedGraph(directed=False)
        for source, target, weight in [
            ("A", "B", 4),
            ("A", "C", 2),
            ("B", "C", 1),
            ("B", "D", 5),
            ("C", "D", 8),
            ("C", "E", 10),
            ("D", "E", 2),
        ]:
            graph.add_edge(source, target, weight)

        result = prim_minimum_spanning_forest(graph)

        self.assertTrue(result.is_spanning_tree)
        self.assertEqual(len(result.edges), len(graph) - 1)
        self.assertEqual(result.total_weight, 10)
        self.assertEqual(
            {frozenset((edge.source, edge.target)) for edge in result.edges},
            {
                frozenset(("A", "C")),
                frozenset(("B", "C")),
                frozenset(("B", "D")),
                frozenset(("D", "E")),
            },
        )

    def test_disconnected_graph_returns_minimum_spanning_forest(self) -> None:
        graph = WeightedGraph(directed=False)
        graph.add_edge("A", "B", 2)
        graph.add_edge("C", "D", -3)
        graph.add_vertex("E")

        result = prim_minimum_spanning_forest(graph)

        self.assertFalse(result.is_spanning_tree)
        self.assertEqual(len(result.components), 3)
        self.assertEqual(len(result.edges), 2)
        self.assertEqual(result.total_weight, -1)
        starts = [event for event in result.events if event.action == "start_component"]
        self.assertEqual(len(starts), 3)

    def test_trace_records_running_weight(self) -> None:
        graph = WeightedGraph(directed=False)
        graph.add_edge("A", "B", 2)
        graph.add_edge("B", "C", 3)

        result = prim_minimum_spanning_forest(graph)

        self.assertEqual([event.running_weight for event in result.events], [0, 2, 5])
        self.assertEqual(
            [event.step for event in result.events],
            list(range(1, len(result.events) + 1)),
        )

    def test_directed_graph_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "undirected"):
            prim_minimum_spanning_forest(WeightedGraph(directed=True))

    def test_empty_graph_has_empty_forest(self) -> None:
        result = prim_minimum_spanning_forest(WeightedGraph(directed=False))
        self.assertTrue(result.is_spanning_tree)
        self.assertEqual(result.edges, ())
        self.assertEqual(result.components, ())
        self.assertEqual(result.total_weight, 0)


if __name__ == "__main__":
    unittest.main()
