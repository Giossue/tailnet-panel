"""Build Linux packages from a PyInstaller binary built on the oldest target glibc."""

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sysconfig
from importlib import metadata
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer

from app.config import VERSION


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
STAGING = DIST / "release-staging"
APPDIR = DIST / "TailnetPanel.AppDir"
LICENSE_PACKAGES = ("PyQt6", "PyQt6-Qt6", "PyQt6-sip", "QtAwesome", "QtPy", "PyInstaller")


def copy_wheel_licenses(destination: Path) -> None:
    """Copy the license shipped by each bundled wheel, using the installed version."""
    destination.mkdir(parents=True, exist_ok=True)
    for package in LICENSE_PACKAGES:
        distribution = metadata.distribution(package)
        found = False
        for entry in distribution.files or ():
            if ".dist-info" not in str(entry) or not entry.name.upper().startswith(("LICENSE", "COPYING")):
                continue
            source = Path(distribution.locate_file(entry))
            if source.is_file():
                target = destination / f"{package}-{distribution.version}-{entry.name}"
                shutil.copy2(source, target)
                found = True
        if not found:
            raise RuntimeError(f"No license file found for {package} {distribution.version}")
    python_license = Path(sysconfig.get_path("stdlib")) / "LICENSE.txt"
    if python_license.is_file():
        shutil.copy2(python_license, destination / "Python-LICENSE")
    else:
        raise RuntimeError("Python license file not found")
    for source in (ROOT / "packaging" / "licenses").glob("*"):
        shutil.copy2(source, destination / source.name)


def render_icon(destination: Path) -> None:
    renderer = QSvgRenderer(str(ROOT / "app" / "assets" / "panel-mark.svg"))
    if not renderer.isValid():
        raise RuntimeError("Invalid application SVG icon")
    canvas = QImage(256, 256, QImage.Format.Format_ARGB32)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    renderer.render(painter)
    painter.end()
    if not canvas.save(str(destination), "PNG"):
        raise RuntimeError("Could not render application icon")


def prepare_staging() -> None:
    executable = DIST / "TailnetPanel"
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise RuntimeError("Build dist/TailnetPanel with build_executable.py first")
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("This release recipe currently targets Linux x86_64 only")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    shutil.copy2(executable, STAGING / "tailnet-panel")
    render_icon(STAGING / "tailnet-panel.png")
    copy_wheel_licenses(STAGING / "licenses")


def build_appdir() -> None:
    if APPDIR.exists():
        shutil.rmtree(APPDIR)
    (APPDIR / "usr" / "bin").mkdir(parents=True)
    docs = APPDIR / "usr" / "share" / "doc" / "tailnet-panel"
    docs.mkdir(parents=True)
    shutil.copy2(STAGING / "tailnet-panel", APPDIR / "usr" / "bin" / "tailnet-panel")
    shutil.copy2(ROOT / "packaging" / "tailnet-panel.desktop", APPDIR / "tailnet-panel.desktop")
    shutil.copy2(STAGING / "tailnet-panel.png", APPDIR / "tailnet-panel.png")
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(ROOT / name, docs / name)
    shutil.copy2(ROOT / "packaging" / "SOURCE.txt", docs / "SOURCE.txt")
    helper_dir = APPDIR / "usr" / "share" / "tailnet-panel"
    helper_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "configure_passwordless_tailscale.py", helper_dir / "configure_passwordless_tailscale.py")
    shutil.copytree(STAGING / "licenses", docs / "licenses")
    apprun = APPDIR / "AppRun"
    apprun.write_text(
        '#!/bin/sh\nAPPDIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"\n'
        'exec "$APPDIR/usr/bin/tailnet-panel" "$@"\n',
        encoding="utf-8",
    )
    apprun.chmod(0o755)


def build_source_archive() -> Path:
    output = DIST / f"tailnet-panel-{VERSION}-source.tar.gz"
    subprocess.run(
        ["git", "-c", f"safe.directory={ROOT}", "archive", "--format=tar.gz", f"--prefix=tailnet-panel-{VERSION}/", "-o", str(output), "HEAD"],
        cwd=ROOT,
        check=True,
    )
    return output


def write_checksums(artifacts: list[Path]) -> None:
    lines = []
    for artifact in artifacts:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        lines.append(f"{digest}  {artifact.name}")
    (DIST / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nfpm", default="nfpm", help="path to nFPM binary")
    parser.add_argument("--appimagetool", default="appimagetool", help="path to appimagetool AppImage")
    args = parser.parse_args()
    prepare_staging()
    build_appdir()
    env = os.environ.copy()
    env["VERSION"] = VERSION
    env["ARCH"] = "x86_64"
    artifacts = []
    for packager, filename in (
        ("deb", f"tailnet-panel_{VERSION}_amd64.deb"),
        ("rpm", f"tailnet-panel-{VERSION}-1.x86_64.rpm"),
        ("archlinux", f"tailnet-panel-{VERSION}-1-x86_64.pkg.tar.zst"),
    ):
        target = DIST / filename
        subprocess.run(
            [args.nfpm, "package", "-f", "packaging/nfpm.yaml", "-p", packager, "-t", str(target)],
            cwd=ROOT,
            env=env,
            check=True,
        )
        artifacts.append(target)
    appimage = DIST / f"Tailnet-Panel-{VERSION}-x86_64.AppImage"
    subprocess.run(
        [args.appimagetool, "--appimage-extract-and-run", str(APPDIR), str(appimage)],
        cwd=ROOT,
        env=env,
        check=True,
    )
    artifacts.append(appimage)
    artifacts.append(build_source_archive())
    write_checksums(artifacts)
    for artifact in artifacts:
        print(f"{artifact.name}: {artifact.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
