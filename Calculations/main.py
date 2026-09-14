from __future__ import annotations

import sys
from pathlib import Path


CALCULATIONS_DIR = Path(__file__).resolve().parent
PYTHON_CALCULATION_DIR = CALCULATIONS_DIR / ".py"
LATEX_EXPORT_DIR = CALCULATIONS_DIR / "ExportToLaTex"

sys.path.insert(0, str(PYTHON_CALCULATION_DIR))
sys.path.insert(0, str(LATEX_EXPORT_DIR))

from latex_export import LatexResult, export_results
from motor_calculation import calculate_motor_results
from two_mass_system import calculate_two_mass_results


def collect_results() -> dict[str, LatexResult]:
    results = {}

    results.update(calculate_motor_results())
    results.update(calculate_two_mass_results())

    return results


def main() -> None:
    export_results(collect_results())


if __name__ == "__main__":
    main()
