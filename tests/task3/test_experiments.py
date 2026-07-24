import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "experiments"
    / "benchmark_scripts"
    / "task3_experiments.py"
)
SPEC = importlib.util.spec_from_file_location("task3_experiments", SCRIPT)
experiments = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = experiments
SPEC.loader.exec_module(experiments)


class StrategyExperimentTests(unittest.TestCase):
    def test_job_generation_is_deterministic(self) -> None:
        self.assertEqual(
            experiments.generate_jobs(10, 123),
            experiments.generate_jobs(10, 123),
        )

    def test_one_trial_produces_all_experiment_families(self) -> None:
        rows = experiments.run_experiments(trials=1)

        self.assertEqual(
            {row.experiment for row in rows},
            {"weighted_jobs", "weighted_greedy", "exam_timetabling"},
        )
        self.assertTrue(all(row.total_ns > 0 for row in rows))
        dynamic_rows = [
            row for row in rows if row.experiment == "weighted_jobs"
        ]
        by_size: dict[int, set[float]] = {}
        for row in dynamic_rows:
            by_size.setdefault(row.size, set()).add(row.objective)
        self.assertTrue(all(len(objectives) == 1 for objectives in by_size.values()))


if __name__ == "__main__":
    unittest.main()
