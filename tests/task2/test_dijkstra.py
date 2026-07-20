import math
import unittest

from task2_graphs import WeightedGraph, dijkstra


class DijkstraTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = WeightedGraph()
        for source, target, weight in [
            ("Kathmandu", "Bhaktapur", 12),
            ("Kathmandu", "Pokhara", 200),
            ("Bhaktapur", "Dhulikhel", 18),
            ("Dhulikhel", "Pokhara", 145),
            ("Bhaktapur", "Pokhara", 190),
        ]:
            self.graph.add_edge(source, target, weight)
        self.graph.add_vertex("Janakpur")

    def test_shortest_distances_and_path_reconstruction(self) -> None:
        result = dijkstra(self.graph, "Kathmandu")

        self.assertEqual(result.distances["Pokhara"], 175)
        self.assertEqual(
            result.path_to("Pokhara"),
            ("Kathmandu", "Bhaktapur", "Dhulikhel", "Pokhara"),
        )
        self.assertTrue(math.isinf(result.distances["Janakpur"]))
        self.assertEqual(result.path_to("Janakpur"), ())

    def test_trace_records_settlement_and_successful_relaxation(self) -> None:
        result = dijkstra(self.graph, "Kathmandu")

        settled = [event.vertex for event in result.events if event.action == "settle"]
        relaxed = [event.vertex for event in result.events if event.action == "relax"]
        self.assertEqual(settled, ["Kathmandu", "Bhaktapur", "Dhulikhel", "Pokhara"])
        self.assertGreaterEqual(relaxed.count("Pokhara"), 2)
        self.assertEqual(
            [event.step for event in result.events],
            list(range(1, len(result.events) + 1)),
        )

    def test_negative_edge_is_rejected(self) -> None:
        self.graph.add_edge("Pokhara", "Butwal", -1)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            dijkstra(self.graph, "Kathmandu")

    def test_unknown_vertices_raise_clear_errors(self) -> None:
        with self.assertRaises(KeyError):
            dijkstra(self.graph, "missing")
        with self.assertRaises(KeyError):
            dijkstra(self.graph, "Kathmandu").path_to("missing")


if __name__ == "__main__":
    unittest.main()
