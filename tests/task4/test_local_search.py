import random
import unittest

from task4_heuristics import (
    BinCapacity,
    Item,
    best_fit_decreasing,
    local_search,
    validate_packing,
)


class LocalSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.capacity = BinCapacity(10, 10, 10)

    def test_relocation_repairs_greedy_counterexample(self) -> None:
        items = [
            Item("A", 6, 2, 2),
            Item("B", 4, 8, 1),
            Item("C", 4, 2, 8),
            Item("D", 6, 1, 2),
        ]
        greedy = best_fit_decreasing(items, self.capacity)

        improved = local_search(items, self.capacity, greedy)

        self.assertEqual(greedy.bin_count, 3)
        self.assertEqual(improved.bin_count, 2)
        self.assertGreater(improved.evaluated_moves, 0)
        self.assertGreater(improved.accepted_moves, 0)
        self.assertTrue(validate_packing(improved, items, self.capacity))

    def test_local_search_never_increases_bin_count(self) -> None:
        generator = random.Random(24_0678)
        for trial in range(20):
            items = [
                Item(
                    f"{trial}-{index}",
                    generator.randint(1, 7),
                    generator.randint(1, 7),
                    generator.randint(1, 7),
                )
                for index in range(15)
            ]
            greedy = best_fit_decreasing(items, self.capacity)
            improved = local_search(items, self.capacity, greedy)
            with self.subTest(trial=trial):
                self.assertLessEqual(improved.bin_count, greedy.bin_count)
                self.assertTrue(validate_packing(improved, items, self.capacity))

    def test_empty_input_and_invalid_arguments(self) -> None:
        result = local_search([], self.capacity)
        self.assertEqual(result.bin_count, 0)
        with self.assertRaises(ValueError):
            local_search([], self.capacity, max_passes=0)


if __name__ == "__main__":
    unittest.main()
