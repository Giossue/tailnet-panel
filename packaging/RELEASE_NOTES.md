# Tailnet Panel 1.0.0

Instaladores Linux para **x86_64**. Compilados en Debian 12 (glibc 2.36) para distribuciones compatibles con esa versión o una posterior. Tailscale se instala por separado; abre el panel con tu usuario normal.

| Distribuciones | Archivo | Instalación |
| --- | --- | --- |
| Debian 12+, Ubuntu 24.04+ y derivadas | `.deb` | `sudo apt install ./tailnet-panel_1.0.0_amd64.deb` |
| Fedora y otras con RPM compatible | `.rpm` | `sudo dnf install ./tailnet-panel-1.0.0-1.x86_64.rpm` |
| Arch y derivadas | `.pkg.tar.zst` | `sudo pacman -U ./tailnet-panel-1.0.0-1-x86_64.pkg.tar.zst` |
| Otras distribuciones con glibc 2.36+ | `.AppImage` | `chmod +x Tailnet-Panel-1.0.0-x86_64.AppImage && ./Tailnet-Panel-1.0.0-x86_64.AppImage` |

Comprueba las descargas con `sha256sum -c SHA256SUMS.txt`. Se adjunta el código fuente de esta versión. [Avisos y licencias de terceros](https://github.com/Giossue/tailnet-panel/blob/v1.0.0/THIRD_PARTY_NOTICES.md).
La AppImage requiere `libGL.so.1`, `libEGL.so.1` y fuentes de escritorio instaladas en el sistema.

---

Linux x86_64 installers, built on Debian 12 for distributions with glibc 2.36 or newer. Install Tailscale separately and launch the panel as your regular user. SHA-256 checksums and the matching source archive are attached.
The AppImage requires system `libGL.so.1`, `libEGL.so.1`, and desktop fonts.
