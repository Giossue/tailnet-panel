"""
Ventana Principal de Tailnet Panel (MainWindow)
Interfaz de escritorio con vistas, componentes y tema compartidos.
"""
import os
import getpass
import json
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTabWidget, QStackedWidget, QSystemTrayIcon, QMenu,
    QApplication, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QFrame, QScrollArea, QLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

from app.config import config, APP_NAME, VERSION, IS_LINUX, set_current_user_operator, is_current_user_operator
from app.ui.theme import apply_theme
from app.ui.icons import get_icon, get_app_icon
from app.ui.components.controls import (
    AppButton, AppCheckBox, AppSpinBox, InteractionFeedback, refresh_button_icons, refresh_tab_icons,
    refresh_action_icons, set_action_icon, set_tab_icon,
)
from app.ui.components.stat_card import StatCard
from app.ui.components.status_console import StatusConsole
from app.ui.components.terminal_panel import TerminalPanel
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.preferences_view import PreferencesView
from app.ui.views.exit_node_view import ExitNodeView
from app.ui.views.diagnostics_view import DiagnosticsView
from app.ui.views.serve_funnel_view import ServeFunnelView
from app.ui.views.files_view import FilesView
from app.ui.views.ssh_view import SshView
from app.ui.views.security_view import SecurityView
from app.ui.views.accounts_view import AccountsView
from app.ui.views.appc_view import AppcView
from app.ui.views.system_view import SystemView
from app.ui.views.all_commands_view import AllCommandsView
from app.core.async_query import AsyncTailscaleQuery
from app.core.runner import global_runner, passwordless_sudo_available

