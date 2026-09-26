"""
Vista de Diagnósticos de Red (Comandos: netcheck, ping, nc, dns, metrics, bugreport).
"""
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QButtonGroup, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QFormLayout, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppRadioButton, AppSpinBox, set_tab_icon
from app.ui.components.stat_card import StatCard
from app.core.runner import global_runner

class DiagnosticsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # ----------------- Subtab 1: Netcheck -----------------
        tab_netcheck = QWidget()
        netcheck_layout = QVBoxLayout(tab_netcheck)
        netcheck_layout.setSpacing(12)

        nc_bar = QHBoxLayout()
        self.btn_run_netcheck = AppButton("Ejecutar Netcheck")
        self.btn_run_netcheck.set_icon("rocket")
        self.btn_run_netcheck.setProperty("class", "btn-primary")
        self.btn_run_netcheck.clicked.connect(self.action_run_netcheck)
        nc_bar.addWidget(self.btn_run_netcheck)

        self.btn_netcheck_json = AppButton("Netcheck JSON")
        self.btn_netcheck_json.set_icon("file")
        self.btn_netcheck_json.clicked.connect(lambda: global_runner.run(["netcheck", "--format=json"]))
        nc_bar.addWidget(self.btn_netcheck_json)

        nc_bar.addStretch()
        netcheck_layout.addLayout(nc_bar)

        # Tarjetas de resumen netcheck
        cards_layout = QHBoxLayout()
        self.card_udp = StatCard("Soporte UDP", "---", "Conexión directa peer-to-peer", "diagnostics")
        self.card_derp = StatCard("Servidor DERP Preferido", "---", "Relay de respaldo", "serve")
        self.card_ipv4 = StatCard("IPv4 / IPv6", "---", "Enrutabilidad global", "globe")
        cards_layout.addWidget(self.card_udp)
        cards_layout.addWidget(self.card_derp)
        cards_layout.addWidget(self.card_ipv4)
        netcheck_layout.addLayout(cards_layout)

        # Tabla de latencias DERP
        lbl_derp = QLabel("Latencias por Región DERP (Servidores Relay de Tailscale):")
        lbl_derp.setStyleSheet("font-weight: 600; margin-top: 8px;")
        netcheck_layout.addWidget(lbl_derp)

        self.derp_table = QTableWidget()
        self.derp_table.setColumnCount(3)
        self.derp_table.setHorizontalHeaderLabels(["Región DERP", "Código", "Latencia (ms)"])
        self.derp_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.derp_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.derp_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.derp_table.verticalHeader().setVisible(False)
        self.derp_table.setAlternatingRowColors(True)
        netcheck_layout.addWidget(self.derp_table)

        tabs.addTab(tab_netcheck, "Netcheck")
        set_tab_icon(tabs, 0, "globe")

        # ----------------- Subtab 2: Ping -----------------
        tab_ping = QWidget()
        ping_layout = QVBoxLayout(tab_ping)

        ping_box = QGroupBox("Prueba de Conectividad con Tailscale Ping")
        ping_form = QFormLayout(ping_box)
        ping_form.setSpacing(12)

        self.ping_host_input = QLineEdit()
        self.ping_host_input.setPlaceholderText("Nombre del equipo o IP Tailscale (ej: laptop o 100.x.y.z)")
        ping_form.addRow("Host / IP Destino:", self.ping_host_input)

        # Modo de Ping
        mode_layout = QHBoxLayout()
        self.rb_ping_std = AppRadioButton("Estándar")
        self.rb_ping_std.setChecked(True)
        self.rb_ping_direct = AppRadioButton("--until-direct")
        self.rb_ping_icmp = AppRadioButton("--icmp")
        self.rb_ping_tsmp = AppRadioButton("--tsmp")

        self.ping_mode_group = QButtonGroup(self)
        self.ping_mode_group.addButton(self.rb_ping_std)
        self.ping_mode_group.addButton(self.rb_ping_direct)
        self.ping_mode_group.addButton(self.rb_ping_icmp)
        self.ping_mode_group.addButton(self.rb_ping_tsmp)

        mode_layout.addWidget(self.rb_ping_std)
        mode_layout.addWidget(self.rb_ping_direct)
        mode_layout.addWidget(self.rb_ping_icmp)
        mode_layout.addWidget(self.rb_ping_tsmp)
        mode_layout.addStretch()
        ping_form.addRow("Modo de Ping:", mode_layout)

        self.ping_count = AppSpinBox()
        self.ping_count.setRange(1, 100)
        self.ping_count.setValue(4)
        ping_form.addRow("Cantidad de paquetes (-c):", self.ping_count)

        btn_start_ping = AppButton("Iniciar Ping")
        btn_start_ping.set_icon("ping")
        btn_start_ping.setProperty("class", "btn-primary")
        btn_start_ping.clicked.connect(self.action_start_ping)
        ping_form.addRow("", btn_start_ping)

        ping_layout.addWidget(ping_box)
        ping_layout.addStretch()

        tabs.addTab(tab_netcheck, "Netcheck")
        set_tab_icon(tabs, 0, "globe")

        tabs.addTab(tab_ping, "Ping")
        set_tab_icon(tabs, 1, "ping")

        # ----------------- Subtab 3: Netcat (nc) -----------------
        tab_nc = QWidget()
        nc_layout = QVBoxLayout(tab_nc)

        nc_box = QGroupBox("Herramienta Netcat sobre Tailscale (tailscale nc)")
        nc_form = QFormLayout(nc_box)
        nc_form.setSpacing(10)

        self.nc_host = QLineEdit()
        self.nc_host.setPlaceholderText("Host o IP Tailscale destino")
        nc_form.addRow("Host Destino:", self.nc_host)

        self.nc_port = AppSpinBox()
        self.nc_port.setRange(1, 65535)
        self.nc_port.setValue(80)
        nc_form.addRow("Puerto:", self.nc_port)

        btn_nc_run = AppButton("Conectar con Netcat")
        btn_nc_run.set_icon("netcat")
        btn_nc_run.setProperty("class", "btn-primary")
        btn_nc_run.clicked.connect(self.action_run_nc)
        nc_form.addRow("", btn_nc_run)

        nc_layout.addWidget(nc_box)
        nc_layout.addStretch()

        tabs.addTab(tab_nc, "Netcat")
        set_tab_icon(tabs, 2, "netcat")

        # ----------------- Subtab 4: DNS -----------------
        tab_dns = QWidget()
        dns_layout = QVBoxLayout(tab_dns)

        dns_box = QGroupBox("Consultas y Estado DNS Local")
        dns_form = QFormLayout(dns_box)
        dns_form.setSpacing(12)

        btn_dns_status = AppButton("Ver Estado de DNS y MagicDNS")
        btn_dns_status.set_icon("dns")
        btn_dns_status.clicked.connect(lambda: global_runner.run(["dns", "status"]))
        dns_form.addRow("Configuración Actual:", btn_dns_status)

        query_row = QHBoxLayout()
        self.dns_query_input = QLineEdit()
        self.dns_query_input.setPlaceholderText("Nombre a resolver (ej: servidor o google.com)")
        btn_do_query = AppButton("Consultar Resolvedor")
        btn_do_query.set_icon("search")
        btn_do_query.clicked.connect(self.action_dns_query)
        query_row.addWidget(self.dns_query_input)
        query_row.addWidget(btn_do_query)
        dns_form.addRow("Consulta DNS:", query_row)

        dns_layout.addWidget(dns_box)
        dns_layout.addStretch()

        tabs.addTab(tab_dns, "DNS")
        set_tab_icon(tabs, 3, "dns")

        # ----------------- Subtab 5: Métricas & Bug Report -----------------
        tab_sys_diag = QWidget()
        diag_layout = QVBoxLayout(tab_sys_diag)

        metrics_box = QGroupBox("Métricas del Cliente Tailscale")
        m_layout = QHBoxLayout(metrics_box)
        btn_metrics_print = AppButton("Imprimir Métricas")
        btn_metrics_print.set_icon("metrics")
        btn_metrics_print.clicked.connect(lambda: global_runner.run(["metrics", "print"]))
        m_layout.addWidget(btn_metrics_print)

        btn_metrics_write = AppButton("Guardar Métricas en Archivo")
        btn_metrics_write.set_icon("download")
        btn_metrics_write.clicked.connect(self.action_save_metrics)
        m_layout.addWidget(btn_metrics_write)
        diag_layout.addWidget(metrics_box)

        bug_box = QGroupBox("Reporte de Problemas / Diagnóstico Oficial")
        b_layout = QHBoxLayout(bug_box)
        btn_bugreport = AppButton("Generar Bug Report (--diagnose)")
        btn_bugreport.set_icon("bugreport")
        btn_bugreport.setProperty("class", "btn-primary")
        btn_bugreport.clicked.connect(lambda: global_runner.run(["bugreport", "--diagnose"]))
        b_layout.addWidget(btn_bugreport)
        diag_layout.addWidget(bug_box)

        diag_layout.addStretch()
        tabs.addTab(tab_sys_diag, "Métricas & Bugreport")
        set_tab_icon(tabs, 4, "metrics")

        layout.addWidget(tabs)

    def action_run_netcheck(self):
        if global_runner.is_running():
            return

        def on_netcheck_finish(result):
            global_runner.finished.disconnect(on_netcheck_finish)
            try:
                if result.success:
                    data = json.loads(result.output)
                    udp = data.get("UDP", False)
                    self.card_udp.set_value("Habilitado" if udp else "Bloqueado")
                    self.card_udp.set_status_color("success" if udp else "danger")

                    pref_derp = data.get("PreferredDERP", 0)
                    derp_node = data.get("RegionName", f"Región {pref_derp}")
                    self.card_derp.set_value(str(derp_node))

                    ipv4 = data.get("IPv4", False)
                    ipv6 = data.get("IPv6", False)
                    self.card_ipv4.set_value(f"IPv4: {'OK' if ipv4 else 'No'} | IPv6: {'OK' if ipv6 else 'No'}")

                    # Latencias
                    latencies = data.get("RegionLatency", {})
                    self.derp_table.setRowCount(len(latencies))
                    for i, (r_id, lat) in enumerate(sorted(latencies.items(), key=lambda x: x[1])):
                        ms = round(lat * 1000, 1) if lat < 10 else round(lat, 1)
                        self.derp_table.setItem(i, 0, QTableWidgetItem(f"DERP Región {r_id}"))
                        self.derp_table.setItem(i, 1, QTableWidgetItem(str(r_id)))
                        self.derp_table.setItem(i, 2, QTableWidgetItem(f"{ms} ms"))
            except Exception:
                pass

        global_runner.finished.connect(on_netcheck_finish)
        global_runner.run(["netcheck", "--format=json"])

    def action_start_ping(self):
        host = self.ping_host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Atención", "Por favor ingresa el host destino.")
            return

        args = ["ping"]
        if self.rb_ping_direct.isChecked():
            args.append("--until-direct")
        elif self.rb_ping_icmp.isChecked():
            args.append("--icmp")
        elif self.rb_ping_tsmp.isChecked():
            args.append("--tsmp")

        args.append(f"-c={self.ping_count.value()}")
        args.append(host)
        global_runner.run(args)

    def action_run_nc(self):
        host = self.nc_host.text().strip()
        if not host:
            QMessageBox.warning(self, "Atención", "Por favor ingresa el host destino.")
            return
        args = ["nc", host, str(self.nc_port.value())]
        launched = global_runner.launch_in_external_terminal(args, window_title=f"Netcat {host}:{self.nc_port.value()}")
        if not launched:
            global_runner.run(args)

    def action_dns_query(self):
        name = self.dns_query_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Atención", "Por favor escribe el nombre de dominio a consultar.")
            return
        global_runner.run(["dns", "query", name])

    def action_save_metrics(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar métricas", "metrics.txt", "Archivos de texto (*.txt)")
        if path:
            global_runner.run(["metrics", "write", path])
