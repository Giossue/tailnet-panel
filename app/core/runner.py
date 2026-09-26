"""
Ejecutor asíncrono de comandos de Tailscale multiplataforma con soporte para streaming y elevación de privilegios.
"""
import sys
import os
import time
import shutil
import base64
import shlex
import subprocess
import tempfile
from typing import List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QProcess, QDateTime
from app.config import config, IS_LINUX, IS_WINDOWS, IS_MACOS


def redact_arguments(args: List[str]) -> List[str]:
    """Oculta secretos de la vista previa, la consola y el historial."""
    redacted = list(args)
    for index, arg in enumerate(redacted):
        for flag in ("--auth-key=", "--authkey="):
            if arg.startswith(flag):
                redacted[index] = flag + "[oculto]"
        if arg in ("--auth-key", "--authkey") and index + 1 < len(redacted):
            redacted[index + 1] = "[oculto]"
        if index >= 2 and redacted[index - 2:index] == ["lock", "disable"]:
            redacted[index] = "[oculto]"
    return redacted


def sensitive_values(args: List[str]) -> List[str]:
    """Devuelve las credenciales recibidas para borrarlas de cualquier salida."""
    values = []
    for index, arg in enumerate(args):
        for flag in ("--auth-key=", "--authkey="):
            if arg.startswith(flag):
                values.append(arg[len(flag):])
        if arg in ("--auth-key", "--authkey") and index + 1 < len(args):
            values.append(args[index + 1])
        if index >= 2 and args[index - 2:index] == ["lock", "disable"]:
            values.append(arg)
    return sorted({value for value in values if value}, key=len, reverse=True)


def auth_key_from_args(args: List[str]) -> Optional[str]:
    """Extrae una auth key pasada directamente a login/up, si existe."""
    if not args or args[0] not in ("login", "up"):
        return None
    for index, arg in enumerate(args):
        for flag in ("--auth-key=", "--authkey="):
            if arg.startswith(flag):
                value = arg[len(flag):]
                return value if value and not value.startswith("file:") else None
        if arg in ("--auth-key", "--authkey") and index + 1 < len(args):
            value = args[index + 1]
            return value if value and not value.startswith("file:") else None
    return None


def replace_auth_key_with_file(args: List[str], path: str) -> List[str]:
    """Usa el formato file: del CLI para evitar la clave en argv."""
    replaced = []
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg.startswith(("--auth-key=", "--authkey=")):
            replaced.append(f"--auth-key=file:{path}")
        elif arg in ("--auth-key", "--authkey"):
            replaced.append(f"--auth-key=file:{path}")
            skip_next = True
        else:
            replaced.append(arg)
    return replaced


def requires_system_elevation(args: List[str]) -> bool:
    """Acciones que modifican la instalación o la configuración del sistema."""
    return bool(args) and (
        args[0] == "update" or args[:2] == ["configure", "synology"]
    )

class CommandResult:
    def __init__(self, command: str, exit_code: int, output: str, error_output: str, duration_ms: int):
        self.command = command
        self.exit_code = exit_code
        self.output = output
        self.error_output = error_output
        self.duration_ms = duration_ms
        self.success = (exit_code == 0)
        self.timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

