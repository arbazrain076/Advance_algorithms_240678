import unittest

from task1_structures import City


class CityTests(unittest.TestCase):
    def test_city_normalizes_name_and_key(self) -> None:
        city = City("  Kathmandu  ", 27.7172, 85.3240, 845_767, 12.5)

        self.assertEqual(city.name, "Kathmandu")
        self.assertEqual(city.key, "kathmandu")

    def test_city_rejects_invalid_values(self) -> None:
        invalid_values = [
            ("name", " "),
            ("latitude", 90.1),
            ("longitude", -180.1),
            ("population", -1),
            ("distance", -0.1),
            ("distance", float("inf")),
        ]

        for field, value in invalid_values:
            values = {
                "name": "Pokhara",
                "latitude": 28.2096,
                "longitude": 83.9856,
                "population": 518_452,
                "distance": 0.0,
            }
            values[field] = value

            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    City(**values)


if __name__ == "__main__":
    unittest.main()
