# Advanced Algorithms — Student 240678

## Project Overview

This repository contains the implementations, tests, reproducible benchmarks, and generated
figures for the ST5003CEM Advanced Algorithms coursework. Each assessed task is kept in an
independent package so its correctness, complexity, and measured behaviour can be evaluated
without coupling it to another task.

## Tasks Implemented

1. **Advanced data structures:** binary search tree, AVL tree, min-heap, and hash table.
2. **Graph algorithms:** Dijkstra shortest paths, Prim minimum spanning forest, and
   Bellman–Ford shortest paths with negative-cycle reporting.
3. **Algorithmic strategies:** dynamic programming for weighted scheduling, greedy interval
   heuristics, and pruned backtracking for exam timetabling.
4. **NP-hard optimisation:** multi-resource bin packing using greedy construction, local
   search, and an exact small-instance reference.
5. **Concurrent programming:** sequential and synchronised parallel merge sort in Java.

## Technologies Used

- Python 3.11 or newer
- Java Development Kit 17 or newer
- PowerShell 5.1 or newer for the Java helper scripts
- Python standard library for algorithms, tests, benchmarks, CSV output, and SVG generation

## Requirements

The Python implementations have no third-party runtime dependency. The project metadata is
defined in `pyproject.toml`. A JDK is required only for Task 5.

Check the required tools:

```powershell
python --version
javac -version
java -version
```

## Installation

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Running the Python Tests

After installation, run all Task 1–4 tests:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Without installing the package, set the source path for the current PowerShell session first:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -p "test_*.py" -v
```

## Running the Benchmarks

The following commands regenerate the retained CSV evidence in
`experiments/benchmark_data/`:

```powershell
python experiments/benchmark_scripts/task1_benchmark.py --trials 5
python experiments/benchmark_scripts/task2_benchmark.py --trials 5
python experiments/benchmark_scripts/task3_experiments.py --trials 5
python experiments/benchmark_scripts/task4_experiments.py --trials 5
```

Regenerate the SVG figures from the retained CSV files:

```powershell
python experiments/benchmark_scripts/task1_figures.py
python experiments/benchmark_scripts/task2_figures.py
python experiments/benchmark_scripts/task3_figures.py
python experiments/benchmark_scripts/task4_figures.py
python experiments/benchmark_scripts/task5_figures.py
```

## Compiling and Running the Java Concurrency Task

The test helper compiles the Java source and test classes with warnings treated as errors, then
runs the concurrency checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File task5_concurrency/run_tests.ps1
```

Run the Task 5 benchmark and write its CSV results to the shared benchmark-data directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File task5_concurrency/run_benchmark.ps1 -Trials 5
```

Use `-Quick` for a shorter benchmark validation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File task5_concurrency/run_benchmark.ps1 -Trials 1 -Quick -Output tmp/task5_validation.csv
```

## Repository Structure

```text
.
├── README.md
├── .gitignore
├── pyproject.toml
├── src/
│   ├── task1_structures/
│   ├── task2_graphs/
│   ├── task3_strategies/
│   └── task4_heuristics/
├── tests/
│   ├── task1/
│   ├── task2/
│   ├── task3/
│   └── task4/
├── experiments/
│   ├── benchmark_scripts/
│   ├── benchmark_data/
│   └── figures/
└── task5_concurrency/
    ├── src/
    ├── test/
    ├── run_tests.ps1
    └── run_benchmark.ps1
```

## Generated Benchmark Data and Figures

- `experiments/benchmark_data/` contains the retained CSV measurements for all five tasks.
- `experiments/figures/` contains the reproducible SVG charts and algorithm traces.
- Benchmark scripts accept deterministic seeds and record the operation, input size, trial, and
  measured runtime needed to interpret each result.

Student ID: **240678**
