"""
Panel de terminal integrado y colapsable para visualizar la salida de comandos.
Inspirado en OutputConsole de Tailscale Control con soporte de colapso rápido.
"""
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextCursor
from html import escape
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, AppCheckBox
from app.core.runner import global_runner, CommandResult
from app.config import config
from app.ui.theme import get_theme_colors

class TerminalPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TerminalPanel")
        self.auto_scroll = True
        self.is_collapsed = False
        self._entries = []
        self.init_ui()
        self.setup_connections()
        self.toggle_collapse()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de encabezado del terminal (TerminalHeader)
        self.header_frame = QFrame()
        self.header_frame.setObjectName("TerminalHeader")
        toolbar = QHBoxLayout(self.header_frame)
        toolbar.setContentsMargins(12, 6, 12, 6)
        toolbar.setSpacing(10)

        self.term_icon_lbl = QLabel()
        self.term_icon_lbl.setPixmap(get_icon("terminal").pixmap(QSize(15, 15)))
        toolbar.addWidget(self.term_icon_lbl)

        self.title_label = QLabel("Consola de Comandos")
        self.title_label.setStyleSheet("background: transparent; font-weight: 700;")
        toolbar.addWidget(self.title_label)

        self.status_label = QLabel("Listo")
        self.status_label.setObjectName("TerminalStatus")
        self.status_label.setProperty("state", "idle")
        toolbar.addWidget(self.status_label)

        toolbar.addStretch()

        self.auto_scroll_cb = AppCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.toggled.connect(self._toggle_auto_scroll)
        toolbar.addWidget(self.auto_scroll_cb)

        self.btn_copy = AppButton("Copiar")
        self.btn_copy.set_icon("copy")
        self.btn_copy.clicked.connect(self.copy_output)
        toolbar.addWidget(self.btn_copy)

        self.btn_clear = AppButton("Limpiar")
        self.btn_clear.set_icon("clean")
        self.btn_clear.clicked.connect(self.clear_output)
        toolbar.addWidget(self.btn_clear)

        self.btn_cancel = AppButton("Cancelar")
        self.btn_cancel.set_icon("cancel")
        self.btn_cancel.setProperty("class", "btn-danger")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_current)
        toolbar.addWidget(self.btn_cancel)

        # Botón para colapsar / expandir la consola
        self.btn_toggle_collapse = AppButton()
        self.btn_toggle_collapse.set_icon("chevron-down")
        self.btn_toggle_collapse.setToolTip("Minimizar / Restaurar consola")
        self.btn_toggle_collapse.setFixedSize(28, 28)
        self.btn_toggle_collapse.clicked.connect(self.toggle_collapse)
        toolbar.addWidget(self.btn_toggle_collapse)

        layout.addWidget(self.header_frame)

        # Área de texto tipo consola
        self.console = QPlainTextEdit()
        self.console.setObjectName("TerminalOutput")
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(5000)
        self.console.setPlaceholderText("La salida de los comandos de Tailscale aparecerá aquí...")
        self.console.setMinimumHeight(110)
        layout.addWidget(self.console)

    def setup_connections(self):
        global_runner.started.connect(self.on_command_started)
        global_runner.output_line.connect(self.on_output_line)
        global_runner.finished.connect(self.on_command_finished)

    def _toggle_auto_scroll(self, checked: bool):
        self.auto_scroll = checked

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.console.hide()
            self.btn_toggle_collapse.set_icon("chevron-down")
        else:
            self.console.show()
            self.btn_toggle_collapse.set_icon("chevron-up")

    def on_command_started(self, cmd_str: str):
        if self.is_collapsed:
            self.toggle_collapse()
        self.btn_cancel.setEnabled(True)
        self._set_status("Ejecutando...", "running")

        self._append_entry("command", cmd_str)
        self._scroll_to_bottom()

    def on_output_line(self, line: str, is_error: bool):
        self._append_entry("error" if is_error else "output", line)

        if self.auto_scroll:
            self._scroll_to_bottom()

    def on_command_finished(self, result: CommandResult):
        self.btn_cancel.setEnabled(False)
        if result.success:
            status_text = f"Finalizado con éxito (Código: 0) en {result.duration_ms}ms"
            self._set_status(status_text, "success")
            self._append_entry("success", f"[OK] {status_text}")
        else:
            status_text = f"Finalizado con error (Código: {result.exit_code}) en {result.duration_ms}ms"
            self._set_status(status_text, "error")
            self._append_entry("error", f"[ERROR] {status_text}")
        self._scroll_to_bottom()

    def _append_entry(self, kind: str, value: str):
        self._entries.append((kind, value))
        self._entries = self._entries[-1000:]
        self._render_entry(kind, value)

    def _render_entry(self, kind: str, value: str):
        colors = get_theme_colors(config.theme)
        safe = escape(value)
        if kind == "command":
            self.console.appendHtml(
                f"<br><span style='color: {colors['accent']}; font-weight: bold;'>$</span> "
                f"<span style='color: {colors['text']}; font-weight: bold;'>{safe}</span>"
            )
        elif kind == "error":
            self.console.appendHtml(f"<span style='color: {colors['danger']};'>{safe}</span>")
        elif kind == "success":
            self.console.appendHtml(f"<span style='color: {colors['success']};'>{safe}</span>")
        else:
            self.console.appendHtml(f"<span style='color: {colors['text']};'>{safe}</span>")

    def refresh_theme(self):
        self.term_icon_lbl.setPixmap(get_icon("terminal").pixmap(QSize(15, 15)))
        self.console.clear()
        for kind, value in self._entries:
            self._render_entry(kind, value)
        if self.auto_scroll:
            self._scroll_to_bottom()

    def _set_status(self, text: str, state: str):
        self.status_label.setText(text)
        self.status_label.setProperty("state", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _scroll_to_bottom(self):
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console.setTextCursor(cursor)

    def cancel_current(self):
        global_runner.cancel()
        self._set_status("Cancelado por el usuario", "error")

    def clear_output(self):
        self._entries.clear()
        self.console.clear()
        self._set_status("Listo", "idle")

    def copy_output(self):
        text = self.console.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            orig = self.btn_copy.text()
            self.btn_copy.setText("¡Copiado!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1200, lambda: self.btn_copy.setText(orig))
