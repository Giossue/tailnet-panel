"""
Vista de App Connector (Comandos: appc-routes, --all, --map, --n).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from app.core.runner import global_runner
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton

class AppcView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header_box = QGroupBox("Monitorización de Rutas de App Connector (tailscale appc-routes)")
        h_layout = QVBoxLayout(header_box)

        desc_lbl = QLabel(
            "Los App Connectors permiten dirigir tráfico de dominios y aplicaciones corporativas específicas "
            "a través de nodos designados sin necesidad de VPNs tradicionales de subred completa."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setProperty("class", "muted-copy")
        h_layout.addWidget(desc_lbl)

        btn_bar = QHBoxLayout()
        btn_routes = AppButton("Estado Rutas")
        btn_routes.set_icon("routes")
        btn_routes.clicked.connect(lambda: global_runner.run(["appc-routes"]))
        btn_bar.addWidget(btn_routes)

        btn_all = AppButton("Todas las Rutas y Políticas (--all)")
        btn_all.set_icon("globe")
        btn_all.setProperty("class", "btn-primary")
        btn_all.clicked.connect(lambda: global_runner.run(["appc-routes", "--all"]))
        btn_bar.addWidget(btn_all)

        btn_map = AppButton("Mapa de Dominios (--map)")
        btn_map.set_icon("map")
        btn_map.clicked.connect(lambda: global_runner.run(["appc-routes", "--map"]))
        btn_bar.addWidget(btn_map)

        btn_n = AppButton("Total de Rutas (--n)")
        btn_n.set_icon("list-ol")
        btn_n.clicked.connect(lambda: global_runner.run(["appc-routes", "--n"]))
        btn_bar.addWidget(btn_n)

        btn_bar.addStretch()
        h_layout.addLayout(btn_bar)

        layout.addWidget(header_box)

        # Visor de salida
        self.output_view = QPlainTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setPlaceholderText("La salida de las rutas del App Connector se mostrará aquí y en la terminal...")
        layout.addWidget(self.output_view)

        global_runner.finished.connect(self._on_command_finished)

    def _on_command_finished(self, result):
        if "appc-routes" in result.command:
            self.output_view.setPlainText(result.output if result.output else result.error_output)
