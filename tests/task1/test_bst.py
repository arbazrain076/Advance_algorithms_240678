import unittest

from task1_structures import BinarySearchTree, City


def city(name: str, population: int = 1) -> City:
    return City(name, 27.0, 85.0, population, 1.0)


class BinarySearchTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = BinarySearchTree()
        for name in ["Pokhara", "Biratnagar", "Surkhet", "Butwal", "Kathmandu"]:
            self.tree.insert(city(name))

    def test_find_is_case_insensitive(self) -> None:
        self.assertEqual(self.tree.find("  KATHMANDU  "), city("Kathmandu"))
        self.assertIsNone(self.tree.find("Dharan"))

    def test_duplicate_key_updates_without_growing(self) -> None:
        previous = self.tree.insert(city("POKHARA", population=999))

        self.assertEqual(previous, city("Pokhara"))
        self.assertEqual(len(self.tree), 5)
        self.assertEqual(self.tree.find("pokhara").population, 999)

    def test_inorder_and_invariants(self) -> None:
        names = [item.name for item in self.tree.inorder()]

        self.assertEqual(
            names,
            ["Biratnagar", "Butwal", "Kathmandu", "Pokhara", "Surkhet"],
        )
        self.assertTrue(self.tree.validate())

    def test_delete_leaf_one_child_two_children_and_root(self) -> None:
        for name in ["Kathmandu", "Butwal", "Pokhara", "Surkhet"]:
            with self.subTest(name=name):
                removed = self.tree.delete(name)
                self.assertIsNotNone(removed)
                self.assertIsNone(self.tree.find(name))
                self.assertTrue(self.tree.validate())

        self.assertEqual(len(self.tree), 1)
        self.assertIsNone(self.tree.delete("missing"))

    def test_sorted_input_exposes_linear_height(self) -> None:
        tree = BinarySearchTree()
        for name in ["A", "B", "C", "D"]:
            tree.insert(city(name))

        self.assertEqual(tree.height, 4)

    def test_empty_name_is_rejected_for_lookup(self) -> None:
        with self.assertRaises(ValueError):
            self.tree.find(" ")


if __name__ == "__main__":
    unittest.main()