class CommandRunner(QObject):
    """
    Ejecutor de comandos mediante QProcess. Emite señales en tiempo real para no congelar la interfaz gráfica.
    """
    started = pyqtSignal(str)                 # Comando completo ejecutado
    output_line = pyqtSignal(str, bool)       # (línea de texto, es_error)
    finished = pyqtSignal(CommandResult)      # Resultado al terminar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process: Optional[QProcess] = None
        self.current_command_str: str = ""
        self.accumulated_out: List[str] = []
        self.accumulated_err: List[str] = []
        self.start_time: float = 0.0
        self.history: List[CommandResult] = []
        self._sensitive_values: List[str] = []
        self._secret_file: Optional[str] = None

    def _redact_output(self, content: str) -> str:
        for value in self._sensitive_values:
            content = content.replace(value, "[oculto]")
        return content

    def is_running(self) -> bool:
        return self.process is not None and self.process.state() != QProcess.ProcessState.NotRunning

    def cancel(self):
        """Cancela el proceso actual si está en ejecución."""
        if self.process and self.is_running():
            self.process.kill()
            self.process.waitForFinished(300)
            self._cleanup_secret_file()

    def __del__(self):
        if self.process and self.is_running():
            self.process.kill()
            self.process.waitForFinished(300)
        self._cleanup_secret_file()

    def _cleanup_secret_file(self):
        path = self._secret_file
        self._secret_file = None
        if path:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass

    def run(self, args: List[str], needs_sudo: bool = False, custom_socket: Optional[str] = None):
        """
        Ejecuta un comando de Tailscale asíncronamente con los argumentos dados.
        """
        if self.is_running():
            self.output_line.emit("[AVISO] Un comando ya se encuentra en ejecución. Cancélalo primero o espera a que finalice.", True)
            return

        ts_bin = config.tailscale_path
        self._sensitive_values = sensitive_values(args)
        execution_args = list(args)
        auth_key = auth_key_from_args(args)
        if auth_key:
            try:
                runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
                if not runtime_dir or not os.path.isdir(runtime_dir) or not os.access(runtime_dir, os.W_OK):
                    runtime_dir = None
                fd, path = tempfile.mkstemp(prefix="tailnet-panel-key-", dir=runtime_dir)
                self._secret_file = path
                with os.fdopen(fd, "w", encoding="utf-8") as secret_file:
                    secret_file.write(auth_key)
                execution_args = replace_auth_key_with_file(args, path)
            except OSError as error:
                self._cleanup_secret_file()
                self._sensitive_values = []
                result = CommandResult("tailscale [clave oculta]", -1, "", str(error), 0)
                self.output_line.emit(str(error), True)
                self.history.append(result)
                self.finished.emit(result)
                return
        final_args = []

        # Agregar flag de socket global si está configurado
        socket_to_use = custom_socket if custom_socket else config.custom_socket
        if socket_to_use:
            final_args.append(f"--socket={socket_to_use}")

        final_args.extend(execution_args)

        # Determinar elevación de privilegios
        exec_program = ts_bin
        exec_args = final_args
        display_cmd = ""

        # Si el usuario es operador o tiene force_no_sudo, no requerir sudo
        from app.config import is_current_user_operator
        effective_needs_sudo = needs_sudo
        if effective_needs_sudo and (
            config.force_no_sudo
            or (not requires_system_elevation(args) and is_current_user_operator())
        ):
            effective_needs_sudo = False

        if effective_needs_sudo:
            if IS_LINUX:
                if os.geteuid() == 0:
                    exec_program = ts_bin
                    exec_args = final_args
                    display_cmd = f"{ts_bin} {' '.join(final_args)}"
                elif config.use_pkexec and shutil.which("pkexec"):
                    exec_program = "pkexec"
                    exec_args = [ts_bin] + final_args
                    display_cmd = f"pkexec {ts_bin} {' '.join(final_args)}"
                else:
                    exec_program = "sudo"
                    exec_args = [ts_bin] + final_args
                    display_cmd = f"sudo {ts_bin} {' '.join(final_args)}"
            elif IS_MACOS:
                exec_program = "sudo"
                exec_args = [ts_bin] + final_args
                display_cmd = f"sudo {ts_bin} {' '.join(final_args)}"
            elif IS_WINDOWS:
                exec_program = ts_bin
                exec_args = final_args
                display_cmd = f"{ts_bin} {' '.join(final_args)}"
        else:
            display_cmd = f"{ts_bin} {' '.join(final_args)}"

        self.current_command_str = display_cmd.replace(" ".join(final_args), " ".join(redact_arguments(final_args)), 1)
        self.accumulated_out = []
        self.accumulated_err = []
        self.start_time = time.time()

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

        self.started.emit(self.current_command_str)
        self.process.start(exec_program, exec_args)

    def _on_error(self, error):
        if error != QProcess.ProcessError.FailedToStart or not self.process:
            return
        process = self.process
        message = self._redact_output(process.errorString())
        self.output_line.emit(message, True)
        result = CommandResult(
            self.current_command_str, -1, "", message,
            int((time.time() - self.start_time) * 1000),
        )
        self.process = None
        process.finished.disconnect(self._on_finished)
        process.errorOccurred.disconnect(self._on_error)
        process.deleteLater()
        self._cleanup_secret_file()
        self._sensitive_values = []
        self.history.append(result)
        self.finished.emit(result)

    def _on_stdout(self):
        if not self.process:
            return
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.accumulated_out.append(data)
        if not self._sensitive_values:
            for line in data.splitlines():
                self.output_line.emit(line, False)

    def _on_stderr(self):
        if not self.process:
            return
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.accumulated_err.append(data)
        if not self._sensitive_values:
            for line in data.splitlines():
                self.output_line.emit(line, True)

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        if not self.process:
            return
        self._on_stdout()
        self._on_stderr()
        elapsed_ms = int((time.time() - self.start_time) * 1000)
        # Una credencial puede llegar partida en varios fragmentos. Para estos
        # comandos se emite la salida solo después de reunirla y redactarla.
        full_out = self._redact_output("".join(self.accumulated_out))
        full_err = self._redact_output("".join(self.accumulated_err))
        if self._sensitive_values:
            for line in full_out.splitlines():
                self.output_line.emit(line, False)
            for line in full_err.splitlines():
                self.output_line.emit(line, True)
        self.accumulated_out = []
        self.accumulated_err = []
        self._sensitive_values = []

        result = CommandResult(
            command=self.current_command_str,
            exit_code=exit_code if exit_status == QProcess.ExitStatus.NormalExit else -1,
            output=full_out,
            error_output=full_err,
            duration_ms=elapsed_ms
        )
        process = self.process
        self.process = None
        process.finished.disconnect(self._on_finished)
        process.errorOccurred.disconnect(self._on_error)
        process.deleteLater()
        self._cleanup_secret_file()
        self.history.append(result)
        self.finished.emit(result)

    @staticmethod
    def launch_in_external_terminal(cmd_args: List[str], window_title: str = "Tailscale Session"):
        """Lanza un comando interactivo en la terminal predeterminada del sistema."""
        ts_bin = config.tailscale_path
        full_cmd = [ts_bin] + ([f"--socket={config.custom_socket}"] if config.custom_socket else []) + cmd_args

        if IS_LINUX:
            terminals = [
                ["x-terminal-emulator", "-e"],
                ["gnome-terminal", "--"],
                ["konsole", "-e"],
                ["alacritty", "-e"],
                ["kitty"],
                ["xfce4-terminal", "-e"],
                ["xterm", "-e"]
            ]
            for term in terminals:
                if shutil.which(term[0]):
                    started, _ = QProcess.startDetached(term[0], term[1:] + full_cmd)
                    if started:
                        return True
        elif IS_MACOS:
            # AppleScript recibe una cadena fija; los argumentos solo aparecen
            # después de decodificar un comando POSIX citado por shlex.
            script = build_macos_terminal_script(full_cmd)
            started, _ = QProcess.startDetached("osascript", ["-e", script])
            return started
        elif IS_WINDOWS:
            try:
                subprocess.Popen(full_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return True
            except OSError:
                return False

        return False


def build_macos_terminal_script(full_cmd: List[str]) -> str:
    """Construye AppleScript sin insertar argumentos sin escapar."""
    encoded = base64.b64encode(shlex.join(full_cmd).encode("utf-8")).decode("ascii")
    return f'tell application "Terminal" to do script "printf %s {encoded} | /usr/bin/base64 -D | /bin/sh"'

# Runner global para acciones de la aplicación
global_runner = CommandRunner()
