$ErrorActionPreference = "Stop"

$sourceFiles = Get-ChildItem -Recurse -Filter *.java `
    task5_concurrency/src, task5_concurrency/test |
    Select-Object -ExpandProperty FullName

New-Item -ItemType Directory -Force task5_concurrency/build | Out-Null
javac -Xlint:all -Werror -d task5_concurrency/build $sourceFiles
java -cp task5_concurrency/build coursework.concurrent.ParallelMergeSortTest
