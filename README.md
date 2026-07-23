# Advance Algorithms 240678

Implementation, testing, benchmarking, and analysis for the ST5003CEM Advanced Algorithms
coursework.

The coursework is organised as independent task packages so that every algorithm can be run,
tested, and evaluated separately. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete design,
experiment methodology, and delivery schedule.

## Current Progress

- [x] Assignment requirements mapped to an implementation plan
- [x] Task 1 - Advanced Data Structures
- [x] Task 2 - Graph Algorithms and Pathfinding
- [x] Task 3 - Algorithmic Strategies
- [x] Task 4 - NP-Hard Problem and Heuristics
- [x] Task 5 - Concurrent Programming
- [ ] Integrated analysis and final reproducibility audit

## Quick Start

Commands will be added with each completed task. Python implementations target Python 3.11 or
newer, while the concurrency task targets a C++17 compiler.

## Task 1 Commands

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py' -v
python experiments/task1_benchmark.py --trials 5
python experiments/task1_figures.py
```

Task 1's design, complexity analysis, benchmark interpretation, limitations, and use-case decisions
are documented in [reports/task1_analysis.md](reports/task1_analysis.md).

## Task 2 Commands

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py' -v
python experiments/task2_benchmark.py --trials 5
python experiments/task2_figures.py
```

Task 2's graph-model justification, algorithm traces, runtime comparison, constant-factor discussion,
and limitations are documented in [reports/task2_analysis.md](reports/task2_analysis.md).

## Task 3 Commands

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py' -v
python experiments/task3_experiments.py --trials 5
python experiments/task3_figures.py
```

Task 3's recurrence, greedy proof and counterexamples, pruning strategy, empirical comparison, and
limitations are documented in [reports/task3_analysis.md](reports/task3_analysis.md).

## Task 4 Commands

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py' -v
python experiments/task4_experiments.py --trials 5
python experiments/task4_figures.py
```

Task 4's NP-hardness argument, heuristic design, exact small-instance reference, quality/runtime
trade-off, and limitations are documented in [reports/task4_analysis.md](reports/task4_analysis.md).

## Task 5 Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File task5_concurrency/run_tests.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File task5_concurrency/run_benchmark.ps1 -Trials 5
python experiments/task5_figures.py
```

Task 5's critical sections, synchronisation strategy, correctness checks, speedup, efficiency, and
scalability limits are documented in [reports/task5_analysis.md](reports/task5_analysis.md).
