import unittest

from task3_strategies import (
    Job,
    compare_greedy,
    find_counterexample,
    greedy_weighted_schedule,
)


class WeightedIntervalGreedyTests(unittest.TestCase):
    def test_earliest_finish_is_optimal_when_all_weights_are_equal(self) -> None:
        jobs = [
            Job("A", 0, 3, 1),
            Job("B", 1, 2, 1),
            Job("C", 2, 4, 1),
            Job("D", 3, 5, 1),
            Job("E", 4, 6, 1),
        ]

        comparison = compare_greedy(jobs, "earliest_finish")

        self.assertTrue(comparison.is_optimal)
        self.assertEqual(comparison.greedy.maximum_profit, 3)

    def test_weighted_earliest_finish_can_be_suboptimal(self) -> None:
        jobs = [
            Job("early", 0, 2, 4),
            Job("valuable", 0, 3, 10),
            Job("late", 2, 4, 4),
        ]

        comparison = compare_greedy(jobs, "earliest_finish")

        self.assertEqual(comparison.greedy.maximum_profit, 8)
        self.assertEqual(comparison.optimal.maximum_profit, 10)
        self.assertEqual(comparison.optimality_gap, 2)

    def test_counterexamples_are_discovered_not_hard_coded(self) -> None:
        for rule in ["earliest_finish", "shortest_duration", "highest_weight"]:
            with self.subTest(rule=rule):
                comparison = find_counterexample(rule)
                self.assertGreater(comparison.optimality_gap, 0)

    def test_all_rules_return_compatible_jobs(self) -> None:
        jobs = [
            Job("A", 0, 4, 8),
            Job("B", 1, 2, 2),
            Job("C", 2, 3, 3),
            Job("D", 3, 5, 5),
        ]
        for rule in ["earliest_finish", "shortest_duration", "highest_weight"]:
            result = greedy_weighted_schedule(jobs, rule)
            self.assertTrue(
                all(
                    left.end <= right.start
                    for left, right in zip(result.selected_jobs, result.selected_jobs[1:])
                )
            )

    def test_unknown_rule_and_duplicate_identifiers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            greedy_weighted_schedule([], "not-a-rule")
        duplicate = [Job("A", 0, 1, 1), Job("A", 2, 3, 1)]
        with self.assertRaises(ValueError):
            greedy_weighted_schedule(duplicate)


if __name__ == "__main__":
    unittest.main()
