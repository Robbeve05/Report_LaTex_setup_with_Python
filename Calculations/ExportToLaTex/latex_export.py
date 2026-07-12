from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path


# =============================================================================
# Instellingen
# =============================================================================

# Dit pad is relatief ten opzichte van dit Python-bestand.
# Pas alleen deze variabele aan als je het gegenereerde .tex-bestand ergens
# anders wilt opslaan.
OUTPUT_TEX_RELATIVE_PATH = Path("..") / ".." / "LaTex" / "calculated_values.tex"


@dataclass(frozen=True)
class LatexResult:
    command_name: str
    value: float
    number_format: str

    def formatted_value(self) -> str:
        return format(self.value, self.number_format)


LATEX_COMMAND_NAME_PATTERN = re.compile(r"^[A-Za-z]+$")


def validate_result(result_key: str, result: LatexResult) -> None:
    if not LATEX_COMMAND_NAME_PATTERN.fullmatch(result.command_name):
        raise ValueError(
            f"Ongeldige LaTeX-commandonaam bij resultaat '{result_key}': "
            f"'{result.command_name}'. Gebruik alleen letters en laat de backslash weg."
        )

    if not math.isfinite(result.value):
        raise ValueError(
            f"Ongeldige numerieke waarde bij resultaat '{result_key}' "
            f"({result.command_name}): {result.value}. "
            "NaN en oneindige waarden mogen niet naar LaTeX worden geschreven."
        )


def build_latex_command(result: LatexResult) -> str:
    return rf"\newcommand{{\{result.command_name}}}{{{result.formatted_value()}}}"


def write_latex_file(results: dict[str, LatexResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "% ============================================================================",
        "% AUTOMATISCH GEGENEREERD BESTAND",
        "% Pas dit bestand niet handmatig aan.",
        "% Wijzig de berekeningen in het Python-bestand en voer dat opnieuw uit.",
        "% ============================================================================",
        "",
    ]

    for result_key, result in results.items():
        validate_result(result_key, result)
        lines.append(build_latex_command(result))

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_output_path() -> Path:
    script_dir = Path(__file__).resolve().parent
    return script_dir / OUTPUT_TEX_RELATIVE_PATH


def export_results(results: dict[str, LatexResult]) -> None:
    output_path = get_output_path()
    write_latex_file(results, output_path)
    print(f"LaTeX-waarden geschreven naar: {output_path}")
