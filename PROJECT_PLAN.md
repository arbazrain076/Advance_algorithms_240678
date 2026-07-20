# Advanced Algorithms Coursework Project Plan

## 1. Goal

Build five independently runnable, well-tested task packages that demonstrate implementation skill,
theoretical analysis, empirical measurement, visual explanation, and critical evaluation. Each task
will produce reproducible evidence rather than relying only on written claims.

## 2. Project Standards

- Python 3.11+ for Tasks 1-4; C++17 standard threads for the compute-bound concurrency experiment.
- Deterministic datasets using recorded random seeds.
- Wall-clock benchmarks use `time.perf_counter_ns`, warm-up runs, repeated trials, and median values.
- Every experiment records raw CSV data before generating a chart.
- Tests cover normal cases, edge cases, invalid input, and algorithm-specific invariants.
- Each task has its own README with commands, design decisions, complexity tables, and findings.
- Charts have descriptive titles, labelled axes, units, legends, and accessible colours.
- Code comments explain reasoning and invariants, not obvious syntax.

## 3. Independent Task Strategy

### Task 1 - Advanced Data Structures

Build a route-planning data layer around a `City` record:

- Binary Search Tree keyed by city name.
- AVL Tree with rotations and explicit balance checks.
- Min-Heap keyed by route distance.
- Hash Table using separate chaining and controlled resizing.

Experiments will use 100, 1,000, and 10,000 cities. Two input orders (random and sorted) will expose
the BST's worst-case shape while showing why AVL balancing matters. Separate workloads will measure
insert, successful search, unsuccessful search, and deletion. Heap priority extraction and hash-table
collision behaviour will be reported independently because they answer different use cases.

Distinctive output: a structure audit reports tree height, AVL balance validity, heap-order validity,
hash load factor, bucket distribution, and observed nanoseconds per operation alongside total time.

### Task 2 - Graph Algorithms and Pathfinding

Represent a directed transport network with an adjacency list, ideal for sparse road networks.

- Dijkstra: non-negative shortest paths using a binary heap.
- Bellman-Ford: negative-edge support and a reproducible negative-cycle witness.
- Prim: minimum spanning forest on an explicitly undirected projection of the network. This semantic
  distinction will be stated clearly because an MST is not defined for a general directed graph.

Experiments will vary both vertex count and graph density. Step-event logs will drive diagrams showing
relaxations, settled vertices, selected MST edges, and negative-cycle detection.

Distinctive output: the same small network will be replayed algorithm-by-algorithm, followed by a
sparse/dense benchmark that separates asymptotic growth from measured constant factors.

### Task 3 - Algorithmic Strategies

Three approved problems will be implemented independently:

1. Dynamic programming - Weighted Job Scheduling. Provide the recurrence
   `OPT(i) = max(profit[i] + OPT(p(i)), OPT(i-1))`, reconstruct the chosen schedule, and compare
   bottom-up DP with exhaustive search on small instances.
2. Greedy - Weighted Interval Scheduling counterexample. Test common greedy rules (earliest finish,
   shortest duration, and highest weight) against the exact DP optimum. Automatically search for a
   small counterexample and explain why the greedy-choice property fails in general.
3. Backtracking - Exam Timetabling. Use most-constrained-variable ordering, least-constraining-value
   ordering, forward checking, and symmetry breaking. Compare explored states with pruning enabled
   and disabled.

Distinctive output: each paradigm includes a decision trace and an exact small-instance reference,
making correctness and limitations visible rather than asserted.

### Task 4 - NP-Hard Problem and Heuristics

Choose Multi-dimensional Bin Packing with CPU, RAM, and bandwidth constraints.

- Explain NP-hardness by restriction from one-dimensional bin packing.
- Greedy baseline: multi-resource best-fit decreasing using dominant resource utilisation.
- Local search: relocate and swap moves that try to empty lightly loaded bins.
- Optional extension if time permits: GRASP with a restricted candidate list and repeated construction.

Evaluate solution quality, feasibility, runtime, and stability across multiple seeds. Small instances
will also use an exact branch-and-bound solver to report optimality gaps, not only raw bin counts.

Distinctive output: resource-utilisation heatmaps reveal whether a method merely reduces bin count or
also creates balanced, practical packings.

### Task 5 - Concurrent Programming

Implement sequential and parallel merge sort in C++17 over Task 1-style generated records.

- A bounded worker strategy prevents recursive thread explosion.
- Disjoint array ranges avoid locks during local sorting.
- A mutex and condition variable protect the shared work queue.
- Timing includes the same data generation policy and excludes verification/report writing.
- Run with 1, 2, 4, and 8 workers, verify identical sorted output, and plot speedup and efficiency.

Discuss thread creation, queue contention, memory bandwidth, cache effects, merge cost, and Amdahl's
law. Report slowdowns honestly when the input is too small to amortise overhead.

Distinctive output: scalability is measured at several input sizes so the crossover point between
overhead and useful parallelism is visible.

## 4. Repository Layout

```text
.
|-- README.md
|-- PROJECT_PLAN.md
|-- pyproject.toml
|-- src/
|   |-- common/
|   |-- task1_structures/
|   |-- task2_graphs/
|   |-- task3_strategies/
|   `-- task4_heuristics/
|-- task5_concurrency/
|-- tests/
|-- experiments/
|   |-- data/
|   `-- figures/
`-- reports/
```

Generated benchmark CSV files and final figures will be versioned when they provide assessment
evidence. Temporary caches and local build products will be ignored.

## 5. Verification Checklist Per Task

1. Run unit and property/invariant tests.
2. Run a small deterministic demonstration and save readable output.
3. Run benchmark sizes required by the brief.
4. Save raw measurements to CSV.
5. Generate and inspect labelled figures.
6. Compare empirical results with complexity predictions.
7. State limitations, constant-factor effects, and appropriate use cases.
8. Confirm every command works from a clean checkout.

## 6. Incremental Delivery and Commit Plan

Use 30-40 focused commits across the whole coursework. Each commit must represent a meaningful,
reviewable unit and pass the relevant tests.

- Project foundation and methodology: 3 commits.
- Task 1 structures, tests, benchmark, figures, analysis: 7 commits.
- Task 2 representation, three algorithms, traces, comparison: 7 commits.
- Task 3 DP, greedy study, backtracking, comparisons: 7 commits.
- Task 4 heuristics, exact reference, evaluation, visualisation: 5 commits.
- Task 5 sequential/concurrent implementations, benchmarks, analysis: 5 commits.
- Final report integration and reproducibility audit: 3 commits.

Target total: 37 substantive commits. Push after each stable task component so remote history shows
the genuine development progression.

## 7. Delivery Order

1. Repository foundation and reproducibility tools.
2. Task 1 complete.
3. Task 2 complete.
4. Task 3 complete.
5. Task 4 complete.
6. Task 5 complete.
7. Integrated report, references, final clean-check, and reproducibility rerun.

