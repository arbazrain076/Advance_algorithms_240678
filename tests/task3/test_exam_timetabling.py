import unittest

from task3_strategies import Exam, ExamTimetabler, Placement, Room


class ExamTimetablingTests(unittest.TestCase):
    def test_solver_satisfies_conflicts_rooms_and_capacity(self) -> None:
        exams = [
            Exam("Algorithms", 80),
            Exam("Databases", 45),
            Exam("Networks", 35),
            Exam("Security", 60),
        ]
        rooms = [Room("Hall", 100), Room("Lab", 50)]
        conflicts = [
            ("Algorithms", "Databases"),
            ("Algorithms", "Security"),
            ("Databases", "Networks"),
        ]
        solver = ExamTimetabler(exams, conflicts, slots=3, rooms=rooms)

        result = solver.solve(use_pruning=True)

        self.assertTrue(result.solved)
        self.assertTrue(solver.validate(result.assignments))
        self.assertGreater(result.nodes_visited, 0)
        self.assertTrue(result.events)

    def test_conflicting_exams_never_share_a_slot(self) -> None:
        solver = ExamTimetabler(
            [Exam("A", 10), Exam("B", 10)],
            [("A", "B")],
            slots=2,
            rooms=[Room("R1", 20), Room("R2", 20)],
        )
        result = solver.solve()

        self.assertNotEqual(
            result.assignments["A"].slot,
            result.assignments["B"].slot,
        )

    def test_forward_checking_reduces_unsatisfiable_search(self) -> None:
        exams = [Exam(chr(65 + index), 10) for index in range(5)]
        solver = ExamTimetabler(exams, [], slots=4, rooms=[Room("Only", 20)])

        baseline = solver.solve(use_pruning=False)
        pruned = solver.solve(use_pruning=True)

        self.assertFalse(baseline.solved)
        self.assertFalse(pruned.solved)
        self.assertLess(pruned.nodes_visited, baseline.nodes_visited)
        self.assertGreater(pruned.forward_prunes, 0)

    def test_validation_detects_invalid_assignment(self) -> None:
        solver = ExamTimetabler(
            [Exam("A", 30), Exam("B", 30)],
            [("A", "B")],
            slots=2,
            rooms=[Room("R", 40)],
        )
        invalid = {"A": Placement(0, "R"), "B": Placement(0, "R")}
        self.assertFalse(solver.validate(invalid))

    def test_invalid_problem_definitions_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Exam("", 10)
        with self.assertRaises(ValueError):
            Room("R", 0)
        with self.assertRaises(ValueError):
            ExamTimetabler([], [], 1, [Room("R", 10)])
        with self.assertRaises(ValueError):
            ExamTimetabler(
                [Exam("A", 10)],
                [("A", "missing")],
                1,
                [Room("R", 10)],
            )


if __name__ == "__main__":
    unittest.main()
