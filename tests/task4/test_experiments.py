import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "experiments" / "task4_experiments.py"
SPEC = importlib.util.spec_from_file_location("task4_experiments", SCRIPT)
experiments = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = experiments
SPEC.loader.exec_module(experiments)


class PackingExperimentTests(unittest.TestCase):
    def test_item_generation_is_deterministic(self) -> None:
        self.assertEqual(
            experiments.generate_items(10, 123),
            experiments.generate_items(10, 123),
        )

    def test_small_instance_compares_all_methods(self) -> None:
        items = experiments.generate_items(8, 123)
        rows = experiments.evaluate_instance(items, trial=1, include_exact=True)

        self.assertEqual({row.method for row in rows}, {"Greedy", "Local search", "Exact"})
        exact = next(row for row in rows if row.method == "Exact")
        self.assertEqual(exact.optimality_gap, 0)
        self.assertTrue(all(row.bins >= row.lower_bound for row in rows))

    def test_large_instance_skips_exponential_reference(self) -> None:
        items = experiments.generate_items(20, 123)
        rows = experiments.evaluate_instance(items, trial=1, include_exact=False)
        self.assertEqual({row.method for row in rows}, {"Greedy", "Local search"})
        self.assertTrue(all(row.optimality_gap == -1 for row in rows))


if __name__ == "__main__":
    unittest.main()
