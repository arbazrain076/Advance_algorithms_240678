import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "experiments" / "task2_benchmark.py"
SPEC = importlib.util.spec_from_file_location("task2_benchmark", SCRIPT)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)


class GraphBenchmarkTests(unittest.TestCase):
    def test_generation_is_deterministic_and_reachable(self) -> None:
        first = benchmark.generate_graph(20, 0.2, 123)
        second = benchmark.generate_graph(20, 0.2, 123)

        self.assertEqual(list(first.edges()), list(second.edges()))
        result = benchmark.dijkstra(first, 0)
        self.assertTrue(all(distance < float("inf") for distance in result.distances.values()))

    def test_trial_covers_all_algorithms(self) -> None:
        graph = benchmark.generate_graph(10, 0.2, 123)
        rows = benchmark.run_trial(graph, "sparse", 1)

        self.assertEqual({row.algorithm for row in rows}, {"Dijkstra", "Bellman-Ford", "Prim"})
        self.assertTrue(all(row.total_ns > 0 for row in rows))
        self.assertTrue(all(row.ns_per_complexity_unit > 0 for row in rows))

    def test_invalid_generation_parameters_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            benchmark.generate_graph(1, 0.2, 123)
        with self.assertRaises(ValueError):
            benchmark.generate_graph(10, 0, 123)


if __name__ == "__main__":
    unittest.main()
