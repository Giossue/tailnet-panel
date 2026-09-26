"""
Vista principal: Dashboard & Peers (Comandos: up, down, status, ip, whoami, whois, wait, systray, web).
"""
import getpass
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QApplication, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt
from app.ui.components.command_dialog import CommandDialog
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppCheckBox, TableActionButton, table_action_cell, configure_action_table
from app.core.command_registry import COMMANDS_BY_ID
from app.core.runner import global_runner
from app.config import config
from app.ui.theme import get_theme_colors
from PyQt6.QtGui import QColor

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cached_status: Optional[Dict[str, Any]] = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Fila 1: Barra de Destino Rápido (Inspirada en NodesTab de Tailscale Control)
        target_frame = QFrame()
        target_frame.setProperty("class", "card")
        target_layout = QHBoxLayout(target_frame)
        target_layout.setContentsMargins(12, 10, 12, 10)
        target_layout.setSpacing(10)

        target_lbl = QLabel("Destino Rápido:")
        target_lbl.setStyleSheet("font-weight: 700;")
        target_layout.addWidget(target_lbl)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Nombre del equipo o IP Tailscale (ej: 100.x.y.z o laptop)...")
        target_layout.addWidget(self.target_input, stretch=1)

        self.btn_target_ping = AppButton("Ping")
        self.btn_target_ping.set_icon("ping")
        self.btn_target_ping.clicked.connect(self.action_target_ping)
        target_layout.addWidget(self.btn_target_ping)

        self.btn_target_ssh = AppButton("SSH")
        self.btn_target_ssh.set_icon("ssh")
        self.btn_target_ssh.clicked.connect(self.action_target_ssh)
        target_layout.addWidget(self.btn_target_ssh)

        self.btn_target_whois = AppButton("WhoIs")
        self.btn_target_whois.set_icon("search")
        self.btn_target_whois.clicked.connect(self.action_target_whois)
        target_layout.addWidget(self.btn_target_whois)

        layout.addWidget(target_frame)

        # Banner de aviso de modo operador (si no es operador)
        self.operator_frame = QFrame()
        self.operator_frame.setObjectName("OperatorNotice")
        op_layout = QHBoxLayout(self.operator_frame)
        op_layout.setContentsMargins(12, 8, 12, 8)

        current_u = getpass.getuser()
        lbl_op_info = QLabel(
            f"Autoriza una vez a {current_u} para administrar Tailscale sin diálogos repetidos."
        )
        op_layout.addWidget(lbl_op_info)
        op_layout.addStretch()

        btn_setup_op = AppButton("Habilitar permisos")
        btn_setup_op.set_icon("key")
        btn_setup_op.setProperty("class", "btn-primary")
        btn_setup_op.clicked.connect(lambda: global_runner.run(["set", f"--operator={current_u}"], needs_sudo=True))
        op_layout.addWidget(btn_setup_op)

        layout.addWidget(self.operator_frame)
        self.operator_frame.hide()
        global_runner.finished.connect(self._on_command_finished)

        self.whois_input = self.target_input

        # Fila 4: Cabecera de la tabla de peers y filtros
        peers_header = QHBoxLayout()
        peers_title = QLabel("Dispositivos en la Red (Peers)")
        peers_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        peers_header.addWidget(peers_title)

        peers_header.addStretch()

        self.search_peers = QLineEdit()
        self.search_peers.setPlaceholderText("Filtrar peers por nombre o IP...")
        self.search_peers.setMaximumWidth(250)
        self.search_peers.textChanged.connect(self._filter_peers_table)
        peers_header.addWidget(self.search_peers)

        self.cb_active_only = AppCheckBox("Solo activos")
        self.cb_active_only.toggled.connect(self.refresh_data)
        peers_header.addWidget(self.cb_active_only)

        layout.addLayout(peers_header)

        # Fila 5: Tabla de Peers
        self.peers_table = QTableWidget()
        self.peers_table.setColumnCount(6)
        self.peers_table.setHorizontalHeaderLabels([
            "Dispositivo", "IP Tailscale", "Sistema Operativo", "Estado / Tráfico", "DNS Name", "Acciones"
        ])
        self.peers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.peers_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.peers_table.setAlternatingRowColors(True)
        self.peers_table.verticalHeader().setVisible(False)
        configure_action_table(self.peers_table)
        layout.addWidget(self.peers_table)

    def refresh_data(self):
        """Aplica los filtros al último estado compartido por la ventana."""
        status = self.cached_status
        if not status:
            self.peers_table.setRowCount(0)
            return

        # Peers
        peer_dict = status.get("Peer") or {}
        active_only = self.cb_active_only.isChecked()
        filtered_peers = []
        for pid, p in peer_dict.items():
            if not p:
                continue
            if active_only and not p.get("Active", False):
                continue
            filtered_peers.append(p)

        self._populate_peers_table(filtered_peers)
        self._filter_peers_table(self.search_peers.text())

    def apply_status(self, status):
        self.cached_status = status
        self.refresh_data()

    def _on_command_finished(self, result):
        if result.success and "--operator=" in result.command:
            from app.config import set_current_user_operator
            set_current_user_operator(getpass.getuser())
            self.operator_frame.hide()
            if hasattr(self.window(), "refresh_operator_status"):
                self.window().refresh_operator_status(force=True)

    def _populate_peers_table(self, peers):
        self.peers_table.setRowCount(len(peers))
        for row, p in enumerate(peers):
            hostname = p.get("HostName", "Desconocido")
            ips = p.get("TailscaleIPs", ["---"])
            ip_str = ips[0] if ips else "---"
            os_name = p.get("OS", "desconocido")
            active = p.get("Active", False)
            online = p.get("Online", False)
            dns_name = p.get("DNSName", "").rstrip(".")

            # Dispositivo
            dev_item = QTableWidgetItem(f"  {hostname}")
            dev_item.setIcon(get_icon("device"))
            self.peers_table.setItem(row, 0, dev_item)

            # IP
            ip_item = QTableWidgetItem(ip_str)
            self.peers_table.setItem(row, 1, ip_item)

            # OS
            os_item = QTableWidgetItem(os_name.capitalize())
            self.peers_table.setItem(row, 2, os_item)

            # Estado
            status_text = "En línea (Activo)" if active else ("En línea" if online else "Desconectado")
            status_item = QTableWidgetItem(status_text)
            colors = get_theme_colors(config.theme)
            status_item.setForeground(QColor(colors["success"] if active or online else colors["muted"]))
            self.peers_table.setItem(row, 3, status_item)

            # DNS
            dns_item = QTableWidgetItem(dns_name)
            self.peers_table.setItem(row, 4, dns_item)

            # Acciones
            action_btn = TableActionButton("Opciones", "chevron-down")
            action_btn.clicked.connect(
                lambda checked, h=hostname, ip=ip_str, w=action_btn: self._show_peer_menu(h, ip, w)
            )
            self.peers_table.setCellWidget(row, 5, table_action_cell(action_btn))

    def _show_peer_menu(self, hostname: str, ip: str, widget: AppButton):
        menu = QMenu(self)

        act_copy = menu.addAction(f"Copiar IP ({ip})")
        act_copy.setIcon(get_icon("copy"))
        act_copy.triggered.connect(lambda: QApplication.clipboard().setText(ip))

        act_ping = menu.addAction(f"Ping a {hostname}")
        act_ping.setIcon(get_icon("ping"))
        act_ping.triggered.connect(lambda: global_runner.run(["ping", ip]))

        act_ssh = menu.addAction(f"Conectar SSH ({hostname})")
        act_ssh.setIcon(get_icon("ssh"))
        act_ssh.triggered.connect(lambda: global_runner.launch_in_external_terminal(["ssh", ip], window_title=f"SSH {hostname}"))

        act_file = menu.addAction("Enviar archivo (Taildrop)")
        act_file.setIcon(get_icon("folder"))
        act_file.triggered.connect(lambda: self._open_taildrop_for(hostname))

        act_whois = menu.addAction(f"Whois de {ip}")
        act_whois.setIcon(get_icon("search"))
        act_whois.triggered.connect(lambda: global_runner.run(["whois", ip]))

        menu.exec(widget.mapToGlobal(widget.rect().bottomLeft()))

    def _open_taildrop_for(self, hostname: str):
        cmd = COMMANDS_BY_ID[25] # tailscale file cp
        dlg = CommandDialog(cmd, self)
        # Preconfigurar destino
        if "target" in dlg.param_widgets:
            _, w = dlg.param_widgets["target"]
            w.setText(f"{hostname}:")
            dlg.update_preview()
        dlg.exec()

    def _filter_peers_table(self, query: str):
        query = query.lower().strip()
        for r in range(self.peers_table.rowCount()):
            host_item = self.peers_table.item(r, 0)
            ip_item = self.peers_table.item(r, 1)
            text = f"{host_item.text() if host_item else ''} {ip_item.text() if ip_item else ''}".lower()
            self.peers_table.setRowHidden(r, query not in text)

    def action_up(self):
        """Ejecuta comando #1 tailscale up."""
        global_runner.run(["up"], needs_sudo=True)

    def action_up_custom(self):
        """Abre modal con todos los flags de comando #1."""
        dlg = CommandDialog(COMMANDS_BY_ID[1], self)
        dlg.exec()

    def action_down(self):
        """Ejecuta comando #2 tailscale down."""
        reply = QMessageBox.question(
            self, "Confirmar desconexión",
            "¿Deseas desconectar este dispositivo de Tailscale?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            global_runner.run(["down"], needs_sudo=True)

    def action_web(self):
        """Ejecuta comando #105 tailscale web."""
        dlg = CommandDialog(COMMANDS_BY_ID[105], self)
        dlg.exec()

    def action_whoami(self):
        """Ejecuta comando #108 tailscale whoami."""
        global_runner.run(["whoami"])

    def action_whois(self):
        """Ejecuta comando #110 tailscale whois <IP>."""
        ip = self.whois_input.text().strip() if hasattr(self, "whois_input") else ""
        if not ip and hasattr(self, "target_input"):
            ip = self.target_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Atención", "Por favor ingresa una dirección IP o nombre de host.")
            return
        global_runner.run(["whois", ip])

    def action_target_ping(self):
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Ingresa un Host o IP para hacer Ping.")
            return
        global_runner.run(["ping", target])

    def action_target_ssh(self):
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Ingresa un Host o IP para conectar por SSH.")
            return
        global_runner.launch_in_external_terminal(["ssh", target], window_title=f"SSH {target}")

    def action_target_whois(self):
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Ingresa una IP o Host para WhoIs.")
            return
        global_runner.run(["whois", target])
