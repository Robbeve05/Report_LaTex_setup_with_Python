from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import control as ct
import matplotlib
import numpy as np

matplotlib.use("Agg")

import matplotlib.pyplot as plt

CALCULATIONS_DIR = Path(__file__).resolve().parents[1]
LATEX_EXPORT_DIR = CALCULATIONS_DIR / "ExportToLaTex"
sys.path.insert(0, str(LATEX_EXPORT_DIR))

from latex_export import LatexResult


# =============================================================================
# Parameters
# =============================================================================

# Standaard componenten
JM = 9.25e-6  # [kg m^2]
JRED = 8.8e-9

# Arm componenten
ARMEN = 3
M_BALLJOINTS = 0.010

# Bovenarm
M_BOVENARM = 0.120 + M_BALLJOINTS * 2
L_BOVENARM = 0.210

# Onderarm
M_ONDERARM = 0.043 + M_BALLJOINTS * 2
L_ONDERARM_TOTAAL = 0.55
L_ONDERARM_CARBON = 0.475

E_CARBON = 6.5e10
D_OUTER = 0.010
D_INNER = 0.008

# Endeffector
M_ENDEFFECTOR = 0.3

# Overbrengingen
I0 = 47
I1 = 1 / L_BOVENARM
I2 = 1 / L_ONDERARM_TOTAAL

# Regelaarparameters
WB_FACTOR_MOTOR = 0.35
KT = 0.0254
KA = 0.6


@dataclass(frozen=True)
class TwoMassResults:
    inertiamatch: float
    j1: float
    j2: float
    je_motor: float
    k12: float
    war: float
    wr: float
    far: float
    fr: float
    wb_motor: float
    ks: float
    kp: float
    ki: float
    kd: float
    ti: float
    td: float
    tf: float


def calculate_two_mass_system() -> TwoMassResults:
    i_onderarm = math.pi / 64 * (D_OUTER**4 - D_INNER**4)
    k_onderarm = (3 * E_CARBON * i_onderarm) / L_ONDERARM_CARBON**3

    j_bovenarm = 1 / 3 * M_BOVENARM * L_BOVENARM**2
    j_onderarm = (1 / 3 * M_ONDERARM * L_ONDERARM_TOTAAL**2) * 2

    j1 = JM + (JRED + j_bovenarm + (j_onderarm / 2 / I1**2)) / I0**2
    j2 = (j_onderarm / 2 + ((M_ENDEFFECTOR / ARMEN) / I2**2)) / (I1 * I0) ** 2
    k12 = (k_onderarm * 2) / (I1 * I0) ** 2

    je_motor = j1 + j2
    inertiamatch = (j1 + j2 - JM) / JM

    war = math.sqrt(k12 / j2)
    wr = math.sqrt((k12 * (j1 + j2)) / (j1 * j2))

    wb_motor = wr * WB_FACTOR_MOTOR
    mag_motor = abs(ct.evalfr(build_motor_transfer_function(j1, j2, k12), 1j * wb_motor))
    ks = 1 / mag_motor

    kp = ks / (KA * KT)
    ti = 10 / wb_motor
    td = 3 / wb_motor
    tf = 1 / (10 * wb_motor)

    ki = kp / ti
    kd = kp * td

    return TwoMassResults(
        inertiamatch=inertiamatch,
        j1=j1,
        j2=j2,
        je_motor=je_motor,
        k12=k12,
        war=war,
        wr=wr,
        far=war / (2 * math.pi),
        fr=wr / (2 * math.pi),
        wb_motor=wb_motor,
        ks=ks,
        kp=kp,
        ki=ki,
        kd=kd,
        ti=ti,
        td=td,
        tf=tf,
    )


def build_motor_transfer_function(j1: float, j2: float, k12: float) -> ct.TransferFunction:
    numerator = [j2, 0, k12]
    denominator = [j1 * j2, 0, k12 * (j1 + j2), 0, 0]

    return ct.TransferFunction(numerator, denominator)


def build_motor_transfer_function_from_parameters() -> ct.TransferFunction:
    results = calculate_two_mass_system()
    return build_motor_transfer_function(results.j1, results.j2, results.k12)


def build_pid_controller(results: TwoMassResults) -> ct.TransferFunction:
    s = ct.tf([1, 0], [1])
    return results.kp + results.ki / s + results.kd * s / (results.tf * s + 1)


