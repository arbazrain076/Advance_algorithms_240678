param(
    [int]$Trials = 5,
    [switch]$Quick,
    [string]$Output = "experiments/benchmark_data/task5_benchmarks.csv"
)

$ErrorActionPreference = "Stop"

$sourceFiles = Get-ChildItem -Recurse -Filter *.java task5_concurrency/src |
    Select-Object -ExpandProperty FullName

New-Item -ItemType Directory -Force task5_concurrency/build | Out-Null
javac -Xlint:all -Werror -d task5_concurrency/build $sourceFiles

$arguments = @(
    "-cp", "task5_concurrency/build",
    "coursework.concurrent.Benchmark",
    "--trials", $Trials,
    "--output", $Output
)
if ($Quick) {
    $arguments += "--quick"
}
java $arguments
