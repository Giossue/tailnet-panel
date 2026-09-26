"""
Vista de Preferencias y Configuración (Comandos: get, get all, get <option>, get --json, set, syspolicy).
"""
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QGroupBox, QFormLayout, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from app.core.command_registry import COMMANDS_BY_ID
from app.ui.components.command_dialog import CommandDialog
from app.core.async_query import AsyncTailscaleQuery
from app.core.runner import global_runner
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppComboBox, set_tab_icon

class PreferencesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.preferences_query = AsyncTailscaleQuery(self)
        self.preferences_query.completed.connect(self._on_preferences_response)
        self.refresh_get_tree()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # Pestaña 1: Configurar Opciones (Set)
        tab_set = QWidget()
        set_layout = QVBoxLayout(tab_set)
        set_layout.setSpacing(14)

        group_quick_set = QGroupBox("Preferencias del dispositivo")
        form_quick = QFormLayout(group_quick_set)
        form_quick.setSpacing(10)

        # Hostname
        row_host = QHBoxLayout()
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Nuevo nombre de host para este equipo")
        self.btn_set_host = AppButton("Guardar nombre")
        self.btn_set_host.clicked.connect(self.action_set_hostname)
        row_host.addWidget(self.host_input)
        row_host.addWidget(self.btn_set_host)
        form_quick.addRow("Nombre del equipo:", row_host)

        # Advertise Routes
        row_routes = QHBoxLayout()
        self.routes_input = QLineEdit()
        self.routes_input.setPlaceholderText("Ej: 192.168.1.0/24, 10.0.0.0/16")
        self.btn_set_routes = AppButton("Anunciar Rutas")
        self.btn_set_routes.clicked.connect(self.action_set_routes)
        row_routes.addWidget(self.routes_input)
        row_routes.addWidget(self.btn_set_routes)
        form_quick.addRow("Anunciar Subredes:", row_routes)

        # Shields Up
        row_shields = QHBoxLayout()
        self.btn_shields_on = AppButton("Activar Shields-Up")
        self.btn_shields_on.set_icon("shield-on")
        self.btn_shields_on.clicked.connect(lambda: global_runner.run(["set", "--shields-up=true"], needs_sudo=True))
        self.btn_shields_off = AppButton("Desactivar Shields-Up")
        self.btn_shields_off.set_icon("shield")
        self.btn_shields_off.clicked.connect(lambda: global_runner.run(["set", "--shields-up=false"], needs_sudo=True))
        row_shields.addWidget(self.btn_shields_on)
        row_shields.addWidget(self.btn_shields_off)
        row_shields.addStretch()
        form_quick.addRow("Bloqueo Entrante:", row_shields)

        # Tailscale SSH Server
        row_ssh = QHBoxLayout()
        self.btn_ssh_on = AppButton("Habilitar Tailscale SSH")
        self.btn_ssh_on.set_icon("ssh")
        self.btn_ssh_on.clicked.connect(lambda: global_runner.run(["set", "--ssh=true"], needs_sudo=True))
        self.btn_ssh_off = AppButton("Deshabilitar SSH")
        self.btn_ssh_off.set_icon("times")
        self.btn_ssh_off.clicked.connect(lambda: global_runner.run(["set", "--ssh=false"], needs_sudo=True))
        row_ssh.addWidget(self.btn_ssh_on)
        row_ssh.addWidget(self.btn_ssh_off)
        row_ssh.addStretch()
        form_quick.addRow("Servidor SSH:", row_ssh)

        set_layout.addWidget(group_quick_set)

        # Botón para diálogo completo de 'set' con todos los flags
        more_set_layout = QHBoxLayout()
        btn_full_set = AppButton("Opciones avanzadas")
        btn_full_set.set_icon("settings")
        btn_full_set.clicked.connect(lambda: CommandDialog(COMMANDS_BY_ID[76], self).exec())
        more_set_layout.addWidget(btn_full_set)
        more_set_layout.addStretch()
        set_layout.addLayout(more_set_layout)
        set_layout.addStretch()

        tabs.addTab(tab_set, "Modificar")
        set_tab_icon(tabs, 0, "settings")

        # Pestaña 2: Consultar Preferencias (Get)
        tab_get = QWidget()
        get_layout = QVBoxLayout(tab_get)

        get_toolbar = QHBoxLayout()
        self.btn_refresh_get = AppButton("Actualizar")
        self.btn_refresh_get.set_icon("refresh")
        self.btn_refresh_get.clicked.connect(self.refresh_get_tree)
        get_toolbar.addWidget(self.btn_refresh_get)

        self.btn_get_all = AppButton("Ver todas")
        self.btn_get_all.set_icon("file")
        self.btn_get_all.clicked.connect(lambda: global_runner.run(["get", "all"]))
        get_toolbar.addWidget(self.btn_get_all)

        get_toolbar.addStretch()

        get_toolbar.addWidget(QLabel("Consultar opción específica:"))
        self.combo_option = AppComboBox()
        self.combo_option.addItems(["accept-routes", "accept-dns", "advertise-exit-node", "advertise-routes", "exit-node", "shields-up", "ssh", "hostname"])
        get_toolbar.addWidget(self.combo_option)

        btn_query_opt = AppButton("Consultar")
        btn_query_opt.set_icon("search")
        btn_query_opt.clicked.connect(lambda: global_runner.run(["get", self.combo_option.currentText()]))
        get_toolbar.addWidget(btn_query_opt)

        get_layout.addLayout(get_toolbar)

        self.tree_get = QTreeWidget()
        self.tree_get.setHeaderLabels(["Propiedad", "Valor"])
        self.tree_get.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_get.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        get_layout.addWidget(self.tree_get)

        tabs.addTab(tab_get, "Consultar")
        set_tab_icon(tabs, 1, "search")

        # Pestaña 3: Políticas de Sistema (Syspolicy)
        tab_policy = QWidget()
        pol_layout = QVBoxLayout(tab_policy)

        pol_toolbar = QHBoxLayout()
        btn_pol_list = AppButton("Listar políticas")
        btn_pol_list.set_icon("license")
        btn_pol_list.clicked.connect(lambda: global_runner.run(["syspolicy", "list"]))
        pol_toolbar.addWidget(btn_pol_list)

        btn_pol_reload = AppButton("Recargar políticas")
        btn_pol_reload.set_icon("refresh")
        btn_pol_reload.clicked.connect(lambda: global_runner.run(["syspolicy", "reload"]))
        pol_toolbar.addWidget(btn_pol_reload)

        pol_toolbar.addStretch()
        pol_layout.addLayout(pol_toolbar)

        pol_desc = QLabel(
            "Las políticas del sistema permiten a los administradores de red aplicar configuraciones "
            "centralizadas y de solo lectura a los clientes mediante MDM o archivos del sistema operativo."
        )
        pol_desc.setWordWrap(True)
        pol_desc.setProperty("class", "muted-copy")
        pol_layout.addWidget(pol_desc)
        pol_layout.addStretch()

        tabs.addTab(tab_policy, "Políticas")
        set_tab_icon(tabs, 2, "license")

        layout.addWidget(tabs)
    def action_set_hostname(self):
        new_name = self.host_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Atención", "Escribe un nombre de host válido.")
            return
        global_runner.run(["set", f"--hostname={new_name}"], needs_sudo=True)

    def action_set_routes(self):
        routes = self.routes_input.text().strip()
        if not routes:
            QMessageBox.warning(self, "Atención", "Escribe las subredes a anunciar.")
            return
        global_runner.run(["set", f"--advertise-routes={routes}"], needs_sudo=True)

    def refresh_get_tree(self):
        self.preferences_query.run(["get", "--json"])

    def _on_preferences_response(self, output):
        self.tree_get.clear()
        try:
            data = json.loads(output) if output else None
        except (TypeError, ValueError):
            data = None
        if not data:
            item = QTreeWidgetItem(self.tree_get, ["Estado", "No se pudieron obtener preferencias (¿Tailscale está iniciado?)"])
            return

        def add_dict(parent, d):
            for k, v in d.items():
                if isinstance(v, dict):
                    child = QTreeWidgetItem(parent, [str(k), ""])
                    add_dict(child, v)
                elif isinstance(v, list):
                    child = QTreeWidgetItem(parent, [str(k), f"[{len(v)} elementos]"])
                    for i, elem in enumerate(v):
                        QTreeWidgetItem(child, [str(i), str(elem)])
                else:
                    QTreeWidgetItem(parent, [str(k), str(v)])

        add_dict(self.tree_get, data)
        self.tree_get.expandAll()