def get_distro_name() -> str:
    """Obtiene el nombre amigable de la distribución Linux o sistema operativo."""
    if IS_LINUX and os.path.exists("/etc/os-release"):
        try:
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except Exception:
            pass
    return "Linux Multiplataforma"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = config.theme
        self.setWindowTitle(f"{APP_NAME} · v{VERSION}")
        self.setWindowIcon(get_app_icon(self.current_theme))
        self.resize(1180, 860)
        self.setMinimumSize(920, 640)

        # Aplicar tema inicial
        app = QApplication.instance()
        if getattr(app, "_interaction_feedback", None) is None:
            app._interaction_feedback = InteractionFeedback(app)
        apply_theme(app, self.current_theme)

        self.init_ui()
        self.init_tray()
        self.init_shortcuts()

        # Una sola consulta compartida por las vistas que muestran estado.
        self.status_query = AsyncTailscaleQuery(self)
        self.status_query.completed.connect(self._on_status_response)
        self.operator_query = AsyncTailscaleQuery(self)
        self.operator_query.completed.connect(self._on_operator_response)
        global_runner.profile_changed.connect(lambda: self.refresh_operator_status(force=True))
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_status)
        if config.auto_refresh:
            self.status_timer.start(max(2, config.refresh_interval) * 1000)
        QTimer.singleShot(0, self.refresh_status)

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(18, 14, 18, 14)
        main_v_layout.setSpacing(14)

        # ----------------- 1. Barra Superior de Marca (AppHeader) -----------------
        header_frame = QFrame()
        header_frame.setObjectName("AppHeader")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(4, 2, 4, 6)
        h_layout.setSpacing(12)

        # Marca propia del panel
        self.brand_mark = QFrame()
        self.brand_mark.setObjectName("BrandMark")
        bm_layout = QHBoxLayout(self.brand_mark)
        bm_layout.setContentsMargins(4, 4, 4, 4)
        self.brand_icon_lbl = QLabel()
        self.brand_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bm_layout.addWidget(self.brand_icon_lbl)
        self._update_brand_icon()
        h_layout.addWidget(self.brand_mark)

        # Título y Subtítulo
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        brand_title = QLabel(APP_NAME)
        brand_title.setObjectName("BrandTitle")
        title_box.addWidget(brand_title)

        self.brand_subtitle = QLabel(get_distro_name())
        self.brand_subtitle.setObjectName("BrandSubtitle")
        title_box.addWidget(self.brand_subtitle)
        h_layout.addLayout(title_box)

        h_layout.addStretch()

        # Controles superiores (Theme Switcher + Menú)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        # Botón de alternancia de tema (Sol / Luna)
        self.btn_theme = AppButton()
        self.btn_theme.setObjectName("ThemeToggleBtn")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setFixedSize(36, 36)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self._update_theme_button()
        controls_layout.addWidget(self.btn_theme)

        # Botón de opciones / configuración
        self.btn_settings = AppButton()
        self.btn_settings.set_icon("settings")
        self.btn_settings.setToolTip("Opciones y Configuración")
        self.btn_settings.setFixedSize(36, 36)
        self.btn_settings.clicked.connect(self._show_settings_menu)
        controls_layout.addWidget(self.btn_settings)

        h_layout.addLayout(controls_layout)
        main_v_layout.addWidget(header_frame)

        # ----------------- 2. Consola de Estado Hero (StatusConsole) -----------------
        self.status_console = StatusConsole(self)
        self.status_console.refresh_requested.connect(self.refresh_status)
        main_v_layout.addWidget(self.status_console)

        # ----------------- 3. Pestañas Principales No Invasivas -----------------
        self.main_tabs = QTabWidget()
        self.main_tabs.setObjectName("MainTabs")

        # Pestaña 1: Nodos (NodesTab / Dashboard)
        self.view_dashboard = DashboardView(self)
        self.view_dashboard.setObjectName("MainPage")
        self.main_tabs.addTab(self._main_tab_page(self.view_dashboard), "Nodos")
        set_tab_icon(self.main_tabs, 0, "device")

        # Pestaña 2: Catálogo de Comandos (115)
        self.view_all_commands = AllCommandsView(self)
        self.view_all_commands.setObjectName("MainPage")
        self.main_tabs.addTab(self._main_tab_page(self.view_all_commands), "Comandos")
        set_tab_icon(self.main_tabs, 1, "catalog")

        # Pestaña 3: Servicios & Red (Exit Nodes, Serve/Funnel, App Connector, Files, SSH)
        self.services_tab = QTabWidget()
        self.view_exit_node = ExitNodeView(self)
        self.view_serve_funnel = ServeFunnelView(self)
        self.view_appc = AppcView(self)
        self.view_files = FilesView(self)
        self.view_ssh = SshView(self)

        self.services_tab.addTab(self._scroll_view(self.view_exit_node), "Exit Nodes")
        set_tab_icon(self.services_tab, 0, "exit-node")
        self.services_tab.addTab(self._scroll_view(self.view_serve_funnel), "Serve && Funnel")
        set_tab_icon(self.services_tab, 1, "serve")
        self.services_tab.addTab(self._scroll_view(self.view_appc), "App Connector")
        set_tab_icon(self.services_tab, 2, "appc")
        self.services_tab.addTab(self._scroll_view(self.view_files), "Archivos (Taildrop/Drive)")
        set_tab_icon(self.services_tab, 3, "files")
        self.services_tab.addTab(self._scroll_view(self.view_ssh), "Tailscale SSH")
        set_tab_icon(self.services_tab, 4, "ssh")

        self.main_tabs.addTab(self._main_tab_page(self.services_tab), "Servicios")
        set_tab_icon(self.main_tabs, 2, "serve")

        # Pestaña 4: Configuración & Seguridad (Preferencias, Lock, Cuentas, Sistema)
        self.config_tab = QTabWidget()
        self.view_preferences = PreferencesView(self)
        self.view_security = SecurityView(self)
        self.view_accounts = AccountsView(self)
        self.view_system = SystemView(self)

        self.config_tab.addTab(self._scroll_view(self.view_preferences), "Preferencias")
        set_tab_icon(self.config_tab, 0, "preferences")
        self.config_tab.addTab(self._scroll_view(self.view_security), "Seguridad && Lock")
        set_tab_icon(self.config_tab, 1, "security")
        self.config_tab.addTab(self._scroll_view(self.view_accounts), "Cuentas && Perfiles")
        set_tab_icon(self.config_tab, 2, "accounts")
        self.config_tab.addTab(self._scroll_view(self.view_system), "Sistema && SO")
        set_tab_icon(self.config_tab, 3, "system")

        self.main_tabs.addTab(self._main_tab_page(self.config_tab), "Configuración")
        set_tab_icon(self.main_tabs, 3, "security")

        # Pestaña 5: Diagnósticos
        self.view_diagnostics = DiagnosticsView(self)
        self.main_tabs.addTab(self._main_tab_page(self._scroll_view(self.view_diagnostics)), "Diagnósticos")
        set_tab_icon(self.main_tabs, 4, "diagnostics")

        main_v_layout.addWidget(self.main_tabs, stretch=1)

        # ----------------- 4. Consola Terminal Integrada -----------------
        self.terminal_panel = TerminalPanel(self)
        main_v_layout.addWidget(self.terminal_panel)

        # Mapeo de vistas para navegación programática
        self.views_list = [
            self.view_dashboard,       # 0
            self.view_preferences,     # 1
            self.view_exit_node,       # 2
            self.view_diagnostics,     # 3
            self.view_serve_funnel,    # 4
            self.view_files,           # 5
            self.view_ssh,             # 6
            self.view_security,        # 7
            self.view_accounts,        # 8
            self.view_appc,            # 9
            self.view_system,          # 10
            self.view_all_commands     # 11
        ]

    def _main_tab_page(self, content: QWidget) -> QWidget:
        """Deja espacio entre la navegación principal y el contenido."""
        page = QWidget()
        page.setObjectName("MainTabPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(content)
        return page

    def _scroll_view(self, view: QWidget) -> QScrollArea:
        """Conserva la altura natural de los formularios al reducir la ventana."""
        scroll = QScrollArea()
        scroll.setObjectName("ViewScrollArea")
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        view.layout().setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        scroll.setWidget(view)
        return scroll

    def init_shortcuts(self):
        shortcut_f12 = QShortcut(QKeySequence("F12"), self)
        shortcut_f12.activated.connect(self.terminal_panel.toggle_collapse)

    def switch_view(self, index: int):
        """Permite navegar programáticamente a cualquiera de las 12 vistas."""
        if 0 <= index < len(self.views_list):
            if index == 0:
                self.main_tabs.setCurrentIndex(0)
            elif index == 11:
                self.main_tabs.setCurrentIndex(1)
            elif index in (2, 4, 9, 5, 6):
                self.main_tabs.setCurrentIndex(2)
                sub_map = {2: 0, 4: 1, 9: 2, 5: 3, 6: 4}
                self.services_tab.setCurrentIndex(sub_map.get(index, 0))
            elif index in (1, 7, 8, 10):
                self.main_tabs.setCurrentIndex(3)
                sub_map = {1: 0, 7: 1, 8: 2, 10: 3}
                self.config_tab.setCurrentIndex(sub_map.get(index, 0))
            elif index == 3:
                self.main_tabs.setCurrentIndex(4)

    def toggle_theme(self):
        """Alterna en vivo entre el tema Dark y Light."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.current_theme = new_theme
        config.theme = new_theme

        # Aplicar nueva hoja de estilo globalmente
        apply_theme(QApplication.instance(), new_theme)

        # Actualizar íconos y marca
        self._update_brand_icon()
        self._update_theme_button()
        refresh_button_icons(self)
        for card in self.findChildren(StatCard):
            card.refresh_theme()
        refresh_tab_icons(self)
        self.view_all_commands.filter_commands()
        self.terminal_panel.refresh_theme()
        self.setWindowIcon(get_app_icon(new_theme))
        if hasattr(self, "tray_icon"):
            self.tray_icon.setIcon(get_app_icon(new_theme))
            refresh_action_icons(self.tray_icon.contextMenu())

        # Refrescar consola de estado
        self.status_console._update_appearance()
        if self.view_dashboard.cached_status:
            self.view_dashboard.refresh_data()

    def _update_theme_button(self):
        if self.current_theme == "dark":
            self.btn_theme.set_icon("sun")
            self.btn_theme.setToolTip("Cambiar a Modo Claro")
        else:
            self.btn_theme.set_icon("moon")
            self.btn_theme.setToolTip("Cambiar a Modo Oscuro")

    def _update_brand_icon(self):
        self.brand_icon_lbl.setPixmap(get_app_icon().pixmap(28, 28))

    def refresh_status(self):
        """Consulta el estado de forma asíncrona."""
        self.status_query.run(["status", "--json"])
        self.refresh_operator_status()

    def refresh_operator_status(self, force=False):
        if force:
            self.operator_query.cancel()
        self.operator_query.run(["get", "operator"])

    def _on_operator_response(self, output):
        set_current_user_operator(output or "")
        has_access = is_current_user_operator() or (
            IS_LINUX and not config.force_no_sudo
            and passwordless_sudo_available(config.tailscale_path)
        )
        self.view_dashboard.operator_frame.setVisible(not has_access)

    def _on_status_response(self, output):
        try:
            status = json.loads(output) if output else None
        except (TypeError, ValueError):
            status = None

        self.view_dashboard.apply_status(status)
        self.view_ssh.apply_status(status)
        self.view_exit_node.apply_status(status)
        if not status:
            self.status_console.set_status(False, "", "", state_label="Tailscale no disponible")
            return

        backend_state = status.get("BackendState", "Stopped")
        is_running = (backend_state == "Running")
        self_info = status.get("Self") or {}
        hostname = self_info.get("HostName", "Tailscale")
        ts_ips = self_info.get("TailscaleIPs") or []
        primary_ip = ts_ips[0] if ts_ips else ""

        peer_dict = status.get("Peer") or {}
        total_peers = len(peer_dict)
        online_peers = sum(
            1 for p in peer_dict.values()
            if p and (p.get("Active", False) or p.get("Online", False))
        )

        self.status_console.set_status(
            connected=is_running,
            hostname=hostname,
            ip=primary_ip,
            total_nodes=total_peers,
            online_nodes=online_peers,
            state_label={
                "Stopped": "Tailscale detenido",
                "NeedsLogin": "Inicia sesión en Tailscale",
            }.get(backend_state, "Tailscale desconectado"),
        )

    def _show_settings_menu(self):
        menu = QMenu(self)
        act_config = menu.addAction("Configuración de la Aplicación...")
        set_action_icon(act_config, "settings")
        act_config.triggered.connect(self.open_settings_dialog)

        act_web = menu.addAction("Administración local (Web)")
        set_action_icon(act_web, "web")
        act_web.triggered.connect(lambda: global_runner.run(["web"]))

        menu.addSeparator()

        act_up = menu.addAction("Conectar (tailscale up)")
        set_action_icon(act_up, "connect")
        act_up.triggered.connect(lambda: global_runner.run(["up"], needs_sudo=True))

        act_down = menu.addAction("Desconectar (tailscale down)")
        set_action_icon(act_down, "disconnect")
        act_down.triggered.connect(lambda: global_runner.run(["down"], needs_sudo=True))

        menu.addSeparator()

        act_quit = menu.addAction("Salir")
        set_action_icon(act_quit, "cancel")
        act_quit.triggered.connect(QApplication.instance().quit)

        menu.exec(self.btn_settings.mapToGlobal(self.btn_settings.rect().bottomLeft()))

    def open_settings_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Configuración de {APP_NAME}")
        dlg.setMinimumWidth(520)
        layout = QVBoxLayout(dlg)
        form = QFormLayout()

        tailscale_path_in = QLineEdit(config.tailscale_path)
        form.addRow("Ruta del binario Tailscale:", tailscale_path_in)

        custom_socket_in = QLineEdit(config.custom_socket)
        custom_socket_in.setPlaceholderText("Dejar vacío para el socket por defecto")
        form.addRow("Socket personalizado (--socket):", custom_socket_in)

        refresh_spin = AppSpinBox()
        refresh_spin.setRange(2, 60)
        refresh_spin.setValue(config.refresh_interval)
        refresh_spin.setSuffix(" seg")
        form.addRow("Intervalo de refresco:", refresh_spin)

        no_sudo_cb = AppCheckBox("No elevar comandos (solo si mi cuenta ya tiene permisos)")
        no_sudo_cb.setChecked(config.force_no_sudo)
        form.addRow(no_sudo_cb)

        auto_refresh_cb = AppCheckBox("Actualizar el estado automáticamente")
        auto_refresh_cb.setChecked(config.auto_refresh)
        form.addRow(auto_refresh_cb)

        layout.addLayout(form)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_save = AppButton("Guardar")
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(lambda: self._save_config(dlg, tailscale_path_in.text(), custom_socket_in.text(), refresh_spin.value(), no_sudo_cb.isChecked(), auto_refresh_cb.isChecked()))
        btn_cancel = AppButton("Cancelar")
        btn_cancel.clicked.connect(dlg.reject)
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

        dlg.exec()

    def _save_config(self, dlg, path, socket, interval, no_sudo, auto_refresh):
        config.tailscale_path = path.strip()
        config.custom_socket = socket.strip()
        config.refresh_interval = interval
        config.force_no_sudo = no_sudo
        config.auto_refresh = auto_refresh
        set_current_user_operator("")
        self.status_query.cancel()
        self.operator_query.cancel()
        if auto_refresh:
            self.status_timer.start(max(2, interval) * 1000)
        else:
            self.status_timer.stop()
        self.refresh_status()
        self.refresh_operator_status()
        dlg.accept()
        QMessageBox.information(self, "Configuración guardada", "Los ajustes han sido actualizados con éxito.")

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(get_app_icon(self.current_theme))
        self.tray_icon.setToolTip(f"{APP_NAME} v{VERSION}")

        tray_menu = QMenu()
        act_show = tray_menu.addAction("Mostrar Panel")
        set_action_icon(act_show, "tailscale")
        act_show.triggered.connect(self.show_and_raise)

        tray_menu.addSeparator()

        act_up = tray_menu.addAction("Conectar (Up)")
        set_action_icon(act_up, "connect")
        act_up.triggered.connect(lambda: global_runner.run(["up"], needs_sudo=True))

        act_down = tray_menu.addAction("Desconectar (Down)")
        set_action_icon(act_down, "disconnect")
        act_down.triggered.connect(lambda: global_runner.run(["down"], needs_sudo=True))

        tray_menu.addSeparator()

        act_quit = tray_menu.addAction("Salir")
        set_action_icon(act_quit, "cancel")
        act_quit.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_and_raise()

    def closeEvent(self, event):
        self.status_timer.stop()
        for query in self.findChildren(AsyncTailscaleQuery):
            query.cancel()
        if global_runner.is_running():
            global_runner.cancel()
        self.tray_icon.hide()
        super().closeEvent(event)
