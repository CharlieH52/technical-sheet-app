"""Empaquetado de la aplicación con PyInstaller.

Genera un ejecutable ``--onefile --windowed`` en ``dist/``. Incluye los
hiddenimports necesarios para ``pywin32``/``win32com`` y copia los archivos de
configuración de ejemplo junto al ejecutable.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

script_name = "main.py"
output_name = "GENERATE_TECH-SHEET"

HIDDEN_IMPORTS = [
    "win32com.client",
    "win32timezone",
    "pythoncom",
    "pywintypes",
]

DATA_FILES = [
    (".env.example", "."),
]


def build() -> None:
    command_sequence = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--windowed",
        "--onefile",
        "--noconfirm",
        "--clean",
        f"--name={output_name}",
    ]
    for module in HIDDEN_IMPORTS:
        command_sequence.append(f"--hidden-import={module}")
    for source, destination in DATA_FILES:
        command_sequence.append(f"--add-data={source}{os_pathsep()}{destination}")

    command_sequence.append(script_name)
    subprocess.run(command_sequence, check=True)

    # Copiar .env.example junto al ejecutable por si --add-data no lo deja visible.
    dist_dir = Path("dist")
    if dist_dir.exists():
        for source, _ in DATA_FILES:
            src = Path(source)
            if src.exists():
                shutil.copy2(src, dist_dir / src.name)


def os_pathsep() -> str:
    return ";" if sys.platform.startswith("win") else ":"


def clean() -> None:
    for folder in ("build", "__pycache__", "dist"):
        path = Path(folder)
        if path.exists():
            print(f"Eliminando carpeta: {folder}")
            shutil.rmtree(path, ignore_errors=True)

    spec = Path(f"{output_name}.spec")
    if spec.exists():
        print(f"Eliminando archivo: {spec}")
        spec.unlink()


if __name__ == "__main__":
    clean()
    build()
