"""
Vista de Archivos y Almacenamiento: Taildrop y Taildrive (Comandos: file, drive).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTabWidget, QGroupBox, QFormLayout, QFileDialog,
    QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from app.ui.icons import get_icon
from app.ui.components.controls import AppButton, set_tab_icon
from app.core.runner import global_runner
from app.core.async_query import AsyncTailscaleQuery

class FilesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.drive_query = AsyncTailscaleQuery(self)
        self.drive_query.completed.connect(self._on_drive_response)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # ----------------- Subtab 1: Taildrop -----------------
        tab_taildrop = QWidget()
        td_layout = QVBoxLayout(tab_taildrop)
        td_layout.setSpacing(12)

        # Enviar archivo
        send_box = QGroupBox("Enviar Archivo a otro Dispositivo (tailscale file cp)")
        send_form = QFormLayout(send_box)
        send_form.setSpacing(10)

        file_row = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Selecciona el archivo local a enviar...")
        btn_browse_file = AppButton("Examinar...")
        btn_browse_file.set_icon("folder")
        btn_browse_file.clicked.connect(self.browse_send_file)
        file_row.addWidget(self.file_path_input)
        file_row.addWidget(btn_browse_file)
        send_form.addRow("Archivo:", file_row)

        target_row = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Nombre del dispositivo destino (ej: laptop: o telefono:)")
        btn_list_targets = AppButton("Listar Destinos")
        btn_list_targets.set_icon("devices")
        btn_list_targets.clicked.connect(lambda: global_runner.run(["file", "cp", "--targets"]))
        target_row.addWidget(self.target_input)
        target_row.addWidget(btn_list_targets)
        send_form.addRow("Dispositivo Destino:", target_row)

        btn_send = AppButton("Enviar Archivo mediante Taildrop")
        btn_send.set_icon("upload")
        btn_send.setProperty("class", "btn-primary")
        btn_send.clicked.connect(self.action_send_file)
        send_form.addRow("", btn_send)

        td_layout.addWidget(send_box)

        # Recibir archivos
        recv_box = QGroupBox("Bandeja de Entrada / Descargar Archivos (tailscale file get)")
        recv_form = QFormLayout(recv_box)
        recv_form.setSpacing(10)

        dest_row = QHBoxLayout()
        self.dest_dir_input = QLineEdit()
        self.dest_dir_input.setPlaceholderText("Directorio donde guardar los archivos recibidos...")
        btn_browse_dest = AppButton("Examinar...")
        btn_browse_dest.set_icon("folder")
        btn_browse_dest.clicked.connect(self.browse_dest_dir)
        dest_row.addWidget(self.dest_dir_input)
        dest_row.addWidget(btn_browse_dest)
        recv_form.addRow("Guardar en:", dest_row)

        btn_get_files = AppButton("Descargar Archivos Recibidos")
        btn_get_files.set_icon("download")
        btn_get_files.setProperty("class", "btn-primary")
        btn_get_files.clicked.connect(self.action_get_files)
        recv_form.addRow("", btn_get_files)

        td_layout.addWidget(recv_box)
        td_layout.addStretch()

        tabs.addTab(tab_taildrop, "Taildrop (Transferencia P2P)")
        set_tab_icon(tabs, 0, "upload")

        # ----------------- Subtab 2: Taildrive -----------------
        tab_taildrive = QWidget()
        drive_layout = QVBoxLayout(tab_taildrive)
        drive_layout.setSpacing(12)

        # Compartir nueva carpeta
        share_box = QGroupBox("Compartir Nueva Carpeta (tailscale drive share)")
        share_form = QFormLayout(share_box)
        share_form.setSpacing(10)

        self.share_name_input = QLineEdit()
        self.share_name_input.setPlaceholderText("Nombre del recurso compartido (ej: documentos)")
        share_form.addRow("Nombre del recurso:", self.share_name_input)

        share_path_row = QHBoxLayout()
        self.share_path_input = QLineEdit()
        self.share_path_input.setPlaceholderText("Ruta del directorio local...")
        btn_browse_share = AppButton("Examinar...")
        btn_browse_share.set_icon("folder")
        btn_browse_share.clicked.connect(self.browse_share_dir)
        share_path_row.addWidget(self.share_path_input)
        share_path_row.addWidget(btn_browse_share)
        share_form.addRow("Ruta local:", share_path_row)

        btn_do_share = AppButton("Compartir con Taildrive")
        btn_do_share.set_icon("folder-open")
        btn_do_share.setProperty("class", "btn-primary")
        btn_do_share.clicked.connect(self.action_share_drive)
        share_form.addRow("", btn_do_share)

        drive_layout.addWidget(share_box)

        # Recursos compartidos y gestión
        list_box = QGroupBox("Recursos Compartidos Actuales (tailscale drive list)")
        list_layout = QVBoxLayout(list_box)

        btn_list_drive = AppButton("Actualizar Lista")
        btn_list_drive.set_icon("refresh")
        btn_list_drive.clicked.connect(self.refresh_drive_list)
        list_layout.addWidget(btn_list_drive)

        self.drive_list_widget = QListWidget()
        list_layout.addWidget(self.drive_list_widget)

        manage_row = QHBoxLayout()
        self.rename_new_input = QLineEdit()
        self.rename_new_input.setPlaceholderText("Nuevo nombre para renombrar...")
        btn_rename_drive = AppButton("Renombrar")
        btn_rename_drive.set_icon("edit")
        btn_rename_drive.clicked.connect(self.action_rename_drive)

        btn_unshare_drive = AppButton("Dejar de Compartir")
        btn_unshare_drive.set_icon("trash")
        btn_unshare_drive.setProperty("class", "btn-danger")
        btn_unshare_drive.clicked.connect(self.action_unshare_drive)

        manage_row.addWidget(self.rename_new_input)
        manage_row.addWidget(btn_rename_drive)
        manage_row.addWidget(btn_unshare_drive)
        list_layout.addLayout(manage_row)

        drive_layout.addWidget(list_box)
        drive_layout.addStretch()

        tabs.addTab(tab_taildrive, "Taildrive (Carpetas Compartidas)")
        set_tab_icon(tabs, 1, "files")

        layout.addWidget(tabs)

    def browse_send_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo para enviar")
        if path:
            self.file_path_input.setText(path)

    def browse_dest_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar directorio destino")
        if path:
            self.dest_dir_input.setText(path)

    def browse_share_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta a compartir")
        if path:
            self.share_path_input.setText(path)

    def action_send_file(self):
        f = self.file_path_input.text().strip()
        t = self.target_input.text().strip()
        if not f or not t:
            QMessageBox.warning(self, "Atención", "Por favor especifica tanto el archivo como el equipo destino.")
            return
        if not t.endswith(":"):
            t += ":"
        global_runner.run(["file", "cp", f, t])

    def action_get_files(self):
        d = self.dest_dir_input.text().strip()
        args = ["file", "get"]
        if d:
            args.append(d)
        global_runner.run(args)

    def action_share_drive(self):
        name = self.share_name_input.text().strip()
        path = self.share_path_input.text().strip()
        if not name or not path:
            QMessageBox.warning(self, "Atención", "Especifica nombre y ruta del recurso.")
            return
        global_runner.run(["drive", "share", name, path])

    def refresh_drive_list(self):
        self.drive_query.run(["drive", "list"])

    def _on_drive_response(self, output):
        self.drive_list_widget.clear()
        if output:
            for share in output.strip().splitlines():
                if share.strip():
                    self.drive_list_widget.addItem(share.strip())

    def action_rename_drive(self):
        cur = self.drive_list_widget.currentItem()
        if not cur:
            QMessageBox.warning(self, "Atención", "Selecciona un recurso de la lista para renombrar.")
            return
        old_name = cur.text().split()[0]
        new_name = self.rename_new_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Atención", "Ingresa el nuevo nombre.")
            return
        global_runner.run(["drive", "rename", old_name, new_name])

    def action_unshare_drive(self):
        cur = self.drive_list_widget.currentItem()
        if not cur:
            QMessageBox.warning(self, "Atención", "Selecciona un recurso de la lista para dejar de compartir.")
            return
        name = cur.text().split()[0]
        global_runner.run(["drive", "unshare", name])
