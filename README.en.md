# Tailnet Panel

[Español](README.md)

Tailnet Panel is a desktop interface built with PyQt6 for the Tailscale command line tool. It is an independent community project and is not affiliated with or endorsed by Tailscale Inc.

The panel groups 115 entries from the [command catalog](comandos.md) into focused views and a searchable catalog. Command availability depends on the installed Tailscale version and operating system. Tailscale itself is an external prerequisite and is not bundled with this project.

The source has been tested on Linux with Python 3.14. Windows and macOS launch paths are provided, but neither platform has been verified in CI yet.

| Light theme | Dark theme |
| --- | --- |
| ![Panel with sample data in the light theme](docs/screenshots/light.png) | ![Panel with sample data in the dark theme](docs/screenshots/dark.png) |

The screenshots use fictional data.

## What the panel provides

- Status, peers, accounts, exit nodes, files, Serve and Funnel, diagnostics, preferences, and other Tailscale commands in dedicated views.
- Light and dark themes, responsive controls, a collapsible command console, and system tray actions.
- Asynchronous status queries and command execution so the interface remains responsive.
- Auth keys hidden from previews, the console, and history. For `login` and `up`, the key is passed to the CLI through a temporary private file, which is removed when the process ends.
- A configurable Tailscale executable path, custom socket, and refresh interval.

## Requirements

- Python 3.10 or newer. Linux has been tested with Python 3.14.
- Tailscale installed, with its CLI available on `PATH` or at a path selected in the panel.

## Linux installers

Download packages from the [latest release](https://github.com/Giossue/tailnet-panel/releases). They target **x86_64**, are built on Debian 12, and require **glibc 2.36 or newer**. The matching source archive and `SHA256SUMS.txt` are attached.

| Distribution | File | Install |
| --- | --- | --- |
| Debian 12+, Ubuntu 24.04+ and derivatives | `.deb` | `sudo apt install ./tailnet-panel_1.0.0_amd64.deb` |
| Fedora and RPM compatible distributions | `.rpm` | `sudo dnf install ./tailnet-panel-1.0.0-1.x86_64.rpm` |
| Arch and derivatives | `.pkg.tar.zst` | `sudo pacman -U ./tailnet-panel-1.0.0-1-x86_64.pkg.tar.zst` |
| Other compatible distributions | `.AppImage` | `chmod +x Tailnet-Panel-1.0.0-x86_64.AppImage && ./Tailnet-Panel-1.0.0-x86_64.AppImage` |

After installing a native package, launch **Tailnet Panel** from the application menu or run `tailnet-panel`. Install Tailscale separately and use the panel as your regular user.
The AppImage also needs the system graphics libraries `libGL.so.1` and `libEGL.so.1` and desktop fonts; native packages declare these dependencies.

Run these commands from the project directory.

### Linux and macOS

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
./run.sh
```

### Windows

In PowerShell or CMD:

```bat
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run.bat
```

Recreate the virtual environment if you move the project directory.

## Linux permissions

Tailscale runs a privileged daemon. To manage supported daemon operations from your regular account, register that account as a Tailscale operator once:

```bash
sudo tailscale set --operator="$USER"
tailscale get operator
```

You can also use **Habilitar permisos** (Enable permissions) on the panel's main screen. Restart the panel afterward. Operations that modify the Tailscale installation or the operating system may still request authorization. Run the panel as your regular user.

## Linux desktop launcher

After installing dependencies, register a launcher for your user:

```bash
python3 install_desktop.py
```

The script uses the project's current location and replaces this project's previous launcher. Run it again if you move the directory. Remove the launcher with `python3 install_desktop.py --uninstall`.

## Tests

Run the automated tests on Linux without opening a window:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

`test_app.py` additionally makes read-only queries against a local Tailscale installation; it is not run in CI.

## Build an executable

Build on the operating system you intend to distribute for. PyInstaller does not cross-compile:

```bash
python -m pip install -r requirements-build.txt
python build_executable.py
```

The result is written to `dist/`. Tailscale must still be installed on the destination computer. On Linux, build on the oldest distribution you intend to support because [PyInstaller does not bundle glibc](https://www.pyinstaller.org/en/stable/usage.html#making-gnu-linux-apps-forward-compatible). A Linux build has been verified; Windows and macOS builds need their own testing before binary release.

When distributing binaries, include the corresponding source and the required [third-party license notices](THIRD_PARTY_NOTICES.md).

## Contributing, security, and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance and [SECURITY.md](SECURITY.md) for reporting sensitive issues. Do not share auth keys, private tailnet details, or unredacted screenshots in issues.

Tailnet Panel's code is licensed under [GPL-3.0-only](LICENSE). Dependencies and third-party marks have their own terms, summarized in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
