"""
Vista de Tailscale SSH (Comandos: ssh <host>, ssh <usuario>@<host>, set --ssh).
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, TableActionButton, table_action_cell, configure_action_table
from app.core.runner import global_runner

class SshView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Configuración del servidor SSH local
        server_box = QGroupBox("Servidor Tailscale SSH en este Equipo")
        s_layout = QHBoxLayout(server_box)
        s_lbl = QLabel("Permite a otros usuarios autenticados de tu tailnet conectarse a este equipo mediante SSH sin llaves manuales.")
        s_lbl.setWordWrap(True)
        s_lbl.setProperty("class", "muted-copy")
        s_layout.addWidget(s_lbl)

        btn_enable_ssh = AppButton("Activar Servidor SSH")
        btn_enable_ssh.set_icon("key")
        btn_enable_ssh.setProperty("class", "btn-primary")
        btn_enable_ssh.clicked.connect(lambda: global_runner.run(["set", "--ssh=true"], needs_sudo=True))
        s_layout.addWidget(btn_enable_ssh)

        btn_disable_ssh = AppButton("Desactivar Servidor SSH")
        btn_disable_ssh.set_icon("times")
        btn_disable_ssh.clicked.connect(lambda: global_runner.run(["set", "--ssh=false"], needs_sudo=True))
        s_layout.addWidget(btn_disable_ssh)

        layout.addWidget(server_box)

        # Formulario de conexión SSH saliente
        conn_box = QGroupBox("Conectar a un Equipo Remoto con Tailscale SSH")
        conn_form = QFormLayout(conn_box)
        conn_form.setSpacing(10)

        self.user_input = QLineEdit(os.getenv("USER", "root"))
        conn_form.addRow("Usuario Remoto:", self.user_input)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Nombre del host o IP Tailscale (ej: servidor o 100.x.y.z)")
        conn_form.addRow("Host Destino:", self.host_input)

        btn_connect = AppButton("Iniciar Sesión SSH en Terminal")
        btn_connect.set_icon("ssh")
        btn_connect.setProperty("class", "btn-primary")
        btn_connect.clicked.connect(self.action_connect_ssh)
        conn_form.addRow("", btn_connect)

        layout.addWidget(conn_box)

        # Dispositivos disponibles en la red
        peers_lbl = QLabel("Dispositivos Disponibles para Conexión SSH:")
        peers_lbl.setStyleSheet("font-weight: 600; margin-top: 10px;")
        layout.addWidget(peers_lbl)

        self.peers_table = QTableWidget()
        self.peers_table.setColumnCount(4)
        self.peers_table.setHorizontalHeaderLabels(["Host", "IP Tailscale", "Sistema Operativo", "Acción"])
        self.peers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.peers_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.verticalHeader().setVisible(False)
        self.peers_table.setAlternatingRowColors(True)
        configure_action_table(self.peers_table)
        layout.addWidget(self.peers_table)

    def apply_status(self, status):
        if not status:
            self.peers_table.setRowCount(0)
            return
        peers = status.get("Peer") or {}
        self.peers_table.setRowCount(len(peers))
        for row, (pid, p) in enumerate(peers.items()):
            host = p.get("HostName", "---")
            ips = p.get("TailscaleIPs", ["---"])
            ip_str = ips[0] if ips else "---"
            os_name = p.get("OS", "---")

            self.peers_table.setItem(row, 0, QTableWidgetItem(host))
            self.peers_table.setItem(row, 1, QTableWidgetItem(ip_str))
            self.peers_table.setItem(row, 2, QTableWidgetItem(os_name))

            btn_ssh = TableActionButton("Conectar", "ssh")
            btn_ssh.clicked.connect(lambda ch, h=host: self._quick_ssh(h))
            self.peers_table.setCellWidget(row, 3, table_action_cell(btn_ssh))

    def _quick_ssh(self, host: str):
        self.host_input.setText(host)
        self.action_connect_ssh()

    def action_connect_ssh(self):
        host = self.host_input.text().strip()
        user = self.user_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Atención", "Ingresa el host destino.")
            return

        target = f"{user}@{host}" if user else host
        cmd_args = ["ssh", target]
        launched = global_runner.launch_in_external_terminal(cmd_args, window_title=f"SSH: {target}")
        if not launched:
            global_runner.run(cmd_args)
