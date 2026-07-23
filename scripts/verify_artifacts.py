"""Repository-wide validation for generated evidence and local Markdown links."""

from __future__ import annotations

import csv
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CSV_ROWS = {
    "task1_benchmarks.csv": 480,
    "task2_benchmarks.csv": 90,
    "task3_experiments.csv": 125,
    "task4_experiments.csv": 75,
    "task5_benchmarks.csv": 75,
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def verify_csv_files() -> None:
    data_directory = ROOT / "experiments" / "data"
    for filename, expected_rows in EXPECTED_CSV_ROWS.items():
        path = data_directory / filename
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        require(len(rows) == expected_rows, f"{filename}: expected {expected_rows} rows")
        require(rows and all(rows[0]), f"{filename}: missing header name")
        if filename == "task5_benchmarks.csv":
            require(
                all(row["correct"].lower() == "true" for row in rows),
                "Task 5 contains an incorrect sort result",
            )


def verify_figures() -> None:
    figures = sorted((ROOT / "experiments" / "figures").glob("*.svg"))
    require(len(figures) == 18, "expected 18 SVG figures")
    svg_namespace = "{http://www.w3.org/2000/svg}"
    for path in figures:
        root = ET.parse(path).getroot()
        require(root.tag == f"{svg_namespace}svg", f"{path.name}: invalid SVG root")
        require(root.find(f"{svg_namespace}title") is not None, f"{path.name}: missing title")
        require(root.find(f"{svg_namespace}desc") is not None, f"{path.name}: missing description")


def verify_markdown_links() -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            target = target.split("#", 1)[0].strip("<>")
            if not target or re.match(r"^[a-z]+://", target, re.IGNORECASE):
                continue
            require((path.parent / target).resolve().exists(), f"{path}: broken link {target}")


def verify_integrated_word_count() -> None:
    report = (ROOT / "reports" / "final_report.md").read_text(encoding="utf-8")
    main_text = report.split("## References", 1)[0]
    words = re.findall(r"\b[\w-]+\b", main_text)
    require(1_800 <= len(words) <= 2_100, f"integrated report word count is {len(words)}")
    print(f"Integrated report main-text word count: {len(words)}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    verify_csv_files()
    verify_figures()
    verify_markdown_links()
    verify_integrated_word_count()
    print("Artifact, link, and evidence checks: passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        raise
