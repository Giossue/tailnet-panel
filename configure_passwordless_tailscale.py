"""Opt-in, per-user passwordless sudo access to the installed Tailscale CLI.

Run this script with sudo after reviewing the resulting privilege scope. The
application itself continues to run as the regular desktop user.
"""

import argparse
import os
import pwd
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


SUDOERS_DIR = Path("/etc/sudoers.d")
MANAGED_MARKER = "# Managed by Tailnet Panel; permits all Tailscale CLI arguments."


def valid_user(name: str) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", name):
        raise ValueError("El nombre de usuario contiene caracteres no admitidos.")
    account = pwd.getpwnam(name)
    if account.pw_uid == 0:
        raise ValueError("El acceso sin contraseña debe pertenecer a un usuario normal.")
    return name


def valid_tailscale_path(value: str) -> str:
    path = Path(value)
    if not path.is_absolute() or not re.fullmatch(r"/[a-zA-Z0-9_./+-]+", value):
        raise ValueError("La ruta de Tailscale debe ser absoluta y apta para sudoers.")
    target = path.resolve(strict=True)
    for entry in (target, *target.parents):
        info = entry.stat()
        if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise ValueError("Tailscale y sus directorios deben pertenecer a root y no ser editables por otros.")
    if not target.is_file() or not os.access(target, os.X_OK):
        raise ValueError("La ruta indicada no es un ejecutable.")
    return str(target)


def managed_file(username: str) -> Path:
    return SUDOERS_DIR / f"tailnet-panel-{username}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default=os.environ.get("SUDO_USER", ""))
    parser.add_argument("--tailscale-path", default=shutil.which("tailscale") or "")
    parser.add_argument("--remove", action="store_true", help="quitar la regla instalada por este script")
    args = parser.parse_args()

    if os.geteuid() != 0:
        parser.error("Ejecuta este script una vez con sudo o pkexec.")
    try:
        username = valid_user(args.user)
    except (ValueError, KeyError) as error:
        parser.error(str(error))

    destination = managed_file(username)
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or not destination.read_text(encoding="utf-8").startswith(MANAGED_MARKER):
            parser.error(f"No se modificó {destination}: no pertenece a este instalador.")
    if args.remove:
        if destination.exists():
            destination.unlink()
        print(f"Acceso sin contraseña eliminado para {username}.")
        return 0

    try:
        tailscale_path = valid_tailscale_path(args.tailscale_path)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    visudo = shutil.which("visudo")
    if not visudo:
        parser.error("No se encontró visudo; instala el paquete sudo antes de continuar.")

    content = f"{MANAGED_MARKER}\n{username} ALL=(root) NOPASSWD: {tailscale_path}\n"
    fd, temporary_name = tempfile.mkstemp(prefix=".tailnet-panel-", dir=SUDOERS_DIR)
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, 0o440)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        check = subprocess.run([visudo, "-cf", str(temporary)], capture_output=True, text=True)
        if check.returncode != 0:
            raise RuntimeError(f"visudo rechazó la regla: {check.stderr.strip()}")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)

    print(f"Acceso sin contraseña activado para {username} en {tailscale_path}.")
    script = shlex.quote(str(Path(__file__).resolve()))
    print(f"Para revertirlo: sudo python3 {script} --user {username} --remove")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
