"""
Configuración central y utilidades de entorno para Tailnet Panel.
"""
import sys
import os
import shutil
import getpass
from pathlib import Path
from PyQt6.QtCore import QSettings

IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform.startswith("win32")
IS_MACOS = sys.platform == "darwin"

APP_NAME = "Tailnet Panel"
APP_ORG = "TailnetPanelOrg"
VERSION = "1.0.0"

_LEGACY_SETTINGS = ("TailscalePanelOrg", "Tailscale Panel")
_PERSISTED_KEYS = (
    "tailscale_path", "custom_socket", "auto_refresh", "refresh_interval",
    "use_pkexec", "force_no_sudo", "theme",
)

def find_tailscale_binary() -> str:
    """Busca el ejecutable de tailscale en el PATH o en ubicaciones estándar del SO."""
    bin_in_path = shutil.which("tailscale")
    if bin_in_path:
        return bin_in_path

    if IS_LINUX:
        candidates = ["/usr/bin/tailscale", "/usr/local/bin/tailscale", "/opt/tailscale/bin/tailscale"]
    elif IS_MACOS:
        candidates = [
            "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
            "/usr/local/bin/tailscale",
            "/opt/homebrew/bin/tailscale"
        ]
    elif IS_WINDOWS:
        candidates = [
            r"C:\Program Files\Tailscale\tailscale.exe",
            r"C:\Program Files (x86)\Tailscale\tailscale.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Tailscale\tailscale.exe")
        ]
    else:
        candidates = []

    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK if not IS_WINDOWS else os.F_OK):
            return c
    return "tailscale"

class ConfigManager:
    """Gestor persistente de configuraciones de la aplicación."""
    def __init__(self):
        self.settings = QSettings(APP_ORG, APP_NAME)
        previous = QSettings(*_LEGACY_SETTINGS)
        migrated = False
        for key in _PERSISTED_KEYS:
            if not self.settings.contains(key) and previous.contains(key):
                self.settings.setValue(key, previous.value(key))
                migrated = True
        if migrated:
            self.settings.sync()

    @property
    def tailscale_path(self) -> str:
        return self.settings.value("tailscale_path", find_tailscale_binary(), type=str)

    @tailscale_path.setter
    def tailscale_path(self, value: str):
        self.settings.setValue("tailscale_path", value)

    @property
    def custom_socket(self) -> str:
        return self.settings.value("custom_socket", "", type=str)

    @custom_socket.setter
    def custom_socket(self, value: str):
        self.settings.setValue("custom_socket", value)

    @property
    def auto_refresh(self) -> bool:
        return self.settings.value("auto_refresh", True, type=bool)

    @auto_refresh.setter
    def auto_refresh(self, value: bool):
        self.settings.setValue("auto_refresh", value)

    @property
    def refresh_interval(self) -> int:
        return self.settings.value("refresh_interval", 5, type=int)

    @refresh_interval.setter
    def refresh_interval(self, value: int):
        self.settings.setValue("refresh_interval", value)

    @property
    def use_pkexec(self) -> bool:
        """En Linux, preferir pkexec con GUI para elevación si está disponible."""
        return self.settings.value("use_pkexec", True, type=bool)

    @use_pkexec.setter
    def use_pkexec(self, value: bool):
        self.settings.setValue("use_pkexec", value)

    @property
    def force_no_sudo(self) -> bool:
        """Si es True, nunca antepone sudo ni pkexec (ideal para usuarios operadores)."""
        return self.settings.value("force_no_sudo", False, type=bool)

    @force_no_sudo.setter
    def force_no_sudo(self, value: bool):
        self.settings.setValue("force_no_sudo", value)

    @property
    def theme(self) -> str:
        return self.settings.value("theme", "dark", type=str)

    @theme.setter
    def theme(self, value: str):
        self.settings.setValue("theme", value)

config = ConfigManager()

_operator_cache = None


def set_current_user_operator(operator_name: str) -> None:
    """Guarda el resultado de la consulta asíncrona del operador actual."""
    global _operator_cache
    _operator_cache = (
        config.tailscale_path,
        config.custom_socket,
        getpass.getuser(),
        operator_name.strip() == getpass.getuser(),
    )

def is_current_user_operator() -> bool:
    """Lee la última comprobación; nunca bloquea la interfaz con un proceso."""
    return bool(
        _operator_cache
        and _operator_cache[:3] == (config.tailscale_path, config.custom_socket, getpass.getuser())
        and _operator_cache[3]
    )
