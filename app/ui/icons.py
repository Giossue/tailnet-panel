"""
Gestor centralizado de íconos para Tailnet Panel con soporte para QtAwesome y fallback vectorial.
"""
from functools import lru_cache
from typing import Optional
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QRectF
from app.config import config
from app.ui.theme import get_theme_colors

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    qta = None
    HAS_QTAWESOME = False

# Mapeo de nombres semánticos a nombres de íconos de QtAwesome (FontAwesome 6 Solid)
ICON_MAP = {
    # Vistas y navegación
    "dashboard": "fa6s.gauge-high",
    "preferences": "fa6s.sliders",
    "exit-node": "fa6s.shield-halved",
    "diagnostics": "fa6s.network-wired",
    "serve": "fa6s.server",
    "files": "fa6s.folder-open",
    "ssh": "fa6s.terminal",
    "security": "fa6s.lock",
    "accounts": "fa6s.users",
    "appc": "fa6s.diagram-project",
    "system": "fa6s.gears",
    "catalog": "fa6s.book-bookmark",

    # Acciones comunes
    "refresh": "fa6s.rotate",
    "connect": "fa6s.bolt",
    "disconnect": "fa6s.power-off",
    "copy": "fa6s.copy",
    "search": "fa6s.magnifying-glass",
    "clean": "fa6s.broom",
    "trash": "fa6s.trash-can",
    "cancel": "fa6s.circle-xmark",
    "web": "fa6s.globe",
    "user": "fa6s.circle-user",
    "users": "fa6s.users",
    "device": "fa6s.laptop",
    "settings": "fa6s.gear",
    "tailscale": "fa6s.network-wired",
    "key": "fa6s.key",
    "file": "fa6s.file",
    "folder": "fa6s.folder",
    "folder-open": "fa6s.folder-open",
    "devices": "fa6s.laptop-file",
    "upload": "fa6s.cloud-arrow-up",
    "download": "fa6s.cloud-arrow-down",
    "share": "fa6s.share-nodes",
    "edit": "fa6s.pen-to-square",
    "ping": "fa6s.table-tennis-paddle-ball",
    "netcat": "fa6s.plug",
    "dns": "fa6s.compass",
    "metrics": "fa6s.chart-simple",
    "bugreport": "fa6s.bug",
    "cert": "fa6s.certificate",
    "routes": "fa6s.route",
    "update": "fa6s.arrows-rotate",
    "version": "fa6s.tag",
    "license": "fa6s.scale-balanced",
    "wait": "fa6s.hourglass-half",
    "switch": "fa6s.arrow-right-arrow-left",
    "logout": "fa6s.arrow-right-from-bracket",
    "shield": "fa6s.shield-halved",
    "shield-on": "fa6s.shield",
    "check": "fa6s.circle-check",
    "times": "fa6s.circle-xmark",
    "info": "fa6s.circle-info",
    "star": "fa6s.star",
    "rocket": "fa6s.rocket",
    "lock": "fa6s.lock",
    "lock-open": "fa6s.lock-open",
    "globe": "fa6s.globe",
    "play": "fa6s.play",
    "flask": "fa6s.flask",
    "bolt": "fa6s.bolt",
    "server": "fa6s.server",
    "terminal": "fa6s.terminal",
    "sync": "fa6s.arrows-rotate",
    "warning": "fa6s.triangle-exclamation",
    "chevron-down": "fa6s.chevron-down",
    "chevron-up": "fa6s.chevron-up",
    "chevron-left": "fa6s.chevron-left",
    "chevron-right": "fa6s.chevron-right",
    "arrow-up": "fa6s.arrow-up",
    "folder-plus": "fa6s.folder-plus",
    "list": "fa6s.list",
    "list-detail": "fa6s.table-list",
    "map": "fa6s.map",
    "list-ol": "fa6s.list-ol",
    "sun": "fa6s.sun",
    "moon": "fa6s.moon",
    "ellipsis": "fa6s.ellipsis"
}

