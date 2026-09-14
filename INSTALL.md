# Install Guide

This guide explains how to install the Python libraries used by the calculation
setup.

## 1. Install Python

Install Python 3.11 or newer from:

https://www.python.org/downloads/

During installation, enable:

```text
Add python.exe to PATH
```

Check the installation in PowerShell:

```powershell
python --version
pip --version
```

## 2. Open the project folder

Open PowerShell in the root folder of this project:

```powershell
cd "C:\Users\robbe\OneDrive - Avans Hogeschool\Report_LaTex_setup_with_Python"
```

## 3. Create a virtual environment

A virtual environment keeps the libraries for this project separate from other
Python projects.

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script with this error:

```text
cannot be loaded because running scripts is disabled on this system
```

then PowerShell is blocking local scripts. This is not a Python problem. Allow
local scripts for the current Windows user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

When PowerShell asks for confirmation, type:

```powershell
Y
```

Then run the activation command again:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the PowerShell line should start with `(.venv)`.

Alternative without changing the PowerShell execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r Calculations\requirements.txt
```

This uses the Python installation inside `.venv` directly, without activating
the virtual environment first.

## 4. Install the libraries

Install all required libraries from `Calculations/requirements.txt`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r Calculations\requirements.txt
```

The file currently installs:

- `numpy` for matrix, vector and numerical calculations.
- `scipy` for optimisation, ODEs and signal processing.
- `matplotlib` for plots and graphs.
- `pandas` for measurement data, CSV files and Excel analysis.
- `sympy` for symbolic calculations.
- `control` for transfer functions, state-space models and Bode plots.
- `pint` for calculations with physical units.
- `pyserial` for communication with hardware over serial ports.

## 5. Check the installation

Run this command from the project root:

```powershell
python -c "import numpy, scipy, matplotlib, pandas, sympy, control, pint, serial; print('Libraries installed')"
```

If it prints `Libraries installed`, the Python libraries are ready.

## 6. Select the virtual environment in VS Code

If VS Code gives an error such as:

```text
ModuleNotFoundError: No module named 'control'
```

then VS Code is probably using the wrong Python interpreter. The libraries are
installed in `.venv`, so VS Code must also run that Python version.

In VS Code:

1. Press `Ctrl+Shift+P`.
2. Search for `Python: Select Interpreter`.
3. Select:

```text
.venv\Scripts\python.exe
```

The selected interpreter should point to this project folder, not to a global
Python installation such as:

```text
C:\Users\robbe\AppData\Local\Python\...
```

This project also contains `.vscode/settings.json`, which tells VS Code to use
the `.venv` interpreter by default when the full project folder is opened.

If you open `Calculations/Calculation Workspace.code-workspace`, the workspace
settings point one folder back to:

```text
..\.venv\Scripts\python.exe
```

## 7. Run the calculation export

Run:

```powershell
python Calculations\main.py
```

This updates:

```text
LaTex\calculated_values.tex
```

The generated file is loaded by the LaTeX report and should not be edited by
hand.

## Optional: LaTeX installation

To compile the report PDF, install a LaTeX distribution such as MiKTeX:

https://miktex.org/download

After installing MiKTeX, open `LaTex/report.tex` in your LaTeX editor or compile
it from the command line if your editor provides a LaTeX compiler.
