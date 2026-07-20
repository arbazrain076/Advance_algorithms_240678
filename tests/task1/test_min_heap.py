import unittest

from task1_structures import City, MinHeap


def city(name: str, distance: float) -> City:
    return City(name, 27.0, 85.0, 1, distance)


class MinHeapTests(unittest.TestCase):
    def test_push_and_pop_return_priority_order(self) -> None:
        heap = MinHeap()
        cities = [
            city("Pokhara", 200),
            city("Bhaktapur", 12),
            city("Lalitpur", 12),
            city("Biratnagar", 380),
        ]
        for item in cities:
            heap.push(item)
            self.assertTrue(heap.validate())

        self.assertEqual(heap.peek().name, "Bhaktapur")
        self.assertEqual(
            [heap.pop().name for _ in range(len(heap))],
            ["Bhaktapur", "Lalitpur", "Pokhara", "Biratnagar"],
        )

    def test_linear_heapify_builds_valid_heap(self) -> None:
        heap = MinHeap([city(str(index), float(100 - index)) for index in range(100)])

        self.assertTrue(heap.validate())
        self.assertEqual(heap.peek().distance, 1)

    def test_find_and_remove_repair_heap(self) -> None:
        heap = MinHeap(
            [
                city("A", 1),
                city("B", 4),
                city("C", 2),
                city("D", 8),
                city("E", 5),
            ]
        )

        self.assertEqual(heap.find(" c ").name, "C")
        self.assertEqual(heap.remove("A").name, "A")
        self.assertEqual(heap.remove("D").name, "D")
        self.assertIsNone(heap.remove("missing"))
        self.assertTrue(heap.validate())
        self.assertEqual([heap.pop().distance for _ in range(len(heap))], [2, 4, 5])

    def test_empty_operations_raise_clear_errors(self) -> None:
        heap = MinHeap()
        with self.assertRaisesRegex(IndexError, "empty heap"):
            heap.peek()
        with self.assertRaisesRegex(IndexError, "empty heap"):
            heap.pop()
        with self.assertRaises(ValueError):
            heap.find(" ")


if __name__ == "__main__":
    unittest.main()
