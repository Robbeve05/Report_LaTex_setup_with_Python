from __future__ import annotations

from dataclasses import dataclass

from latex_export import LatexResult


# Invoer voor deze berekening.
# Deze waarden mogen ook uit een ander Python-bestand, CSV-bestand of meetbestand komen.
MOTOR_CURRENT_A = 2.5
TORQUE_CONSTANT_NM_PER_A = 0.05
PULLEY_RADIUS_M = 0.012


@dataclass(frozen=True)
class MotorResults:
    motor_torque: float
    belt_force: float


def calculate_motor() -> MotorResults:
    motor_torque = MOTOR_CURRENT_A * TORQUE_CONSTANT_NM_PER_A
    belt_force = motor_torque / PULLEY_RADIUS_M

    return MotorResults(
        motor_torque=motor_torque,
        belt_force=belt_force,
    )


def calculate_motor_results() -> dict[str, LatexResult]:
    results = calculate_motor()

    return {
        "motor_torque": LatexResult(
            command_name="MotorTorque",
            value=results.motor_torque,
            number_format=".3f",
        ),
        "belt_force": LatexResult(
            command_name="BeltForce",
            value=results.belt_force,
            number_format=".2f",
        ),
    }
