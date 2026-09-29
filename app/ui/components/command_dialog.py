"""
Diálogo modal dinámico para configurar parámetros y ejecutar cualquier comando de Tailscale.
"""
from typing import Dict, Any, List
from html import escape
import shutil
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget,
    QComboBox, QFileDialog, QScrollArea, QFrame, QLayout,
    QFormLayout, QGroupBox, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt
from app.core.command_registry import CommandInfo, CommandParam
from app.core.runner import global_runner, redact_arguments, requires_system_elevation, passwordless_sudo_available
from app.config import config, IS_LINUX, IS_MACOS, is_current_user_operator
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppCheckBox, AppComboBox, AppSpinBox

class CommandDialog(QDialog):
    def __init__(self, cmd_info: CommandInfo, parent=None):
        super().__init__(parent)
        self.cmd_info = cmd_info
        self.operator_mode = (
            IS_LINUX
            and cmd_info.needs_sudo
            and not requires_system_elevation(cmd_info.base_args)
            and is_current_user_operator()
        )
        self.passwordless_mode = (
            IS_LINUX and cmd_info.needs_sudo and not self.operator_mode
            and not config.force_no_sudo
            and passwordless_sudo_available(config.tailscale_path)
        )
        self.param_widgets: Dict[str, Any] = {}
        self.setWindowTitle(f"Comando #{cmd_info.id}: {cmd_info.name}")
        self.setWindowIcon(get_icon("settings"))
        self.setMinimumWidth(550)
        self.init_ui()
        self.update_preview()

        screen = self.screen() or QApplication.primaryScreen()
        available_height = screen.availableGeometry().height() - 48 if screen else 760
        if parent is not None:
            available_height = min(available_height, parent.window().height() - 40)
        self.setMaximumHeight(max(360, available_height))
        outer = self.layout()
        margins = outer.contentsMargins()
        footer_height = self.action_layout.sizeHint().height()
        preview_height = self.preview_group.sizeHint().height()
        usable_height = (self.maximumHeight() - margins.top() - margins.bottom()
                         - 2 * outer.spacing() - preview_height - footer_height)
        self.content_scroll.setMinimumHeight(min(self.content_scroll.widget().sizeHint().height(), usable_height))

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        scroll = QScrollArea()
        scroll.setObjectName("CommandDialogScroll")
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("CommandDialogContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)
        content_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        scroll.setWidget(content)
        self.content_scroll = scroll
        layout.addWidget(scroll, stretch=1)

        # Encabezado
        header = QVBoxLayout()
        title_lbl = QLabel(
            f"<b>#{self.cmd_info.id}</b> &nbsp; <code>{escape(self.cmd_info.name)}</code>"
        )
        title_lbl.setTextFormat(Qt.TextFormat.RichText)
        title_lbl.setObjectName("CommandTitle")
        header.addWidget(title_lbl)

        desc_lbl = QLabel(self.cmd_info.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setProperty("class", "muted-copy")
        header.addWidget(desc_lbl)

        if self.cmd_info.needs_sudo:
            sudo_box = QHBoxLayout()
            sudo_box.setSpacing(6)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(get_icon("lock").pixmap(14, 14))
            notice = (
                "Este comando se ejecutará sin autorización adicional."
                if self.operator_mode or self.passwordless_mode else
                "El sistema puede solicitar autorización para ejecutar este comando."
            )
            sudo_notice = QLabel(notice)
            sudo_notice.setProperty("class", "muted-copy")
            sudo_box.addWidget(icon_lbl)
            sudo_box.addWidget(sudo_notice)
            sudo_box.addStretch()
            header.addLayout(sudo_box)

        content_layout.addLayout(header)

        # Formulario de parámetros
        if self.cmd_info.params:
            group = QGroupBox("Parámetros y Opciones")
            form = QFormLayout(group)
            form.setSpacing(8)

            for param in self.cmd_info.params:
                w = self._create_widget_for_param(param)
                self.param_widgets[param.name] = (param, w)
                label_text = param.label + (" *" if param.required else "")
                form.addRow(label_text, w)

            content_layout.addWidget(group)

        # Vista previa del comando generado
        preview_group = QGroupBox("Vista Previa del Comando CLI")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_lbl = QLabel()
        self.preview_lbl.setObjectName("CommandPreview")
        self.preview_lbl.setTextFormat(Qt.TextFormat.PlainText)
        self.preview_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.preview_lbl.setWordWrap(True)
        preview_layout.addWidget(self.preview_lbl)
        self.preview_group = preview_group
        layout.addWidget(preview_group)

        # Botones de acción
        btn_layout = QHBoxLayout()
        self.btn_copy = AppButton("Copiar CLI")
        self.btn_copy.set_icon("copy")
        self.btn_copy.clicked.connect(self.copy_command)
        btn_layout.addWidget(self.btn_copy)

        btn_layout.addStretch()

        self.btn_cancel = AppButton("Cancelar")
        self.btn_cancel.set_icon("cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_run = AppButton("Ejecutar Comando")
        self.btn_run.set_icon("play")
        self.btn_run.setProperty("class", "btn-primary")
        self.btn_run.clicked.connect(self.run_command)
        btn_layout.addWidget(self.btn_run)

        self.action_layout = btn_layout
        layout.addLayout(btn_layout)

    def _create_widget_for_param(self, param: CommandParam):
        if param.param_type == "bool":
            cb = AppCheckBox("Activar")
            cb.setChecked(bool(param.default))
            cb.toggled.connect(self.update_preview)
            return cb
        elif param.param_type == "choice":
            combo = AppComboBox()
            combo.addItems(param.choices)
            if param.default in param.choices:
                combo.setCurrentText(str(param.default))
            combo.currentTextChanged.connect(self.update_preview)
            return combo
        elif param.param_type == "int":
            spin = AppSpinBox()
            spin.setRange(0, 65535)
            try:
                spin.setValue(int(param.default))
            except ValueError:
                spin.setValue(0)
            spin.valueChanged.connect(self.update_preview)
            return spin
        elif param.param_type in ("file", "dir"):
            container = QWidget()
            row = QHBoxLayout(container)
            row.setContentsMargins(0, 0, 0, 0)
            edit = QLineEdit(str(param.default))
            edit.textChanged.connect(self.update_preview)
            btn = AppButton("Explorar...")
            if param.param_type == "file":
                btn.clicked.connect(lambda: self._browse_file(edit))
            else:
                btn.clicked.connect(lambda: self._browse_dir(edit))
            row.addWidget(edit)
            row.addWidget(btn)
            container.edit_field = edit  # Guardar referencia
            return container
        else:
            edit = QLineEdit(str(param.default))
            if param.name in ("auth_key", "authkey", "secret"):
                edit.setEchoMode(QLineEdit.EchoMode.Password)
            if param.help_text:
                edit.setPlaceholderText(param.help_text)
            edit.textChanged.connect(self.update_preview)
            return edit

    def _browse_file(self, edit_widget: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo")
        if path:
            edit_widget.setText(path)

    def _browse_dir(self, edit_widget: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if path:
            edit_widget.setText(path)

    def build_args(self) -> List[str]:
        args = list(self.cmd_info.base_args)

        for param_name, (param, widget) in self.param_widgets.items():
            if param.param_type == "bool":
                if widget.isChecked():
                    flag = param.flag_format.replace("{val}", "true")
                    if flag:
                        args.append(flag)
            elif param.param_type == "choice":
                val = widget.currentText()
                if val != "unchanged":
                    flag = param.flag_format.replace("{val}", val)
                    if flag:
                        args.append(flag)
            elif param.param_type == "int":
                val = str(widget.value())
                flag = param.flag_format.replace("{val}", val)
                if flag:
                    args.append(flag)
            elif param.param_type in ("file", "dir"):
                val = widget.edit_field.text().strip()
                if val:
                    flag = param.flag_format.replace("{val}", val)
                    if flag:
                        args.append(flag)
            else:
                val = widget.text().strip()
                if val:
                    flag = param.flag_format.replace("{val}", val)
                    if flag:
                        args.append(flag)

        return args

    def update_preview(self):
        args = self.build_args()
        display_args = redact_arguments(args)
        ts = "tailscale"
        if self.cmd_info.needs_sudo and not self.operator_mode and not config.force_no_sudo and (IS_LINUX or IS_MACOS):
            if self.passwordless_mode:
                ts = "sudo -n tailscale"
            else:
                ts = "pkexec tailscale" if IS_LINUX and config.use_pkexec and shutil.which("pkexec") else "sudo tailscale"
        if config.custom_socket:
            cmd_preview = f"{ts} --socket={config.custom_socket} {' '.join(display_args)}"
        else:
            cmd_preview = f"{ts} {' '.join(display_args)}"
        self.preview_lbl.setText(cmd_preview)
        self.btn_copy.setEnabled(args == display_args)
        self.btn_copy.setToolTip(
            "" if args == display_args else "La vista previa oculta secretos y no se puede copiar."
        )

    def copy_command(self):
        QApplication.clipboard().setText(self.preview_lbl.text())
        QMessageBox.information(self, "Copiado", "Comando CLI copiado al portapapeles.")

    def run_command(self):
        args = self.build_args()
        # Verificar campos obligatorios
        for param in self.cmd_info.params:
            if param.required:
                _, widget = self.param_widgets[param.name]
                val = ""
                if hasattr(widget, "text"):
                    val = widget.text().strip()
                elif isinstance(widget, QComboBox):
                    val = widget.currentText().strip()
                elif hasattr(widget, "edit_field"):
                    val = widget.edit_field.text().strip()
                if not val:
                    QMessageBox.warning(self, "Campo requerido", f"El campo '{param.label}' es obligatorio.")
                    return

        if self.cmd_info.is_interactive:
            # Lanzar en terminal externa si es interactivo (ej: ssh, nc)
            launched = global_runner.launch_in_external_terminal(args, window_title=self.cmd_info.name)
            if not launched:
                # Si no pudo lanzar terminal externa, ejecutar con global_runner
                global_runner.run(args, needs_sudo=self.cmd_info.needs_sudo)
        else:
            global_runner.run(args, needs_sudo=self.cmd_info.needs_sudo)

        for name in ("auth_key", "authkey", "secret"):
            entry = self.param_widgets.get(name)
            if entry:
                entry[1].clear()
        self.accept()
