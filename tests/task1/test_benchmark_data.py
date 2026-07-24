import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "experiments"
    / "benchmark_scripts"
    / "task1_benchmark.py"
)
SPEC = importlib.util.spec_from_file_location("task1_benchmark", SCRIPT)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)


class BenchmarkDataTests(unittest.TestCase):
    def test_generation_is_deterministic_and_valid(self) -> None:
        first = benchmark.generate_cities(20, seed=123)
        second = benchmark.generate_cities(20, seed=123)

        self.assertEqual(first, second)
        self.assertEqual(len({city.key for city in first}), 20)

    def test_single_trial_covers_required_operations(self) -> None:
        cities = benchmark.generate_cities(20, seed=123)
        rows = benchmark.run_trial("AVL", cities, "sorted", trial=1, seed=456)

        self.assertEqual(
            {row.operation for row in rows},
            {"insert", "successful_search", "unsuccessful_search", "delete"},
        )
        self.assertTrue(all(row.total_ns > 0 for row in rows))
        self.assertTrue(all(row.audit_metric == "height" for row in rows))


if __name__ == "__main__":
    unittest.main()
