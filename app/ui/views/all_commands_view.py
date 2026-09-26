"""
Explorador Maestro de los 115 Comandos de Tailscale CLI con buscador, filtros y ejecución directa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QApplication, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from app.core.command_registry import ALL_COMMANDS, CATEGORIES, CommandInfo
from app.ui.components.command_dialog import CommandDialog
from app.core.runner import global_runner, requires_system_elevation
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppComboBox, TableActionButton, table_action_cell, configure_action_table
from app.config import config
from app.ui.theme import get_theme_colors

class AllCommandsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.populate_table(ALL_COMMANDS)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Encabezado
        header_frame = QFrame()
        header_frame.setProperty("class", "card")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(12, 10, 12, 10)

        title_lbl = QLabel("<b>Catálogo de Comandos Tailscale CLI (115 Comandos)</b>")
        title_lbl.setStyleSheet("background: transparent; font-size: 15px; font-weight: 700;")
        h_layout.addWidget(title_lbl)

        h_layout.addStretch()

        self.lbl_count = QLabel("115 de 115 comandos")
        self.lbl_count.setProperty("class", "muted-copy")
        h_layout.addWidget(self.lbl_count)

        layout.addWidget(header_frame)

        # Mosaico de Comandos Rápidos (Inspirado en CommandsTab de Tailscale Control)
        quick_bar = QHBoxLayout()
        quick_bar.setSpacing(8)

        quick_cmds = [
            ("Estado", "status", ["status"]),
            ("Mis IPs", "globe", ["ip"]),
            ("Netcheck", "diagnostics", ["netcheck"]),
            ("DNS Resolved", "dns", ["dns", "query", "tailscale.com"]),
            ("Versión", "version", ["version"]),
            ("WhoAmI", "user", ["whoami"])
        ]

        for label, icon_name, args in quick_cmds:
            btn_q = AppButton(f" {label}")
            btn_q.set_icon(icon_name)
            btn_q.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_q.clicked.connect(lambda ch, a=args: global_runner.run(a))
            quick_bar.addWidget(btn_q)

        quick_bar.addStretch()
        layout.addLayout(quick_bar)

        # Barra de búsqueda y filtrado
        filter_bar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por número (#1..#115), comando, flag o descripción...")
        self.search_input.textChanged.connect(self.filter_commands)
        filter_bar.addWidget(self.search_input)

        filter_bar.addWidget(QLabel("Categoría:"))
        self.category_combo = AppComboBox()
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.currentTextChanged.connect(self.filter_commands)
        filter_bar.addWidget(self.category_combo)

        btn_reset_filters = AppButton("Limpiar Filtro")
        btn_reset_filters.set_icon("clean")
        btn_reset_filters.clicked.connect(self.reset_filters)
        filter_bar.addWidget(btn_reset_filters)

        layout.addLayout(filter_bar)

        # Tabla de 115 comandos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "#", "Comando CLI", "Categoría", "Función / Descripción", "Permiso", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        configure_action_table(self.table)

        layout.addWidget(self.table)

    def populate_table(self, command_list):
        self.table.setRowCount(len(command_list))
        for row, cmd in enumerate(command_list):
            # ID
            id_item = QTableWidgetItem(f"#{cmd.id}")
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            colors = get_theme_colors(config.theme)
            id_item.setForeground(QColor(colors["accent"]))
            self.table.setItem(row, 0, id_item)

            # Nombre CLI
            name_item = QTableWidgetItem(cmd.name)
            name_item.setFont(self.table.font())
            self.table.setItem(row, 1, name_item)

            # Categoría
            cat_item = QTableWidgetItem(cmd.category)
            self.table.setItem(row, 2, cat_item)

            # Descripción
            desc_item = QTableWidgetItem(cmd.description)
            desc_item.setToolTip(f"Ejemplo: {cmd.example}\n\nRef: {cmd.doc_ref}")
            self.table.setItem(row, 3, desc_item)

            # Mostrar el permiso requerido, no el mecanismo de elevación.
            sudo_text = (
                "Sistema" if cmd.needs_sudo and requires_system_elevation(cmd.base_args)
                else "Operador" if cmd.needs_sudo else "Normal"
            )
            sudo_item = QTableWidgetItem(sudo_text)
            if cmd.needs_sudo:
                sudo_item.setIcon(get_icon("lock", role="warning"))
                sudo_item.setForeground(QColor(colors["warning"]))
            else:
                sudo_item.setForeground(QColor(colors["muted"]))
            sudo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, sudo_item)

            # Contenedor de botones de acción
            btn_run = TableActionButton("Configurar", "settings")
            btn_run.clicked.connect(lambda checked, c=cmd: self.open_command_dialog(c))

            btn_copy = TableActionButton("", "copy")
            btn_copy.setToolTip(f"Copiar ejemplo: {cmd.example}")
            btn_copy.clicked.connect(lambda checked, ex=cmd.example: self.copy_example(ex))
            self.table.setCellWidget(row, 5, table_action_cell(btn_run, btn_copy))

        self.lbl_count.setText(f"{len(command_list)} de {len(ALL_COMMANDS)} comandos mostrados")

    def filter_commands(self):
        query = self.search_input.text().lower().strip()
        selected_cat = self.category_combo.currentText()

        filtered = []
        for cmd in ALL_COMMANDS:
            if selected_cat != "Todos" and cmd.category != selected_cat:
                continue

            if query:
                id_str = f"#{cmd.id}"
                id_num = str(cmd.id)
                match = (
                    query in id_str or
                    query == id_num or
                    query in cmd.name.lower() or
                    query in cmd.description.lower() or
                    query in cmd.example.lower() or
                    query in cmd.category.lower()
                )
                if not match:
                    continue

            filtered.append(cmd)

        self.populate_table(filtered)

    def reset_filters(self):
        self.search_input.clear()
        self.category_combo.setCurrentText("Todos")
        self.populate_table(ALL_COMMANDS)

    def open_command_dialog(self, cmd: CommandInfo):
        dlg = CommandDialog(cmd, self)
        dlg.exec()

    def copy_example(self, example_cmd: str):
        QApplication.clipboard().setText(example_cmd)
        QMessageBox.information(self, "Copiado", f"Comando copiado al portapapeles:\n\n{example_cmd}")
