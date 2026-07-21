import random
import unittest

from task3_strategies import (
    Job,
    exhaustive_weighted_schedule,
    weighted_job_schedule,
)


class WeightedJobSchedulingTests(unittest.TestCase):
    def test_canonical_schedule_and_reconstruction(self) -> None:
        jobs = [
            Job("A", 1, 2, 50),
            Job("B", 3, 5, 20),
            Job("C", 6, 19, 100),
            Job("D", 2, 100, 200),
        ]

        result = weighted_job_schedule(jobs)

        self.assertEqual(result.maximum_profit, 250)
        self.assertEqual([job.identifier for job in result.selected_jobs], ["A", "D"])
        self.assertEqual(len(result.states), len(jobs))

    def test_touching_intervals_are_compatible(self) -> None:
        result = weighted_job_schedule(
            [
                Job("A", 0, 1, 5),
                Job("B", 1, 2, 6),
                Job("C", 2, 3, 7),
            ]
        )
        self.assertEqual(result.maximum_profit, 18)

    def test_dynamic_program_matches_exhaustive_reference(self) -> None:
        generator = random.Random(24_0678)
        for trial in range(30):
            jobs = []
            for index in range(10):
                start = generator.randint(0, 20)
                jobs.append(
                    Job(
                        f"{trial}-{index}",
                        start,
                        start + generator.randint(1, 7),
                        generator.randint(1, 50),
                    )
                )
            with self.subTest(trial=trial):
                dynamic = weighted_job_schedule(jobs)
                exhaustive = exhaustive_weighted_schedule(jobs)
                self.assertEqual(dynamic.maximum_profit, exhaustive.maximum_profit)

    def test_empty_input_and_tie_policy(self) -> None:
        self.assertEqual(weighted_job_schedule([]).maximum_profit, 0)
        result = weighted_job_schedule(
            [Job("A", 0, 2, 10), Job("B", 0, 1, 10)]
        )
        self.assertEqual(len(result.selected_jobs), 1)

    def test_invalid_jobs_and_duplicate_identifiers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Job("", 0, 1, 1)
        with self.assertRaises(ValueError):
            Job("A", 1, 1, 1)
        with self.assertRaises(ValueError):
            Job("A", 0, 1, -1)
        with self.assertRaises(ValueError):
            weighted_job_schedule([Job("A", 0, 1, 1), Job("A", 2, 3, 2)])


if __name__ == "__main__":
    unittest.main()
