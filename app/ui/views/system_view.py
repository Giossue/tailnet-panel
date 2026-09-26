"""
Vista de Sistema, Actualizaciones, Configuración y Autocompletado Shell (Comandos: configure, completion, update, version, licenses, wait).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTabWidget, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from app.ui.components.stat_card import StatCard
from app.core.runner import global_runner
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, set_tab_icon

class SystemView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # ----------------- Subtab 1: Actualizaciones y Versión -----------------
        tab_updates = QWidget()
        upd_layout = QVBoxLayout(tab_updates)
        upd_layout.setSpacing(12)

        # Tarjetas de versión
        ver_cards = QHBoxLayout()
        self.card_ver = StatCard("Versión Local", "---", "Cliente CLI", icon_name="version")
        self.card_upstream = StatCard("Versión Upstream", "---", "Servidor oficial", icon_name="globe")
        ver_cards.addWidget(self.card_ver)
        ver_cards.addWidget(self.card_upstream)
        upd_layout.addLayout(ver_cards)

        ver_bar = QHBoxLayout()
        btn_ver = AppButton("tailscale version")
        btn_ver.set_icon("info")
        btn_ver.clicked.connect(lambda: global_runner.run(["version"]))
        ver_bar.addWidget(btn_ver)

        btn_ver_daemon = AppButton("version --daemon")
        btn_ver_daemon.set_icon("server")
        btn_ver_daemon.clicked.connect(lambda: global_runner.run(["version", "--daemon"]))
        ver_bar.addWidget(btn_ver_daemon)

        btn_ver_upstream = AppButton("version --upstream")
        btn_ver_upstream.set_icon("globe")
        btn_ver_upstream.clicked.connect(lambda: global_runner.run(["version", "--upstream"]))
        ver_bar.addWidget(btn_ver_upstream)

        btn_licenses = AppButton("Licencias Open Source")
        btn_licenses.set_icon("license")
        btn_licenses.clicked.connect(lambda: global_runner.run(["licenses"]))
        ver_bar.addWidget(btn_licenses)

        ver_bar.addStretch()
        upd_layout.addLayout(ver_bar)

        # Grupo de Actualización
        upd_box = QGroupBox("Gestor de Actualizaciones (tailscale update)")
        upd_form = QFormLayout(upd_box)
        upd_form.setSpacing(10)

        upd_btns = QHBoxLayout()
        btn_update_now = AppButton("Actualizar Ahora")
        btn_update_now.set_icon("rocket")
        btn_update_now.setProperty("class", "btn-primary")
        btn_update_now.clicked.connect(lambda: global_runner.run(["update"], needs_sudo=True))
        upd_btns.addWidget(btn_update_now)

        btn_update_dry = AppButton("Simular (--dry-run)")
        btn_update_dry.set_icon("flask")
        btn_update_dry.clicked.connect(lambda: global_runner.run(["update", "--dry-run"]))
        upd_btns.addWidget(btn_update_dry)

        btn_update_unstable = AppButton("Canal Inestable (--track=unstable)")
        btn_update_unstable.set_icon("bolt")
        btn_update_unstable.clicked.connect(lambda: global_runner.run(["update", "--track=unstable"], needs_sudo=True))
        upd_btns.addWidget(btn_update_unstable)
        upd_btns.addStretch()
        upd_form.addRow("Acciones de Actualización:", upd_btns)

        row_custom_ver = QHBoxLayout()
        self.ver_input = QLineEdit()
        self.ver_input.setPlaceholderText("Ej: 1.96.0")
        btn_install_ver = AppButton("Instalar Versión Específica")
        btn_install_ver.set_icon("version")
        btn_install_ver.clicked.connect(self.action_install_version)
        row_custom_ver.addWidget(self.ver_input)
        row_custom_ver.addWidget(btn_install_ver)
        upd_form.addRow("Versión Específica:", row_custom_ver)

        upd_layout.addWidget(upd_box)

        # Esperar a Tailscale (wait)
        wait_box = QGroupBox("Esperar Inicialización (tailscale wait)")
        wait_form = QFormLayout(wait_box)
        row_wait = QHBoxLayout()
        self.wait_timeout = QLineEdit("30s")
        btn_wait = AppButton("tailscale wait")
        btn_wait.set_icon("wait")
        btn_wait.clicked.connect(lambda: global_runner.run(["wait"]))
        btn_wait_timeout = AppButton("tailscale wait --timeout")
        btn_wait_timeout.set_icon("wait")
        btn_wait_timeout.clicked.connect(lambda: global_runner.run(["wait", f"--timeout={self.wait_timeout.text().strip()}"]))
        row_wait.addWidget(btn_wait)
        row_wait.addWidget(self.wait_timeout)
        row_wait.addWidget(btn_wait_timeout)
        row_wait.addStretch()
        wait_form.addRow("Control de Espera:", row_wait)
        upd_layout.addWidget(wait_box)

        upd_layout.addStretch()
        tabs.addTab(tab_updates, "Versión & Actualizaciones")
        set_tab_icon(tabs, 0, "sync")

        # ----------------- Subtab 2: Configuración de SO (configure) -----------------
        tab_config = QWidget()
        cfg_layout = QVBoxLayout(tab_config)

        # Kubernetes
        k8s_box = QGroupBox("Integración con Kubernetes (configure kubeconfig)")
        k8s_form = QFormLayout(k8s_box)
        row_k8s = QHBoxLayout()
        self.k8s_host_input = QLineEdit()
        self.k8s_host_input.setPlaceholderText("k8s.example.ts.net")
        btn_k8s = AppButton("Configurar Kubeconfig")
        btn_k8s.clicked.connect(self.action_k8s)
        row_k8s.addWidget(self.k8s_host_input)
        row_k8s.addWidget(btn_k8s)
        k8s_form.addRow("Kubernetes Host:", row_k8s)
        cfg_layout.addWidget(k8s_box)

        # Synology NAS
        syn_box = QGroupBox("Dispositivos Synology NAS (configure synology)")
        syn_layout = QHBoxLayout(syn_box)
        btn_synology = AppButton("Configurar Synology NAS")
        btn_synology.clicked.connect(lambda: global_runner.run(["configure", "synology"], needs_sudo=True))
        syn_layout.addWidget(btn_synology)
        syn_layout.addWidget(QLabel("Permite las conexiones salientes requeridas en Synology DSM."))
        syn_layout.addStretch()
        cfg_layout.addWidget(syn_box)

        # macOS Integrations
        mac_box = QGroupBox("Integraciones macOS (mac-vpn & sysext)")
        mac_form = QFormLayout(mac_box)

        row_vpn = QHBoxLayout()
        btn_vpn_install = AppButton("Instalar Mac VPN")
        btn_vpn_install.clicked.connect(lambda: global_runner.run(["configure", "mac-vpn", "install"]))
        btn_vpn_uninstall = AppButton("Desinstalar Mac VPN")
        btn_vpn_uninstall.clicked.connect(lambda: global_runner.run(["configure", "mac-vpn", "uninstall"]))
        row_vpn.addWidget(btn_vpn_install)
        row_vpn.addWidget(btn_vpn_uninstall)
        row_vpn.addStretch()
        mac_form.addRow("Configuración VPN macOS:", row_vpn)

        row_sysext = QHBoxLayout()
        btn_sysext_act = AppButton("Activar Extensión")
        btn_sysext_act.clicked.connect(lambda: global_runner.run(["configure", "sysext", "activate"]))
        btn_sysext_deact = AppButton("Desactivar Extensión")
        btn_sysext_deact.clicked.connect(lambda: global_runner.run(["configure", "sysext", "deactivate"]))
        btn_sysext_stat = AppButton("Estado Extensión")
        btn_sysext_stat.clicked.connect(lambda: global_runner.run(["configure", "sysext", "status"]))
        row_sysext.addWidget(btn_sysext_act)
        row_sysext.addWidget(btn_sysext_deact)
        row_sysext.addWidget(btn_sysext_stat)
        row_sysext.addStretch()
        mac_form.addRow("Extensiones de Sistema:", row_sysext)
        cfg_layout.addWidget(mac_box)

        # Systray Linux
        st_box = QGroupBox("Bandeja del Sistema Linux (Systray)")
        st_form = QFormLayout(st_box)
        row_st = QHBoxLayout()
        btn_cfg_systray = AppButton("Configurar Systray")
        btn_cfg_systray.clicked.connect(lambda: global_runner.run(["configure", "systray", "--enable-startup=systemd"]))
        btn_run_systray = AppButton("Lanzar Systray Nativo")
        btn_run_systray.clicked.connect(lambda: global_runner.run(["systray"]))
        row_st.addWidget(btn_cfg_systray)
        row_st.addWidget(btn_run_systray)
        row_st.addStretch()
        st_form.addRow("Systray Daemon:", row_st)
        cfg_layout.addWidget(st_box)

        cfg_layout.addStretch()
        tabs.addTab(tab_config, "Configuración de SO")
        set_tab_icon(tabs, 1, "settings")

        # ----------------- Subtab 3: Autocompletado Shell (completion) -----------------
        tab_comp = QWidget()
        comp_layout = QVBoxLayout(tab_comp)

        comp_box = QGroupBox("Generación de Scripts de Autocompletado Shell (tailscale completion)")
        comp_form = QFormLayout(comp_box)

        row_comp = QHBoxLayout()
        btn_bash = AppButton("Bash")
        btn_bash.set_icon("terminal")
        btn_bash.clicked.connect(lambda: global_runner.run(["completion", "bash"]))
        btn_zsh = AppButton("Zsh")
        btn_zsh.set_icon("terminal")
        btn_zsh.clicked.connect(lambda: global_runner.run(["completion", "zsh"]))
        btn_fish = AppButton("Fish")
        btn_fish.set_icon("terminal")
        btn_fish.clicked.connect(lambda: global_runner.run(["completion", "fish"]))
        btn_ps = AppButton("PowerShell")
        btn_ps.set_icon("terminal")
        btn_ps.clicked.connect(lambda: global_runner.run(["completion", "powershell"]))

        row_comp.addWidget(btn_bash)
        row_comp.addWidget(btn_zsh)
        row_comp.addWidget(btn_fish)
        row_comp.addWidget(btn_ps)
        row_comp.addStretch()
        comp_form.addRow("Shell Soportado:", row_comp)

        comp_layout.addWidget(comp_box)
        comp_layout.addStretch()

        tabs.addTab(tab_comp, "Autocompletado Shell")
        set_tab_icon(tabs, 2, "terminal")

        layout.addWidget(tabs)

    def action_install_version(self):
        v = self.ver_input.text().strip()
        if not v:
            QMessageBox.warning(self, "Atención", "Ingresa la versión a instalar (ej: 1.96.0).")
            return
        global_runner.run(["update", f"--version={v}"], needs_sudo=True)

    def action_k8s(self):
        host = self.k8s_host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Atención", "Ingresa el host de Kubernetes.")
            return
        global_runner.run(["configure", "kubeconfig", host])
