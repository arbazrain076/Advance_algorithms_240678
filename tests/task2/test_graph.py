import unittest

from task2_graphs import Edge, WeightedGraph


class WeightedGraphTests(unittest.TestCase):
    def test_directed_edges_are_independent_and_update_in_place(self) -> None:
        graph = WeightedGraph()
        self.assertIsNone(graph.add_edge("A", "B", 4))
        self.assertEqual(graph.add_edge("A", "B", 2), 4)

        self.assertEqual(graph.weight("A", "B"), 2)
        self.assertIsNone(graph.weight("B", "A"))
        self.assertEqual(graph.edge_count, 1)
        self.assertEqual(set(graph.edges()), {Edge("A", "B", 2)})

    def test_undirected_edge_is_stored_both_ways_but_counted_once(self) -> None:
        graph = WeightedGraph(directed=False)
        graph.add_edge("A", "B", 3)

        self.assertEqual(graph.weight("A", "B"), 3)
        self.assertEqual(graph.weight("B", "A"), 3)
        self.assertEqual(graph.edge_count, 1)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(graph.remove_edge("B", "A"), 3)
        self.assertIsNone(graph.weight("A", "B"))

    def test_directed_projection_keeps_minimum_reciprocal_weight(self) -> None:
        graph = WeightedGraph()
        graph.add_edge("A", "B", 8)
        graph.add_edge("B", "A", 3)
        graph.add_vertex("C")

        projected = graph.as_undirected()

        self.assertFalse(projected.directed)
        self.assertEqual(projected.weight("A", "B"), 3)
        self.assertEqual(set(projected.vertices), {"A", "B", "C"})

    def test_invalid_weight_and_vertex_are_rejected(self) -> None:
        graph = WeightedGraph()
        with self.assertRaises(ValueError):
            graph.add_edge("A", "B", float("inf"))
        with self.assertRaises(TypeError):
            graph.add_edge("A", "B", "heavy")
        with self.assertRaises(TypeError):
            graph.add_vertex([])
        with self.assertRaises(KeyError):
            graph.neighbours("missing")


if __name__ == "__main__":
    unittest.main()
