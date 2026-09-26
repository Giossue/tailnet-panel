"""
Tarjeta reutilizable de estadísticas y estado (StatCard) con soporte para íconos vectoriales QtAwesome.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from app.ui.icons import get_icon
from app.config import config
from app.ui.theme import get_theme_colors

class StatCard(QFrame):
    def __init__(self, title: str, value: str = "---", subtitle: str = "", icon_name: str = "info", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self._icon_name = icon_name
        self._value_role = None
        self.init_ui(title, value, subtitle, icon_name)

    def init_ui(self, title: str, value: str, subtitle: str, icon_name: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        header_layout = QHBoxLayout()
        self.icon_lbl = QLabel()
        self.set_icon(icon_name)
        header_layout.addWidget(self.icon_lbl)

        self.title_lbl = QLabel(title)
        self.title_lbl.setProperty("class", "card-title")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.value_lbl = QLabel(value)
        self.value_lbl.setProperty("class", "metric-value")
        self.value_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.value_lbl)

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setProperty("class", "card-subtitle")
        self.sub_lbl.setWordWrap(True)
        layout.addWidget(self.sub_lbl)

    def set_icon(self, icon_name: str):
        self._icon_name = icon_name
        icon = get_icon(icon_name, role="accent")
        self.icon_lbl.setPixmap(icon.pixmap(QSize(20, 20)))

    def refresh_theme(self):
        self.set_icon(self._icon_name)
        if self._value_role:
            self.set_status_color(self._value_role)

    def set_value(self, value: str):
        self.value_lbl.setText(value)

    def set_subtitle(self, subtitle: str):
        self.sub_lbl.setText(subtitle)

    def set_status_color(self, role: str):
        self._value_role = role
        color = get_theme_colors(config.theme).get(role, role)
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
