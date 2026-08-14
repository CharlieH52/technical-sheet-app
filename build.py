import subprocess
import os

script_name = "main.py"
output_name = "GENERATE_TECH-SHEET"


def build():
    command_sequence = [
        "pyinstaller",
        "--windowed",
        "--onefile",
        f"--name={output_name}",
        "--clean",
        script_name
    ]
    
    subprocess.run(command_sequence)

def clean():
    for folder in ["build", "__pycache__"]:
        if os.path.exists(folder):
            print(f"Eliminando carpeta: {folder}")
            subprocess.run(["rm", "-rf", folder], shell=True)

    if os.path.exists("main.spec"):
        print("Eliminando archivo: main.spec")
        os.remove("main.spec")

if __name__ == "__main__":
    clean()
    build()