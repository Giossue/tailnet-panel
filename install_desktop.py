"""Registra un acceso directo local en escritorios Linux compatibles con XDG."""

import argparse
import os
from pathlib import Path

from app.config import APP_NAME


PROJECT_ROOT = Path(__file__).resolve().parent


def desktop_exec_path(path: Path) -> str:
    """Codifica la ruta de Exec según la especificación Desktop Entry."""
    value = str(path).replace("\\", "\\\\\\\\")
    for character in ('"', '`', '$'):
        value = value.replace(character, "\\" + character)
    return '"' + value.replace("%", "%%") + '"'


def desktop_entry() -> str:
    launcher = PROJECT_ROOT / "run.sh"
    icon = PROJECT_ROOT / "app" / "assets" / "panel-mark.svg"
    return (
        "[Desktop Entry]\n"
        f"Name={APP_NAME}\n"
        "Comment=Panel comunitario para la CLI de Tailscale\n"
        f"Exec={desktop_exec_path(launcher)}\n"
        f"TryExec={launcher}\n"
        f"Icon={icon}\n"
        "Terminal=false\n"
        "Type=Application\n"
        "Categories=Network;\n"
    )


def destination() -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "applications" / (APP_NAME.lower().replace(" ", "-") + ".desktop")


def remove_legacy_launcher(target: Path) -> None:
    """Retira el acceso directo anterior solo si pertenece a este proyecto."""
    legacy = target.with_name("tailscale-panel.desktop")
    if not legacy.is_file():
        return
    lines = legacy.read_text(encoding="utf-8").splitlines()
    launcher = str(PROJECT_ROOT / "run.sh")
    if "Name=Tailscale Panel" in lines and any(
        line.startswith("Exec=") and launcher in line for line in lines
    ):
        legacy.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print", action="store_true", dest="print_only", help="mostrar sin instalar")
    parser.add_argument("--uninstall", action="store_true", help="quitar el acceso directo")
    args = parser.parse_args()
    if args.print_only:
        print(desktop_entry(), end="")
        return
    target = destination()
    if args.uninstall:
        target.unlink(missing_ok=True)
        remove_legacy_launcher(target)
        print(f"Acceso directo quitado: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(desktop_entry(), encoding="utf-8")
    remove_legacy_launcher(target)
    print(f"Acceso directo instalado: {target}")


if __name__ == "__main__":
    main()