def build_open_loop_transfer_function(results: TwoMassResults) -> ct.TransferFunction:
    g_motor = build_motor_transfer_function(results.j1, results.j2, results.k12)
    c_pid = build_pid_controller(results)

    return KA * KT * c_pid * g_motor


def continuous_phase_deg(response: np.ndarray) -> np.ndarray:
    phase_deg = np.unwrap(np.angle(response)) * 180 / math.pi

    if phase_deg[0] > 0:
        phase_deg -= 360

    phase_deg = np.where(phase_deg > 0, phase_deg - 360, phase_deg)

    return phase_deg


def print_results(results: TwoMassResults) -> None:
    print("--- RESULTATEN 2-MASSASYSTEEM ---\n")

    print("Inertia match:")
    print(f" = {results.inertiamatch:.4e} \n")

    print("Traagheden teruggetransformeerd (motoras):")
    print(f"J1 = {results.j1:.4e} [kg m^2]")
    print(f"J2 = {results.j2:.4e} [kg m^2]\n")

    print("Equivalente traagheid op motoras:")
    print(f"Je_motor = {results.je_motor:.4e} [kg m^2]")

    print("Stijfheid:")
    print(f"K12 = {results.k12:.4f} [Nm/rad]\n")

    print("Frequenties:")
    print(f"Anti-resonantie frequentie (War) = {results.war:.4f} [rad/s]")
    print(f"Resonantie frequentie (Wr)       = {results.wr:.4f} [rad/s]\n")

    print("Frequenties in Hz:")
    print(f"f_ar = {results.far:.2f} [Hz]")
    print(f"f_r  = {results.fr:.2f} [Hz]\n")

    print("--- MOTORREGELAAR ---")
    print(f"Bandbreedte wb = {results.wb_motor:.4f} [rad/s]")
    print(f"Ks = {results.ks:.4e} [-]")
    print(f"Kp = {results.kp:.4e} [V/rad]")
    print(f"Ki = {results.ki:.4e} [V/(rad*s)]")
    print(f"Kd = {results.kd:.4e} [V*s/rad]")
    print(f"Ti = {results.ti:.4e} [s]")
    print(f"Td = {results.td:.4e} [s]")
    print(f"Tf = {results.tf:.4e} [s]")


def save_bode_plot(output_path: Path | None = None) -> Path:
    results = calculate_two_mass_system()
    g_motor = build_motor_transfer_function(results.j1, results.j2, results.k12)

    if output_path is None:
        output_path = CALCULATIONS_DIR / "plots" / "two_mass_bode.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    omega_rad_per_s = np.logspace(0, 5, 5000)
    response = np.array([ct.evalfr(g_motor, 1j * omega) for omega in omega_rad_per_s])

    magnitude_abs = np.abs(response)
    phase_deg = continuous_phase_deg(response)

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    fig.suptitle("Bodeplot motorzijde tweemassamodel")

    axes[0].semilogx(omega_rad_per_s, magnitude_abs, linewidth=1.5)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Magnitude [-]")
    axes[0].grid(True, which="both")

    axes[1].semilogx(omega_rad_per_s, phase_deg, linewidth=1.5)
    axes[1].axhline(-180, color="black", linestyle=":", linewidth=1)
    axes[1].set_xlabel("Angular frequency [rad/s]")
    axes[1].set_ylabel("Phase [deg]")
    axes[1].grid(True, which="both")

    for axis in axes:
        axis.axvline(results.war, color="tab:orange", linestyle="--", linewidth=0.5)
        axis.axvline(results.wr, color="tab:red", linestyle="--", linewidth=0.5)

    axes[0].legend(
        [
            "G_motor",
            f"War = {results.war:.2f} rad/s",
            f"Wr = {results.wr:.2f} rad/s",
        ],
        loc="best",
    )

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close("all")

    return output_path


