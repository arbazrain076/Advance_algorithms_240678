import math
import unittest

from task1_structures import AVLTree, City


def city(name: str, population: int = 1) -> City:
    return City(name, 27.0, 85.0, population, 1.0)


class AVLTreeTests(unittest.TestCase):
    def test_all_rotation_patterns_preserve_invariants(self) -> None:
        patterns = [
            ["C", "B", "A"],
            ["A", "B", "C"],
            ["C", "A", "B"],
            ["A", "C", "B"],
        ]
        for names in patterns:
            with self.subTest(names=names):
                tree = AVLTree()
                for name in names:
                    tree.insert(city(name))
                self.assertEqual([item.name for item in tree.inorder()], ["A", "B", "C"])
                self.assertEqual(tree.height, 2)
                self.assertTrue(tree.validate())

    def test_update_is_case_insensitive_and_does_not_grow(self) -> None:
        tree = AVLTree()
        tree.insert(city("Kathmandu", 100))
        previous = tree.insert(city("KATHMANDU", 200))

        self.assertEqual(previous.population, 100)
        self.assertEqual(tree.find("kathmandu").population, 200)
        self.assertEqual(len(tree), 1)

    def test_deletion_rebalances_tree(self) -> None:
        tree = AVLTree()
        for index in range(32):
            tree.insert(city(f"City {index:02}"))

        for index in [0, 2, 1, 15, 31, 20, 21]:
            removed = tree.delete(f"CITY {index:02}")
            self.assertIsNotNone(removed)
            self.assertTrue(tree.validate())

        self.assertIsNone(tree.delete("missing"))
        self.assertEqual(len(tree), 25)

    def test_sorted_input_remains_logarithmic_height(self) -> None:
        tree = AVLTree()
        for index in range(1_000):
            tree.insert(city(f"City {index:04}"))

        conservative_avl_bound = math.ceil(1.45 * math.log2(1_000 + 2))
        self.assertLessEqual(tree.height, conservative_avl_bound)
        self.assertTrue(tree.validate())

    def test_empty_lookup_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AVLTree().find("")


if __name__ == "__main__":
    unittest.main()
