"""Consultas de solo lectura a Tailscale sin bloquear el hilo de Qt."""
import shutil

from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal

from app.config import config, IS_LINUX


class AsyncTailscaleQuery(QObject):
    completed = pyqtSignal(object)  # stdout si terminó bien; None si falló

    def __init__(self, parent=None, timeout_ms=5000):
        super().__init__(parent)
        self.process = None
        self.last_error = ""
        self._full_args = []
        self._allow_passwordless_sudo = False
        self._tried_sudo = False
        self._first_error = ""
        self.timeout = QTimer(self)
        self.timeout.setSingleShot(True)
        self.timeout.setInterval(timeout_ms)
        self.timeout.timeout.connect(self._on_timeout)

    def run(self, args, allow_passwordless_sudo=False):
        """Inicia una consulta. Omite otra solicitud si la anterior sigue activa."""
        if self.process is not None:
            return False
        self.last_error = ""
        self._first_error = ""
        self._tried_sudo = False
        self._allow_passwordless_sudo = allow_passwordless_sudo
        self._full_args = ([f"--socket={config.custom_socket}"] if config.custom_socket else []) + list(args)
        self._start(config.tailscale_path, self._full_args)
        return True

    def _start(self, program, args):
        process = QProcess(self)
        self.process = process
        process.finished.connect(self._on_finished)
        process.errorOccurred.connect(self._on_error)
        self.timeout.start()
        process.start(program, args)

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
        error = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        good = exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0
        if (
            not good and self._allow_passwordless_sudo and not self._tried_sudo
            and IS_LINUX and shutil.which("sudo")
            and "profiles access denied" in error.lower()
        ):
            self._first_error = error
            self._tried_sudo = True
            process = self.process
            self.process = None
            self.timeout.stop()
            process.finished.disconnect(self._on_finished)
            process.errorOccurred.disconnect(self._on_error)
            process.deleteLater()
            self._start("sudo", ["-n", config.tailscale_path, *self._full_args])
            return
        if not good:
            self.last_error = (self._first_error + "\n" + error).strip()
        self._complete(output if good else None)

    def _on_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.last_error = self.process.errorString() if self.process else "No se pudo iniciar la consulta"
            self._complete(None)

    def _on_timeout(self):
        self.last_error = "La consulta agotó el tiempo de espera"
        self._complete(None)
