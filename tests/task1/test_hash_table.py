import unittest

from task1_structures import City, CityHashTable


def city(name: str, population: int = 1) -> City:
    return City(name, 27.0, 85.0, population, 1.0)


class CityHashTableTests(unittest.TestCase):
    def test_insert_find_and_case_insensitive_update(self) -> None:
        table = CityHashTable()
        self.assertIsNone(table.insert(city("Kathmandu", 100)))
        previous = table.insert(city("KATHMANDU", 200))

        self.assertEqual(previous.population, 100)
        self.assertEqual(table.find(" kathmandu ").population, 200)
        self.assertEqual(len(table), 1)
        self.assertTrue(table.validate())

    def test_resize_preserves_all_entries(self) -> None:
        table = CityHashTable(capacity=8, max_load=0.5)
        for index in range(100):
            table.insert(city(f"City {index}"))

        self.assertGreaterEqual(table.statistics.capacity, 256)
        self.assertEqual(table.statistics.entries, 100)
        self.assertTrue(all(table.find(f"CITY {index}") is not None for index in range(100)))
        self.assertTrue(table.validate())

    def test_chains_preserve_colliding_keys(self) -> None:
        table = CityHashTable(capacity=8, max_load=2.0)
        names_by_bucket: dict[int, list[str]] = {}
        for index in range(100):
            name = f"Candidate {index}"
            bucket = table._fnv1a(name.casefold()) & 7
            names_by_bucket.setdefault(bucket, []).append(name)
        colliding = next(names for names in names_by_bucket.values() if len(names) >= 3)[:3]

        for name in colliding:
            table.insert(city(name))

        self.assertEqual(table.statistics.collisions, 2)
        self.assertEqual(table.statistics.longest_chain, 3)
        self.assertTrue(all(table.find(name) is not None for name in colliding))

    def test_delete_and_shrink_preserve_invariants(self) -> None:
        table = CityHashTable(capacity=32)
        for index in range(20):
            table.insert(city(f"City {index}"))
        for index in range(18):
            self.assertIsNotNone(table.delete(f"city {index}"))
            self.assertTrue(table.validate())

        self.assertEqual(table.statistics.capacity, 8)
        self.assertIsNone(table.delete("missing"))
        self.assertEqual(len(table), 2)

    def test_invalid_configuration_and_empty_key_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CityHashTable(capacity=0)
        with self.assertRaises(ValueError):
            CityHashTable(max_load=0.1)
        with self.assertRaises(ValueError):
            CityHashTable().find(" ")


if __name__ == "__main__":
    unittest.main()
