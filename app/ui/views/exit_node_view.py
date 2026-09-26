"""
Vista de Nodos de Salida / Exit Nodes (Comandos: exit-node list, exit-node suggest, set --exit-node, set --advertise-exit-node).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, TableActionButton, FlowLayout, table_action_cell, configure_action_table
from app.ui.components.stat_card import StatCard
from app.core.command_registry import COMMANDS_BY_ID
from app.core.async_query import AsyncTailscaleQuery
from app.core.runner import global_runner

class ExitNodeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.nodes_query = AsyncTailscaleQuery(self)
        self.nodes_query.completed.connect(self._on_nodes_response)
        QTimer.singleShot(200, self.refresh_exit_nodes)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Encabezado con estado y tarjeta
        top_layout = QHBoxLayout()
        self.card_current_exit = StatCard("Exit Node Activo", "Ninguno (Conexión Directa)", "El tráfico no está siendo enrutado", "shield")
        top_layout.addWidget(self.card_current_exit)
        layout.addLayout(top_layout)

        # Barra de botones de acción
        bar_frame = QFrame()
        bar_frame.setProperty("class", "card")
        bar_layout = FlowLayout(bar_frame)
        bar_layout.setContentsMargins(12, 10, 12, 10)
        main_actions = QWidget()
        main_actions_layout = QHBoxLayout(main_actions)
        main_actions_layout.setContentsMargins(0, 0, 0, 0)
        main_actions_layout.setSpacing(8)

        self.btn_refresh = AppButton("Actualizar Lista")
        self.btn_refresh.set_icon("refresh")
        self.btn_refresh.clicked.connect(self.refresh_exit_nodes)
        main_actions_layout.addWidget(self.btn_refresh)

        self.btn_suggest = AppButton("Sugerir Mejor Nodo")
        self.btn_suggest.set_icon("star")
        self.btn_suggest.setProperty("class", "btn-primary")
        self.btn_suggest.clicked.connect(self.action_suggest)
        main_actions_layout.addWidget(self.btn_suggest)

        self.btn_clear_exit = AppButton("Desactivar Exit Node")
        self.btn_clear_exit.set_icon("times")
        self.btn_clear_exit.setProperty("class", "btn-danger")
        self.btn_clear_exit.clicked.connect(self.action_clear_exit)
        main_actions_layout.addWidget(self.btn_clear_exit)

        route_actions = QWidget()
        route_actions_layout = QHBoxLayout(route_actions)
        route_actions_layout.setContentsMargins(0, 0, 0, 0)
        route_actions_layout.setSpacing(8)

        self.btn_advertise = AppButton("Anunciar este nodo como Exit Node")
        self.btn_advertise.set_icon("routes")
        self.btn_advertise.clicked.connect(self.action_advertise)
        route_actions_layout.addWidget(self.btn_advertise)

        self.btn_unadvertise = AppButton("Dejar de anunciar")
        self.btn_unadvertise.set_icon("times")
        self.btn_unadvertise.clicked.connect(lambda: global_runner.run(["set", "--advertise-exit-node=false"], needs_sudo=True))
        route_actions_layout.addWidget(self.btn_unadvertise)

        bar_layout.addWidget(main_actions)
        bar_layout.addWidget(route_actions)

        layout.addWidget(bar_frame)

        # Buscador y título de la tabla
        table_header = QHBoxLayout()
        lbl_title = QLabel("Nodos de Salida Disponibles en la Tailnet")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: 600;")
        table_header.addWidget(lbl_title)

        table_header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar por nombre o IP...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._filter_table)
        table_header.addWidget(self.search_input)

        layout.addLayout(table_header)

        # Tabla de Exit Nodes
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["IP / Host", "Nombre de Nodo", "Detalles", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        configure_action_table(self.table)
        layout.addWidget(self.table)

    def refresh_exit_nodes(self):
        self.nodes_query.run(["exit-node", "list"])
        if self.window() is not self:
            self.window().refresh_status()

    def apply_status(self, status):
        exit_node_status = status.get("ExitNodeStatus") if status else None
        ips = exit_node_status.get("TailscaleIPs") or [] if exit_node_status else []
        if ips:
            self.card_current_exit.set_value(f"Activo: {ips[0]}")
            self.card_current_exit.set_status_color("success")
        else:
            self.card_current_exit.set_value("Ninguno (Directo)")
            self.card_current_exit.set_status_color("muted")

    def _on_nodes_response(self, output):
        nodes = []
        if output:
            for line in output.strip().splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    nodes.append({"ip": parts[0], "hostname": parts[1], "raw": line})
        self.table.setRowCount(len(nodes))

        for row, node in enumerate(nodes):
            ip_item = QTableWidgetItem(node["ip"])
            self.table.setItem(row, 0, ip_item)

            host_item = QTableWidgetItem(node["hostname"])
            self.table.setItem(row, 1, host_item)

            raw_item = QTableWidgetItem(node["raw"])
            self.table.setItem(row, 2, raw_item)

            btn_use = TableActionButton("Usar nodo", "check")
            btn_use.clicked.connect(lambda ch, target=node["ip"]: self.action_set_exit(target))
            self.table.setCellWidget(row, 3, table_action_cell(btn_use))
        self._filter_table(self.search_input.text())

    def action_suggest(self):
        global_runner.run(["exit-node", "suggest"])

    def action_set_exit(self, host: str):
        global_runner.run(["set", f"--exit-node={host}"], needs_sudo=True)

    def action_clear_exit(self):
        global_runner.run(["set", "--exit-node="], needs_sudo=True)

    def action_advertise(self):
        global_runner.run(["set", "--advertise-exit-node=true"], needs_sudo=True)

    def _filter_table(self, query: str):
        query = query.lower().strip()
        for r in range(self.table.rowCount()):
            text = " ".join([self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(3)]).lower()
            self.table.setRowHidden(r, query not in text)
