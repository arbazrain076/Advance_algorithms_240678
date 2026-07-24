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
5. **Concurrent programming:** sequential and process-based parallel merge sort in Python.

## Technologies Used

- Python 3.11 or newer
- Python standard library for algorithms, process-based concurrency, benchmarks, CSV output,
  and SVG generation
- pytest for the complete automated test suite

## Requirements

The implementations have no third-party runtime dependency. The development extras in
`pyproject.toml` install pytest for automated validation.

Check the required tool:

```powershell
python --version
```

## Installation

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Running the Python Tests

After installation, run all Task 1–5 tests:

```powershell
python -m pytest
```

Without installing the package, set the source path for the current PowerShell session first:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
```

## Running the Benchmarks

The following commands regenerate the retained CSV evidence in
`experiments/benchmark_data/`:

```powershell
python experiments/benchmark_scripts/task1_benchmark.py --trials 5
python experiments/benchmark_scripts/task2_benchmark.py --trials 5
python experiments/benchmark_scripts/task3_experiments.py --trials 5
python experiments/benchmark_scripts/task4_experiments.py --trials 5
python -m src.task5_concurrency.benchmark --trials 5
```

Regenerate the SVG figures from the retained CSV files:

```powershell
python experiments/benchmark_scripts/task1_figures.py
python experiments/benchmark_scripts/task2_figures.py
python experiments/benchmark_scripts/task3_figures.py
python experiments/benchmark_scripts/task4_figures.py
python experiments/benchmark_scripts/task5_figures.py
```

## Running the Task 5 Concurrency Benchmark

Task 5 keeps merge sort as the algorithm and uses
`concurrent.futures.ProcessPoolExecutor` with the Windows-safe `spawn` start method. Inputs below
the configurable threshold are processed sequentially to avoid process-startup overhead. Larger
inputs are divided into sorted runs and merged by worker processes. The benchmark module protects
process creation with `if __name__ == "__main__":`; custom entry-point scripts must use the same
guard on Windows.

```powershell
python -m pytest tests/task5
```

Run the complete benchmark for worker counts 1, 2, 4, and 8:

```powershell
python -m src.task5_concurrency.benchmark --trials 5
```

Use quick mode and a separate output file for a short validation that does not overwrite the
retained evidence:

```powershell
python -m src.task5_concurrency.benchmark --trials 1 --quick --threshold 512 --output tmp/task5_validation.csv
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
│   ├── task4_heuristics/
│   └── task5_concurrency/
├── tests/
│   ├── task1/
│   ├── task2/
│   ├── task3/
│   ├── task4/
│   └── task5/
├── experiments/
│   ├── benchmark_scripts/
│   ├── benchmark_data/
│   └── figures/
└── pyproject.toml
```

## Generated Benchmark Data and Figures

- `experiments/benchmark_data/` contains the retained CSV measurements for all five tasks.
- `experiments/figures/` contains the reproducible SVG charts and algorithm traces.
- Benchmark scripts accept deterministic seeds and record the operation, input size, trial, and
  measured runtime needed to interpret each result.

Student ID: **240678**
