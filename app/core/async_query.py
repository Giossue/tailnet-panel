"""Consultas de solo lectura a Tailscale sin bloquear el hilo de Qt."""
from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal

from app.config import config


class AsyncTailscaleQuery(QObject):
    completed = pyqtSignal(object)  # stdout si terminó bien; None si falló

    def __init__(self, parent=None, timeout_ms=5000):
        super().__init__(parent)
        self.process = None
        self.timeout = QTimer(self)
        self.timeout.setSingleShot(True)
        self.timeout.setInterval(timeout_ms)
        self.timeout.timeout.connect(self._on_timeout)

    def run(self, args):
        """Inicia una consulta. Omite otra solicitud si la anterior sigue activa."""
        if self.process is not None:
            return False
        process = QProcess(self)
        self.process = process
        process.finished.connect(self._on_finished)
        process.errorOccurred.connect(self._on_error)
        full_args = ([f"--socket={config.custom_socket}"] if config.custom_socket else []) + list(args)
        self.timeout.start()
        process.start(config.tailscale_path, full_args)
        return True

    def cancel(self):
        """Descarta una consulta obsoleta, por ejemplo después de cambiar el socket."""
        process = self.process
        if process is None:
            return
        self.process = None
        self.timeout.stop()
        process.finished.disconnect(self._on_finished)
        process.errorOccurred.disconnect(self._on_error)
        if process.state() != QProcess.ProcessState.NotRunning:
            process.kill()
            process.waitForFinished(300)
        process.deleteLater()

    def _complete(self, output):
        process = self.process
        if process is None:
            return
        self.process = None
        self.timeout.stop()
        process.finished.disconnect(self._on_finished)
        process.errorOccurred.disconnect(self._on_error)
        if process.state() != QProcess.ProcessState.NotRunning:
            process.kill()
            process.waitForFinished(300)
        process.deleteLater()
        self.completed.emit(output)

    def _on_finished(self, exit_code, exit_status):
        if self.process is None:
            return
        output = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        good = exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0
        self._complete(output if good else None)

    def _on_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self._complete(None)

    def _on_timeout(self):
        self._complete(None)
