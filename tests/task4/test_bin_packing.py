import unittest

from task4_heuristics import (
    BinCapacity,
    Item,
    best_fit_decreasing,
    validate_packing,
)


class BestFitDecreasingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.capacity = BinCapacity(cpu=10, ram=10, bandwidth=10)

    def test_greedy_counterexample_remains_feasible(self) -> None:
        items = [
            Item("A", 6, 2, 2),
            Item("B", 4, 8, 1),
            Item("C", 4, 2, 8),
            Item("D", 6, 1, 2),
        ]

        result = best_fit_decreasing(items, self.capacity)

        self.assertTrue(validate_packing(result, items, self.capacity))
        # Greedy first combines B and C, preventing the optimal pairings A+C and B+D.
        self.assertEqual(result.bin_count, 3)

    def test_result_is_deterministic(self) -> None:
        items = [
            Item("A", 4, 4, 4),
            Item("B", 4, 4, 4),
            Item("C", 6, 6, 6),
        ]
        first = best_fit_decreasing(items, self.capacity)
        second = best_fit_decreasing(reversed(items), self.capacity)

        self.assertEqual(
            [[item.identifier for item in group] for group in first.bins],
            [[item.identifier for item in group] for group in second.bins],
        )

    def test_empty_instance_uses_no_bins(self) -> None:
        result = best_fit_decreasing([], self.capacity)
        self.assertEqual(result.bin_count, 0)
        self.assertTrue(validate_packing(result, [], self.capacity))

    def test_invalid_models_and_oversized_items_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Item("", 1, 1, 1)
        with self.assertRaises(ValueError):
            Item("A", 0, 1, 1)
        with self.assertRaises(ValueError):
            BinCapacity(0, 1, 1)
        with self.assertRaises(ValueError):
            best_fit_decreasing([Item("A", 11, 1, 1)], self.capacity)
        with self.assertRaises(ValueError):
            best_fit_decreasing(
                [Item("A", 1, 1, 1), Item("A", 2, 2, 2)],
                self.capacity,
            )


if __name__ == "__main__":
    unittest.main()