def save_pid_bode_plot(output_path: Path | None = None) -> Path:
    results = calculate_two_mass_system()
    g_motor = build_motor_transfer_function(results.j1, results.j2, results.k12)
    l_motor = build_open_loop_transfer_function(results)

    if output_path is None:
        output_path = CALCULATIONS_DIR / "plots" / "two_mass_pid_bode.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    omega_rad_per_s = np.logspace(0, 5, 5000)

    motor_response = np.array([ct.evalfr(g_motor, 1j * omega) for omega in omega_rad_per_s])
    loop_response = np.array([ct.evalfr(l_motor, 1j * omega) for omega in omega_rad_per_s])

    motor_magnitude_abs = np.abs(motor_response)
    loop_magnitude_abs = np.abs(loop_response)
    motor_phase_deg = continuous_phase_deg(motor_response)
    loop_phase_deg = continuous_phase_deg(loop_response)

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    fig.suptitle("Bodeplot zonder en met tamme PID")

    axes[0].semilogx(
        omega_rad_per_s,
        motor_magnitude_abs,
        label="Zonder PID: G_motor",
        linewidth=1.5,
    )
    axes[0].semilogx(
        omega_rad_per_s,
        loop_magnitude_abs,
        label="Met tamme PID: Ka Kt C_pid G_motor",
        linewidth=1.5,
    )
    axes[0].axhline(1, color="black", linestyle=":", linewidth=1)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Magnitude [-]")
    axes[0].grid(True, which="both")
    axes[0].legend(loc="best")

    axes[1].semilogx(
        omega_rad_per_s,
        motor_phase_deg,
        label="Zonder PID: G_motor",
        linewidth=1.5,
    )
    axes[1].semilogx(
        omega_rad_per_s,
        loop_phase_deg,
        label="Met tamme PID: Ka Kt C_pid G_motor",
        linewidth=1.5,
    )
    axes[1].axhline(-180, color="black", linestyle=":", linewidth=1)
    axes[1].set_xlabel("Angular frequency [rad/s]")
    axes[1].set_ylabel("Phase [deg]")
    axes[1].grid(True, which="both")
    axes[1].legend(loc="best")

    for axis in axes:
        axis.axvline(results.war, color="tab:orange", linestyle="--", linewidth=0.5)
        axis.axvline(results.wr, color="tab:red", linestyle="--", linewidth=0.5)

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close("all")

    return output_path


def calculate_two_mass_results() -> dict[str, LatexResult]:
    results = calculate_two_mass_system()

    return {
        "two_mass_inertiamatch": LatexResult(
            command_name="TwoMassInertiamatch",
            value=results.inertiamatch,
            number_format=".4e",
        ),
        "two_mass_j1": LatexResult(
            command_name="TwoMassJone",
            value=results.j1,
            number_format=".4e",
        ),
        "two_mass_j2": LatexResult(
            command_name="TwoMassJtwo",
            value=results.j2,
            number_format=".4e",
        ),
        "two_mass_je_motor": LatexResult(
            command_name="TwoMassJeMotor",
            value=results.je_motor,
            number_format=".4e",
        ),
        "two_mass_k12": LatexResult(
            command_name="TwoMassStiffness",
            value=results.k12,
            number_format=".4f",
        ),
        "two_mass_war": LatexResult(
            command_name="TwoMassAntiResonanceAngularFrequency",
            value=results.war,
            number_format=".4f",
        ),
        "two_mass_wr": LatexResult(
            command_name="TwoMassResonanceAngularFrequency",
            value=results.wr,
            number_format=".4f",
        ),
        "two_mass_far": LatexResult(
            command_name="TwoMassAntiResonanceFrequency",
            value=results.far,
            number_format=".2f",
        ),
        "two_mass_fr": LatexResult(
            command_name="TwoMassResonanceFrequency",
            value=results.fr,
            number_format=".2f",
        ),
        "two_mass_kp": LatexResult(
            command_name="TwoMassMotorKp",
            value=results.kp,
            number_format=".4e",
        ),
        "two_mass_ki": LatexResult(
            command_name="TwoMassMotorKi",
            value=results.ki,
            number_format=".4e",
        ),
        "two_mass_kd": LatexResult(
            command_name="TwoMassMotorKd",
            value=results.kd,
            number_format=".4e",
        ),
    }


def main() -> None:
    results = calculate_two_mass_system()
    print_results(results)

    motor_bode_path = save_bode_plot()
    pid_bode_path = save_pid_bode_plot()
    print(f"\nBodeplot motorplant opgeslagen naar: {motor_bode_path}")
    print(f"Bodeplot PID/open-loop opgeslagen naar: {pid_bode_path}")


if __name__ == "__main__":
    main()
