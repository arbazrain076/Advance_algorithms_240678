$ErrorActionPreference = "Stop"

$env:PYTHONPATH = "src"
python -m compileall -q src tests experiments scripts
python -m unittest discover -s tests -p "test_*.py" -v
powershell -NoProfile -ExecutionPolicy Bypass -File task5_concurrency/run_tests.ps1
python scripts/verify_artifacts.py

Write-Output "All project checks passed."
