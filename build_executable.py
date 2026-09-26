"""Construye un ejecutable para el sistema operativo actual con PyInstaller."""

import importlib.util
import subprocess
import sys
from pathlib import Path

from app.config import APP_NAME


PROJECT_ROOT = Path(__file__).resolve().parent


def build_command() -> list[str]:
    name = APP_NAME.replace(" ", "")
    return [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--windowed",
        f"--name={name}",
        f"--paths={PROJECT_ROOT}",
        f"--add-data={PROJECT_ROOT / 'app' / 'assets'}:app/assets",
        "--collect-data=qtawesome",
        str(PROJECT_ROOT / "app" / "main.py"),
    ]


def main() -> None:
    if importlib.util.find_spec("PyInstaller") is None:
        raise SystemExit(
            "Falta PyInstaller. Instala requirements-build.txt en un entorno virtual "
            "y vuelve a ejecutar este script."
        )
    subprocess.run(build_command(), cwd=PROJECT_ROOT, check=True)
    print(f"Ejecutable generado en {PROJECT_ROOT / 'dist'}")


if __name__ == "__main__":
    main()
