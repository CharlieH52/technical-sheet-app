import shutil
import subprocess
import sys
from pathlib import Path

script_name = "main.py"
output_name = "GENERATE_TECH-SHEET"


def build() -> None:
    command_sequence = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--windowed",
        "--onefile",
        "--noconfirm",
        f"--name={output_name}",
        "--clean",
        script_name,
    ]
    subprocess.run(command_sequence, check=True)


def clean() -> None:
    for folder in ("build", "__pycache__"):
        path = Path(folder)
        if path.exists():
            print(f"Eliminando carpeta: {folder}")
            shutil.rmtree(path, ignore_errors=True)

    spec = Path("main.spec")
    if spec.exists():
        print("Eliminando archivo: main.spec")
        spec.unlink()


if __name__ == "__main__":
    clean()
    build()
