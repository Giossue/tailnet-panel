"""
Vista de Serve, Funnel y Services (Comandos: serve, funnel, service).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTabWidget,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppCheckBox, AppComboBox, AppSpinBox, set_tab_icon
from app.core.runner import global_runner
from app.core.tailscale_client import TailscaleClient

class ServeFunnelView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Barra superior con estado
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("<b>Gestión de Publicación de Servicios (Serve & Funnel)</b>"))
        top_bar.addStretch()

        btn_status_serve = AppButton("Estado Serve")
        btn_status_serve.set_icon("serve")
        btn_status_serve.clicked.connect(lambda: global_runner.run(["serve", "status"]))
        top_bar.addWidget(btn_status_serve)

        btn_status_funnel = AppButton("Estado Funnel")
        btn_status_funnel.set_icon("globe")
        btn_status_funnel.clicked.connect(lambda: global_runner.run(["funnel", "status"]))
        top_bar.addWidget(btn_status_funnel)

        btn_services_list = AppButton("Listar Services")
        btn_services_list.set_icon("routes")
        btn_services_list.clicked.connect(lambda: global_runner.run(["service", "list"]))
        top_bar.addWidget(btn_services_list)

        layout.addLayout(top_bar)

        tabs = QTabWidget()

        # ----------------- Subtab 1: Tailscale Serve -----------------
        tab_serve = QWidget()
        serve_layout = QVBoxLayout(tab_serve)

        serve_box = QGroupBox("Publicar servicio local dentro de tu Tailnet (HTTPS / HTTP / TCP)")
        serve_form = QFormLayout(serve_box)
        serve_form.setSpacing(10)

        self.serve_target = QLineEdit("localhost:3000")
        serve_form.addRow("Target Local:", self.serve_target)

        self.serve_proto = AppComboBox()
        self.serve_proto.addItems(["HTTPS (Recomendado #65)", "HTTP (#64)", "Proxy TCP (#66)", "Directo (#62)"])
        serve_form.addRow("Protocolo de exposición:", self.serve_proto)

        self.serve_port = AppSpinBox()
        self.serve_port.setRange(1, 65535)
        self.serve_port.setValue(443)
        serve_form.addRow("Puerto en Tailscale:", self.serve_port)

        self.serve_bg = AppCheckBox("Ejecutar en segundo plano de forma persistente (--bg #63)")
        self.serve_bg.setChecked(True)
        serve_form.addRow("Segundo plano:", self.serve_bg)

        btn_row = QHBoxLayout()
        btn_run_serve = AppButton("Publicar Servicio (Serve)")
        btn_run_serve.set_icon("rocket")
        btn_run_serve.setProperty("class", "btn-primary")
        btn_run_serve.clicked.connect(self.action_run_serve)
        btn_row.addWidget(btn_run_serve)

        btn_reset_serve = AppButton("Resetear Serve")
        btn_reset_serve.set_icon("trash")
        btn_reset_serve.setProperty("class", "btn-danger")
        btn_reset_serve.clicked.connect(lambda: global_runner.run(["serve", "reset"]))
        btn_row.addWidget(btn_reset_serve)
        btn_row.addStretch()

        serve_form.addRow("", btn_row)
        serve_layout.addWidget(serve_box)
        serve_layout.addStretch()
        tabs.addTab(tab_serve, "Tailscale Serve (Red Privada)")
        set_tab_icon(tabs, 0, "lock")

        # ----------------- Subtab 2: Tailscale Funnel -----------------
        tab_funnel = QWidget()
        funnel_layout = QVBoxLayout(tab_funnel)

        warn_lbl = QLabel(
            "<b>[AVISO DE SEGURIDAD]</b> Tailscale Funnel expondrá tu servicio local a <b>Internet público</b> mediante "
            "tu dominio público de MagicDNS con certificado HTTPS automático."
        )
        warn_lbl.setObjectName("FunnelWarning")
        warn_lbl.setWordWrap(True)
        funnel_layout.addWidget(warn_lbl)

        funnel_box = QGroupBox("Publicar hacia Internet con Funnel")
        funnel_form = QFormLayout(funnel_box)
        funnel_form.setSpacing(10)

        self.funnel_target = QLineEdit("3000")
        self.funnel_target.setPlaceholderText("Puerto o target (ej: 3000 o localhost:3000)")
        funnel_form.addRow("Target Local:", self.funnel_target)

        self.funnel_bg = AppCheckBox("Ejecutar en segundo plano (--bg #29)")
        self.funnel_bg.setChecked(True)
        funnel_form.addRow("Segundo plano:", self.funnel_bg)

        f_btn_row = QHBoxLayout()
        btn_run_funnel = AppButton("Publicar en Internet (Funnel)")
        btn_run_funnel.set_icon("globe")
        btn_run_funnel.setProperty("class", "btn-primary")
        btn_run_funnel.clicked.connect(self.action_run_funnel)
        f_btn_row.addWidget(btn_run_funnel)

        btn_reset_funnel = AppButton("Resetear Funnel")
        btn_reset_funnel.set_icon("trash")
        btn_reset_funnel.setProperty("class", "btn-danger")
        btn_reset_funnel.clicked.connect(lambda: global_runner.run(["funnel", "reset"]))
        f_btn_row.addWidget(btn_reset_funnel)
        f_btn_row.addStretch()

        funnel_form.addRow("", f_btn_row)
        funnel_layout.addWidget(funnel_box)
        funnel_layout.addStretch()
        tabs.addTab(tab_funnel, "Tailscale Funnel (Internet)")
        set_tab_icon(tabs, 1, "globe")

        # ----------------- Subtab 3: Configuración Declarativa & Servicios HA -----------------
        tab_adv = QWidget()
        adv_layout = QVBoxLayout(tab_adv)

        cfg_box = QGroupBox("Configuración Declarativa JSON (get-config / set-config)")
        cfg_form = QFormLayout(cfg_box)

        cfg_btn_row = QHBoxLayout()
        btn_get_cfg = AppButton("Exportar Configuración (get-config)")
        btn_get_cfg.set_icon("download")
        btn_get_cfg.clicked.connect(self.action_get_config)
        cfg_btn_row.addWidget(btn_get_cfg)

        btn_set_cfg = AppButton("Importar Configuración (set-config)")
        btn_set_cfg.set_icon("upload")
        btn_set_cfg.clicked.connect(self.action_set_config)
        cfg_btn_row.addWidget(btn_set_cfg)
        cfg_btn_row.addStretch()
        cfg_form.addRow("Gestión Declarativa:", cfg_btn_row)
        adv_layout.addWidget(cfg_box)

        ha_box = QGroupBox("Alta Disponibilidad de Servicios (Tailscale Services)")
        ha_form = QFormLayout(ha_box)

        row_adv = QHBoxLayout()
        self.svc_name_input = QLineEdit("svc:web")
        btn_advertise_svc = AppButton("Anunciar Nodo (advertise)")
        btn_advertise_svc.set_icon("share")
        btn_advertise_svc.clicked.connect(lambda: global_runner.run(["serve", "advertise", self.svc_name_input.text().strip()]))
        btn_drain_svc = AppButton("Drenar Nodo (drain)")
        btn_drain_svc.set_icon("trash")
        btn_drain_svc.clicked.connect(lambda: global_runner.run(["serve", "drain", self.svc_name_input.text().strip()]))

        row_adv.addWidget(self.svc_name_input)
        row_adv.addWidget(btn_advertise_svc)
        row_adv.addWidget(btn_drain_svc)
        ha_form.addRow("Servicio (svc:...):", row_adv)
        adv_layout.addWidget(ha_box)

        adv_layout.addStretch()
        tabs.addTab(tab_adv, "Declarativo & Services HA")
        set_tab_icon(tabs, 2, "settings")

        layout.addWidget(tabs)

    def action_run_serve(self):
        target = self.serve_target.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Ingresa un target válido.")
            return

        proto_choice = self.serve_proto.currentIndex()
        args = ["serve"]

        if self.serve_bg.isChecked():
            args.append("--bg")

        if proto_choice == 0: # HTTPS
            args.append(f"--https={self.serve_port.value()}")
            args.append(target)
        elif proto_choice == 1: # HTTP
            args.append(f"--http={self.serve_port.value()}")
            args.append(target)
        elif proto_choice == 2: # TCP
            args.append(f"--tcp={self.serve_port.value()}")
            args.append(target)
        else:
            args.append(target)

        global_runner.run(args)

    def action_run_funnel(self):
        target = self.funnel_target.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Ingresa un target válido para Funnel.")
            return
        args = ["funnel"]
        if self.funnel_bg.isChecked():
            args.append("--bg")
        args.append(target)
        global_runner.run(args)

    def action_get_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar configuración de Serve", "serve_config.json", "JSON (*.json)")
        if path:
            global_runner.run(["serve", "get-config", path, "--all"])

    def action_set_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar configuración de Serve", "", "JSON (*.json)")
        if path:
            global_runner.run(["serve", "set-config", path, "--all"])
