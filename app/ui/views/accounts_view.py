"""
Vista de Cuentas y Fast User Switching (Comandos: login, logout, switch).
"""
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QGroupBox, QFormLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton
from app.core.runner import global_runner
from app.core.async_query import AsyncTailscaleQuery

class AccountsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.accounts_query = AsyncTailscaleQuery(self)
        self.accounts_query.completed.connect(self._on_accounts_response)
        self._switch_in_progress = False
        global_runner.finished.connect(self._on_command_finished)
        self.refresh_accounts()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # ----------------- Sección 1: Cuentas Locales (Switch) -----------------
        switch_box = QGroupBox("Cambio Rápido de Cuenta / Fast User Switching (tailscale switch)")
        switch_layout = QVBoxLayout(switch_box)

        bar_switch = QHBoxLayout()
        btn_list_switch = AppButton("Actualizar Lista")
        btn_list_switch.set_icon("refresh")
        btn_list_switch.clicked.connect(self.refresh_accounts)
        bar_switch.addWidget(btn_list_switch)

        self.account_target_input = QLineEdit()
        self.account_target_input.setPlaceholderText("Nombre de cuenta o ID para cambiar/remover...")
        bar_switch.addWidget(self.account_target_input)

        btn_do_switch = AppButton("Cambiar a Cuenta")
        btn_do_switch.set_icon("switch")
        btn_do_switch.setProperty("class", "btn-primary")
        btn_do_switch.clicked.connect(self.action_switch)
        bar_switch.addWidget(btn_do_switch)

        btn_rem_switch = AppButton("Remover Cuenta")
        btn_rem_switch.set_icon("trash")
        btn_rem_switch.setProperty("class", "btn-danger")
        btn_rem_switch.clicked.connect(self.action_remove_account)
        bar_switch.addWidget(btn_rem_switch)

        switch_layout.addLayout(bar_switch)

        self.accounts_list_widget = QListWidget()
        self.accounts_list_widget.currentItemChanged.connect(self._on_account_selected)
        switch_layout.addWidget(self.accounts_list_widget)

        layout.addWidget(switch_box)

        # ----------------- Sección 2: Inicio de Sesión (Login) -----------------
        login_box = QGroupBox("Autenticación y Nuevo Inicio de Sesión (tailscale login)")
        login_form = QFormLayout(login_box)
        login_form.setSpacing(10)

        btn_login_interactive = AppButton("Iniciar Sesión Interactivo")
        btn_login_interactive.set_icon("globe")
        btn_login_interactive.clicked.connect(lambda: global_runner.run(["login"], needs_sudo=True))
        login_form.addRow("Inicio Web Interactivo:", btn_login_interactive)

        auth_row = QHBoxLayout()
        self.auth_key_input = QLineEdit()
        self.auth_key_input.setPlaceholderText("tskey-auth-...")
        self.auth_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        btn_login_key = AppButton("Iniciar con Auth Key")
        btn_login_key.set_icon("key")
        btn_login_key.setProperty("class", "btn-primary")
        btn_login_key.clicked.connect(self.action_login_key)
        auth_row.addWidget(self.auth_key_input)
        auth_row.addWidget(btn_login_key)
        login_form.addRow("Auth Key Preautorizada:", auth_row)

        layout.addWidget(login_box)

        # ----------------- Sección 3: Cierre de Sesión (Logout) -----------------
        logout_box = QGroupBox("Cierre de Sesión (tailscale logout)")
        lo_layout = QHBoxLayout(logout_box)

        lo_desc = QLabel("Cierra la sesión del dispositivo actual en el tailnet, requiriendo reautenticación.")
        lo_desc.setProperty("class", "muted-copy")
        lo_desc.setWordWrap(True)
        lo_layout.addWidget(lo_desc)

        btn_logout = AppButton("Cerrar Sesión (Logout)")
        btn_logout.set_icon("logout")
        btn_logout.setProperty("class", "btn-danger")
        btn_logout.clicked.connect(self.action_logout)
        lo_layout.addWidget(btn_logout)

        layout.addWidget(logout_box)
        layout.addStretch()

    def refresh_accounts(self):
        self.accounts_query.run(["switch", "--list", "--json"])

    def _on_accounts_response(self, output):
        self.accounts_list_widget.clear()
        if not output:
            return
        try:
            accounts = json.loads(output)
        except (TypeError, ValueError):
            return
        if not isinstance(accounts, list):
            return
        for account in accounts:
            if not isinstance(account, dict):
                continue
            account_id = str(account.get("id") or "").strip()
            if not account_id:
                continue
            name = str(account.get("account") or account.get("nickname") or account_id).strip()
            tailnet = str(account.get("tailnet") or "").strip()
            label = name if not tailnet or tailnet == name else f"{name} · {tailnet}"
            label = f"{label}  ·  ID {account_id}"
            if account.get("selected"):
                label = f"Actual · {label}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, account_id)
            if account.get("selected"):
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.accounts_list_widget.addItem(item)

    def _on_account_selected(self, current, _previous):
        account_id = current.data(Qt.ItemDataRole.UserRole) if current else ""
        self.account_target_input.setText(str(account_id or ""))

    def action_switch(self):
        target = self.account_target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Escribe o selecciona la cuenta.")
            return
        if not global_runner.is_running():
            self._switch_in_progress = True
        global_runner.run(["switch", target], needs_sudo=True)

    def _on_command_finished(self, result):
        if self._switch_in_progress:
            self._switch_in_progress = False
            if result.success:
                self.refresh_accounts()

    def action_remove_account(self):
        target = self.account_target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Atención", "Escribe o selecciona el ID de la cuenta a remover.")
            return
        global_runner.run(["switch", "remove", target], needs_sudo=True)

    def action_login_key(self):
        key = self.auth_key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Atención", "Por favor ingresa la Auth Key.")
            return
        global_runner.run(["login", f"--auth-key={key}"], needs_sudo=True)
        self.auth_key_input.clear()

    def action_logout(self):
        reply = QMessageBox.question(
            self, "Confirmar Logout",
            "¿Estás seguro de que deseas cerrar sesión en Tailscale? Necesitarás volver a autenticarte.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            global_runner.run(["logout"], needs_sudo=True)
