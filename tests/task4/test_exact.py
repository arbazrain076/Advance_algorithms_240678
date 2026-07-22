import random
import unittest

from task4_heuristics import (
    BinCapacity,
    Item,
    best_fit_decreasing,
    exact_branch_and_bound,
    resource_lower_bound,
    validate_packing,
)


class ExactBinPackingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.capacity = BinCapacity(10, 10, 10)

    def test_certifies_greedy_counterexample(self) -> None:
        items = [
            Item("A", 6, 2, 2),
            Item("B", 4, 8, 1),
            Item("C", 4, 2, 8),
            Item("D", 6, 1, 2),
        ]

        greedy = best_fit_decreasing(items, self.capacity)
        exact = exact_branch_and_bound(items, self.capacity)

        self.assertEqual(greedy.bin_count, 3)
        self.assertEqual(exact.bin_count, 2)
        self.assertEqual(resource_lower_bound(items, self.capacity), 2)
        self.assertTrue(validate_packing(exact, items, self.capacity))

    def test_capacity_forces_three_bins(self) -> None:
        items = [
            Item("A", 6, 1, 1),
            Item("B", 6, 1, 1),
            Item("C", 6, 1, 1),
        ]
        exact = exact_branch_and_bound(items, self.capacity)
        self.assertEqual(exact.bin_count, 3)

    def test_exact_is_never_worse_than_greedy_on_small_instances(self) -> None:
        generator = random.Random(24_0678)
        for trial in range(20):
            items = [
                Item(
                    f"{trial}-{index}",
                    generator.randint(1, 7),
                    generator.randint(1, 7),
                    generator.randint(1, 7),
                )
                for index in range(8)
            ]
            greedy = best_fit_decreasing(items, self.capacity)
            exact = exact_branch_and_bound(items, self.capacity)
            with self.subTest(trial=trial):
                self.assertLessEqual(exact.bin_count, greedy.bin_count)
                self.assertTrue(validate_packing(exact, items, self.capacity))

    def test_empty_instance(self) -> None:
        exact = exact_branch_and_bound([], self.capacity)
        self.assertEqual(exact.bin_count, 0)
        self.assertEqual(resource_lower_bound([], self.capacity), 0)


if __name__ == "__main__":
    unittest.main()
