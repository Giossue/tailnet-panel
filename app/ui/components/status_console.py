"""Resumen de conexión y acciones principales de Tailscale."""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel,  QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from app.ui.components.controls import AppButton
from app.core.runner import global_runner


class StatusConsole(QFrame):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusConsole")
        self.is_connected = False
        self.current_ip = ""
        self.hostname = ""
        self.state_label = ""
        self.node_count = 0
        self.online_count = 0
        self.init_ui()
        self._update_appearance()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)

        self.status_dot = QLabel()
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setFixedSize(12, 12)
        layout.addWidget(self.status_dot, alignment=Qt.AlignmentFlag.AlignVCenter)

        copy_layout = QVBoxLayout()
        copy_layout.setSpacing(4)
        eyebrow = QLabel("ESTADO DE TAILSCALE")
        eyebrow.setObjectName("StatusEyebrow")
        copy_layout.addWidget(eyebrow)

        self.host_lbl = QLabel()
        self.host_lbl.setObjectName("StatusHostLabel")
        copy_layout.addWidget(self.host_lbl)

        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(12)
        self.ip_pill = QLabel()
        self.ip_pill.setProperty("class", "kbd-pill")
        self.ip_pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ip_pill.setToolTip("Clic para copiar IP al portapapeles")
        self.ip_pill.mousePressEvent = self._copy_ip
        meta_layout.addWidget(self.ip_pill)

        self.nodes_lbl = QLabel()
        self.nodes_lbl.setProperty("class", "meta-badge")
        meta_layout.addWidget(self.nodes_lbl)

        self.active_lbl = QLabel()
        self.active_lbl.setProperty("class", "meta-badge")
        meta_layout.addWidget(self.active_lbl)
        meta_layout.addStretch()
        copy_layout.addLayout(meta_layout)
        layout.addLayout(copy_layout, stretch=1)

        self.action_btn = AppButton()
        self.action_btn.setObjectName("StatusAction")
        self.action_btn.setMinimumWidth(118)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self.action_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.refresh_btn = AppButton()
        self.refresh_btn.set_icon("refresh")
        self.refresh_btn.setToolTip("Actualizar estado")
        self.refresh_btn.setFixedSize(36, 36)
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(self.refresh_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

    def set_status(self, connected: bool, hostname: str, ip: str,
                   total_nodes: int = 0, online_nodes: int = 0,
                   state_label: str = ""):
        self.is_connected = connected
        self.hostname = hostname or ""
        self.state_label = state_label
        self.current_ip = ip
        self.node_count = total_nodes
        self.online_count = online_nodes
        self._update_appearance()

    def _update_appearance(self):
        state = "connected" if self.is_connected else "disconnected"
        self.status_dot.setProperty("state", state)
        self.action_btn.setProperty("state", state)
        self.host_lbl.setText(
            self.hostname if self.is_connected else self.state_label or "Tailscale desconectado"
        )
        self.ip_pill.setText(self.current_ip if self.is_connected and self.current_ip else "Sin IP activa")
        self.nodes_lbl.setText(f"{self.node_count} nodos")
        self.active_lbl.setText(f"{self.online_count} en línea")
        self.action_btn.setText("Desconectar" if self.is_connected else "Conectar")
        self.action_btn.set_icon("disconnect" if self.is_connected else "connect")
        for widget in (self.status_dot, self.action_btn):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _toggle_connection(self):
        global_runner.run(["down" if self.is_connected else "up"], needs_sudo=True)

    def _copy_ip(self, event):
        if self.current_ip and self.is_connected:
            QApplication.clipboard().setText(self.current_ip)
            self.ip_pill.setText("IP copiada")
            QTimer.singleShot(1200, lambda: self.ip_pill.setText(self.current_ip))
