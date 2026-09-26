"""
Vista de Seguridad: Certificados HTTPS y Tailnet Lock (Comandos: cert, lock).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTabWidget, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, set_tab_icon
from app.core.runner import global_runner

class SecurityView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # ----------------- Subtab 1: Certificados HTTPS -----------------
        tab_cert = QWidget()
        cert_layout = QVBoxLayout(tab_cert)

        cert_box = QGroupBox("Generador de Certificados HTTPS de Let's Encrypt (tailscale cert)")
        cert_form = QFormLayout(cert_box)
        cert_form.setSpacing(10)

        self.cert_host_input = QLineEdit()
        self.cert_host_input.setPlaceholderText("ej: micomputadora.taile8cb90.ts.net")
        cert_form.addRow("MagicDNS Hostname:", self.cert_host_input)

        row_cert_file = QHBoxLayout()
        self.cert_file_input = QLineEdit("cert.pem")
        btn_browse_cert = AppButton("Examinar...")
        btn_browse_cert.set_icon("folder")
        btn_browse_cert.clicked.connect(self.browse_cert)
        row_cert_file.addWidget(self.cert_file_input)
        row_cert_file.addWidget(btn_browse_cert)
        cert_form.addRow("Archivo Certificado (--cert-file):", row_cert_file)

        row_key_file = QHBoxLayout()
        self.key_file_input = QLineEdit("key.pem")
        btn_browse_key = AppButton("Examinar...")
        btn_browse_key.set_icon("folder")
        btn_browse_key.clicked.connect(self.browse_key)
        row_key_file.addWidget(self.key_file_input)
        row_key_file.addWidget(btn_browse_key)
        cert_form.addRow("Archivo Clave Privada (--key-file):", row_key_file)

        btn_gen_cert = AppButton("Obtener Certificado HTTPS")
        btn_gen_cert.set_icon("cert")
        btn_gen_cert.setProperty("class", "btn-primary")
        btn_gen_cert.clicked.connect(self.action_generate_cert)
        cert_form.addRow("", btn_gen_cert)

        cert_layout.addWidget(cert_box)
        cert_layout.addStretch()

        tabs.addTab(tab_cert, "Certificados HTTPS (Let's Encrypt)")
        set_tab_icon(tabs, 0, "cert")

        # ----------------- Subtab 2: Tailnet Lock -----------------
        tab_lock = QWidget()
        lock_layout = QVBoxLayout(tab_lock)
        lock_layout.setSpacing(12)

        lock_bar = QHBoxLayout()
        btn_status_lock = AppButton("Estado Tailnet Lock")
        btn_status_lock.set_icon("security")
        btn_status_lock.clicked.connect(lambda: global_runner.run(["lock", "status"]))
        lock_bar.addWidget(btn_status_lock)

        btn_init_lock = AppButton("Inicializar Lock")
        btn_init_lock.set_icon("lock")
        btn_init_lock.setProperty("class", "btn-primary")
        btn_init_lock.clicked.connect(lambda: global_runner.run(["lock", "init"], needs_sudo=True))
        lock_bar.addWidget(btn_init_lock)

        btn_log_lock = AppButton("Historial de Cambios")
        btn_log_lock.set_icon("license")
        btn_log_lock.clicked.connect(lambda: global_runner.run(["lock", "log"]))
        lock_bar.addWidget(btn_log_lock)

        lock_bar.addStretch()
        lock_layout.addLayout(lock_bar)

        # Claves de firma (Add, Remove, Sign)
        keys_box = QGroupBox("Gestión de Claves de Firma y Nodos")
        keys_form = QFormLayout(keys_box)

        # Add key
        row_add = QHBoxLayout()
        self.add_key_input = QLineEdit()
        self.add_key_input.setPlaceholderText("tlpub:...")
        btn_add_key = AppButton("Añadir Clave")
        btn_add_key.set_icon("key")
        btn_add_key.clicked.connect(self.action_add_key)
        row_add.addWidget(self.add_key_input)
        row_add.addWidget(btn_add_key)
        keys_form.addRow("Añadir Clave Confiable:", row_add)

        # Remove key
        row_rem = QHBoxLayout()
        self.rem_key_input = QLineEdit()
        self.rem_key_input.setPlaceholderText("tlpub:...")
        btn_rem_key = AppButton("Remover Clave")
        btn_rem_key.set_icon("trash")
        btn_rem_key.clicked.connect(self.action_remove_key)
        row_rem.addWidget(self.rem_key_input)
        row_rem.addWidget(btn_rem_key)
        keys_form.addRow("Remover Clave:", row_rem)

        # Sign node key
        row_sign = QHBoxLayout()
        self.sign_key_input = QLineEdit()
        self.sign_key_input.setPlaceholderText("nodekey:...")
        btn_sign_key = AppButton("Firmar Nodo")
        btn_sign_key.set_icon("check")
        btn_sign_key.setProperty("class", "btn-primary")
        btn_sign_key.clicked.connect(self.action_sign_key)
        row_sign.addWidget(self.sign_key_input)
        row_sign.addWidget(btn_sign_key)
        keys_form.addRow("Firmar Clave de Nodo:", row_sign)

        # Revoke keys
        row_rev = QHBoxLayout()
        self.rev_key_input = QLineEdit()
        self.rev_key_input.setPlaceholderText("tlpub:... a revocar")
        btn_rev_key = AppButton("Revocar Claves")
        btn_rev_key.set_icon("times")
        btn_rev_key.setProperty("class", "btn-danger")
        btn_rev_key.clicked.connect(self.action_revoke_key)
        row_rev.addWidget(self.rev_key_input)
        row_rev.addWidget(btn_rev_key)
        keys_form.addRow("Revocar Clave Retroactiva:", row_rev)

        lock_layout.addWidget(keys_box)

        # Desactivación de Lock
        disable_box = QGroupBox("Desactivación de Tailnet Lock")
        dis_form = QFormLayout(disable_box)

        row_dis = QHBoxLayout()
        self.secret_input = QLineEdit()
        self.secret_input.setPlaceholderText("Disablement secret...")
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        btn_dis_global = AppButton("Desactivar Globalmente")
        btn_dis_global.set_icon("lock-open")
        btn_dis_global.setProperty("class", "btn-danger")
        btn_dis_global.clicked.connect(self.action_disable_global)
        row_dis.addWidget(self.secret_input)
        row_dis.addWidget(btn_dis_global)
        dis_form.addRow("Desactivar con Secreto:", row_dis)

        btn_dis_local = AppButton("Desactivar Únicamente en Nodo Local")
        btn_dis_local.set_icon("times")
        btn_dis_local.clicked.connect(lambda: global_runner.run(["lock", "local-disable"], needs_sudo=True))
        dis_form.addRow("Desactivación Local:", btn_dis_local)

        lock_layout.addWidget(disable_box)
        lock_layout.addStretch()

        tabs.addTab(tab_lock, "Tailnet Lock (Zero-Trust Signing)")
        set_tab_icon(tabs, 1, "security")

        layout.addWidget(tabs)

    def browse_cert(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Certificado", "cert.pem", "PEM (*.pem)")
        if path:
            self.cert_file_input.setText(path)

    def browse_key(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Clave", "key.pem", "PEM (*.pem)")
        if path:
            self.key_file_input.setText(path)

    def action_generate_cert(self):
        host = self.cert_host_input.text().strip()
        c_file = self.cert_file_input.text().strip()
        k_file = self.key_file_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Atención", "Ingresa el MagicDNS Hostname.")
            return
        args = ["cert"]
        if c_file:
            args.append(f"--cert-file={c_file}")
        if k_file:
            args.append(f"--key-file={k_file}")
        args.append(host)
        global_runner.run(args)

    def action_add_key(self):
        key = self.add_key_input.text().strip()
        if not key:
            return
        global_runner.run(["lock", "add", key], needs_sudo=True)

    def action_remove_key(self):
        key = self.rem_key_input.text().strip()
        if not key:
            return
        global_runner.run(["lock", "remove", key], needs_sudo=True)

    def action_sign_key(self):
        key = self.sign_key_input.text().strip()
        if not key:
            return
        global_runner.run(["lock", "sign", key], needs_sudo=True)

    def action_revoke_key(self):
        key = self.rev_key_input.text().strip()
        if not key:
            return
        global_runner.run(["lock", "revoke-keys", key], needs_sudo=True)

    def action_disable_global(self):
        sec = self.secret_input.text().strip()
        if not sec:
            return
        global_runner.run(["lock", "disable", sec], needs_sudo=True)
        self.secret_input.clear()