def icon_color(role: str = "default", state: str = "normal") -> str:
    c = get_theme_colors(config.theme)
    if state == "disabled":
        return c["icon_disabled"]
    if role == "primary":
        return "#ffffff"
    if role == "danger":
        return "#ffffff" if state in ("active", "pressed") else c["danger"]
    if role == "accent":
        return c["accent"]
    if role == "warning":
        return c["warning"]
    return c["icon_hover"] if state == "active" else c["icon"]


@lru_cache(maxsize=256)
def _render_icon(name: str, color: str) -> QIcon:
    if HAS_QTAWESOME and qta is not None:
        qta_name = ICON_MAP.get(name, name)
        try:
            return qta.icon(qta_name, color=color)
        except Exception:
            pass
    return _create_fallback_icon(name, color)


@lru_cache(maxsize=512)
def _build_icon(name: str, normal: str, active: str, disabled: str) -> QIcon:
    """Rasteriza los estados Qt una vez, sin depender de un engine Python."""
    icon = QIcon()
    for size in (16, 20, 24, 32):
        icon.addPixmap(_render_icon(name, normal).pixmap(size, size), QIcon.Mode.Normal)
        icon.addPixmap(_render_icon(name, active).pixmap(size, size), QIcon.Mode.Active)
        icon.addPixmap(_render_icon(name, active).pixmap(size, size), QIcon.Mode.Selected)
        icon.addPixmap(_render_icon(name, disabled).pixmap(size, size), QIcon.Mode.Disabled)
    return icon


def get_icon(name: str, color: Optional[str] = None,
             active_color: Optional[str] = None, role: str = "default") -> QIcon:
    """Ícono semántico para el tema actual, con estados normal/hover/deshabilitado."""
    normal = color or icon_color(role, "normal")
    active = active_color or color or icon_color(role, "active")
    disabled = icon_color(role, "disabled")
    return _build_icon(name, normal, active, disabled)

def _create_fallback_icon(name: str, color_hex: str) -> QIcon:
    """Crea un ícono nítido de 64x64 usando dibujo vectorial con QPainter."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    color = QColor(color_hex)
    painter.setPen(QPen(color, 4))
    painter.setBrush(QBrush(color.lighter(130)))

    if name in ("tailscale", "diagnostics", "connect", "routes", "appc"):
        painter.setBrush(QBrush(color))
        painter.drawEllipse(12, 32, 12, 12)
        painter.drawEllipse(40, 16, 12, 12)
        painter.drawEllipse(40, 44, 12, 12)
        painter.drawLine(24, 38, 40, 22)
        painter.drawLine(24, 38, 40, 50)
    elif name in ("security", "exit-node", "shield", "shield-on"):
        painter.drawRoundedRect(16, 12, 32, 40, 6, 6)
    elif name in ("ssh", "system", "preferences"):
        painter.drawRoundedRect(10, 14, 44, 36, 4, 4)
        painter.drawLine(18, 26, 26, 32)
        painter.drawLine(26, 32, 18, 38)
    else:
        painter.drawEllipse(16, 16, 32, 32)

    painter.end()
    return QIcon(pixmap)

def get_app_icon(theme: str = "dark") -> QIcon:
    """
    Renderiza la marca propia del panel para ventana, dock y bandeja del sistema.
    """
    import os
    from PyQt6.QtSvg import QSvgRenderer

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg_path = os.path.join(base_dir, "assets", "panel-mark.svg")

    if os.path.isfile(svg_path):
        renderer = QSvgRenderer(svg_path)
        if renderer.isValid():
            icon = QIcon()
            # Tamaños estándar para títulos de ventana, dock, bandeja y alt-tab (KDE, GNOME, Wayland, X11)
            for s in (16, 20, 22, 24, 32, 48, 64, 128, 256):
                pm = QPixmap(s, s)
                pm.fill(Qt.GlobalColor.transparent)
                p = QPainter(pm)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                pad = max(1.0, s * 0.07)
                renderer.render(p, QRectF(pad, pad, s - 2 * pad, s - 2 * pad))
                p.end()
                icon.addPixmap(pm)
            return icon
        return QIcon(svg_path)

    if HAS_QTAWESOME and qta is not None:
        try:
            return qta.icon("fa6s.network-wired", color=icon_color("default"))
        except Exception:
            pass
    return _create_fallback_icon("tailscale", icon_color("default"))
