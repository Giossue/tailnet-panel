"""Regresiones de los hallazgos de seguridad y fluidez del panel."""
import base64
import getpass
import json
import os
import shlex
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox

from app.config import config, is_current_user_operator, set_current_user_operator
from app.core.async_query import AsyncTailscaleQuery
from app.core.command_registry import COMMANDS_BY_ID
from app.core.runner import CommandRunner, build_macos_terminal_script
from app.ui.components.command_dialog import CommandDialog


class FindingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])

    def setUp(self):
        self.old_path = config.tailscale_path
        self.old_socket = config.custom_socket
        self.old_no_sudo = config.force_no_sudo

    def tearDown(self):
        config.tailscale_path = self.old_path
        config.custom_socket = self.old_socket
        config.force_no_sudo = self.old_no_sudo

    def _fake_binary(self, folder, body):
        path = Path(folder) / "fake tailscale"
        path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
        path.chmod(0o700)
        return str(path)

    def _wait(self, signal, timeout_ms=3000):
        loop = QEventLoop()
        timed_out = []
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: (timed_out.append(True), loop.quit()))
        signal.connect(loop.quit)
        timer.start(timeout_ms)
        loop.exec()
        timer.stop()
        self.assertFalse(timed_out, "La operación asíncrona no terminó a tiempo")

    def test_credentials_never_reach_console_or_history(self):
        secret = "TEST_ONLY_AUTH_KEY_123456789"
        with tempfile.TemporaryDirectory() as folder:
            config.tailscale_path = self._fake_binary(folder, """
import os, sys, time
key_path = sys.argv[-1].split('=file:', 1)[1]
with open(os.path.join(os.path.dirname(__file__), 'argv-audit'), 'w') as audit:
    audit.write(' '.join(sys.argv))
with open(os.path.join(os.path.dirname(__file__), 'key-path'), 'w') as audit:
    audit.write(key_path)
with open(key_path) as key_file:
    value = key_file.read()
sys.stdout.write(value[:8]); sys.stdout.flush()
time.sleep(0.05)
sys.stdout.write(value[8:] + '\\n'); sys.stdout.flush()
sys.stderr.write('error: ' + value + '\\n'); sys.stderr.flush()
""")
            config.custom_socket = ""
            runner = CommandRunner()
            visible = []
            results = []
            runner.started.connect(visible.append)
            runner.output_line.connect(lambda line, _: visible.append(line))
            runner.finished.connect(results.append)
            runner.run(["login", f"--auth-key={secret}"])
            key_path = runner._secret_file
            self.assertIsNotNone(key_path)
            self.assertEqual(stat.S_IMODE(os.stat(key_path).st_mode), 0o600)
            self._wait(runner.finished)
            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertTrue(result.success)
            self.assertIn("[oculto]", result.output)
            self.assertIn("[oculto]", result.error_output)
            self.assertNotIn(secret, "\n".join(visible))
            self.assertNotIn(secret, repr(vars(result)))
            self.assertNotIn(secret, repr([vars(item) for item in runner.history]))
            self.assertNotIn(secret, (Path(folder) / "argv-audit").read_text())
            self.assertEqual((Path(folder) / "key-path").read_text(), key_path)
            self.assertFalse(os.path.exists(key_path))

    def test_failed_start_emits_finish_and_releases_runner(self):
        config.tailscale_path = "/definitely/missing/tailscale-test"
        config.custom_socket = ""
        runner = CommandRunner()
        results = []
        runner.finished.connect(results.append)
        runner.run(["version"])
        self._wait(runner.finished)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].exit_code, -1)
        self.assertFalse(runner.is_running())
        runner.run(["login", "--auth-key=TEST_ONLY_FAILED_START_KEY"])
        key_path = runner._secret_file
        self.assertIsNotNone(key_path)
        self._wait(runner.finished)
        self.assertEqual(len(results), 2)
        self.assertFalse(os.path.exists(key_path))

    def test_query_keeps_qt_event_loop_responsive(self):
        with tempfile.TemporaryDirectory() as folder:
            config.tailscale_path = self._fake_binary(folder, """
import time
time.sleep(0.25)
print('{"BackendState":"Stopped","Peer":{}}')
""")
            config.custom_socket = ""
            query = AsyncTailscaleQuery(timeout_ms=2000)
            events = []
            query.completed.connect(lambda output: events.append(("done", output)))
            query.run(["status", "--json"])
            QTimer.singleShot(20, lambda: events.append(("timer", None)))
            self._wait(query.completed)
            self.assertEqual(events[0][0], "timer")
            self.assertIn("BackendState", events[-1][1])

    def test_operator_runs_daemon_commands_without_pkexec(self):
        with tempfile.TemporaryDirectory() as folder:
            config.tailscale_path = self._fake_binary(folder, "print('ok')\n")
            config.custom_socket = ""
            config.force_no_sudo = False
            set_current_user_operator(getpass.getuser())
            runner = CommandRunner()
            commands = []
            runner.started.connect(commands.append)
            runner.run(["version"], needs_sudo=True)
            self._wait(runner.finished)
            self.assertTrue(commands)
            self.assertFalse(commands[0].startswith(("pkexec ", "sudo ")))
            self.assertTrue(COMMANDS_BY_ID[90].needs_sudo)
            self.assertTrue(COMMANDS_BY_ID[91].needs_sudo)
            self.assertTrue(COMMANDS_BY_ID[92].needs_sudo)

    def test_switch_invalidates_the_previous_profiles_operator(self):
        with tempfile.TemporaryDirectory() as folder:
            config.tailscale_path = self._fake_binary(folder, "print('ok')\n")
            config.custom_socket = ""
            config.force_no_sudo = False
            set_current_user_operator(getpass.getuser())
            runner = CommandRunner()
            changes = []
            runner.profile_changed.connect(lambda: changes.append(True))
            runner.run(["switch", "work"], needs_sudo=True)
            self._wait(runner.finished)
            self.assertEqual(changes, [True])
            self.assertFalse(is_current_user_operator())

    def test_profile_list_retries_with_passwordless_sudo_without_prompt(self):
        with tempfile.TemporaryDirectory() as folder:
            config.tailscale_path = self._fake_binary(folder, """
import json, os, sys
if not os.environ.get('TEST_SUDO_MODE'):
    print('Access denied: profiles access denied', file=sys.stderr)
    sys.exit(1)
print(json.dumps([{'id': 'profile-1', 'selected': True}]))
""")
            config.custom_socket = ""
            sudo = Path(folder) / "sudo"
            sudo.write_text("""#!/usr/bin/env python3
import os, sys
assert sys.argv[1] == '-n'
os.environ['TEST_SUDO_MODE'] = '1'
os.execv(sys.argv[2], sys.argv[2:])
""", encoding="utf-8")
            sudo.chmod(0o700)
            query = AsyncTailscaleQuery()
            results = []
            query.completed.connect(results.append)
            with patch.dict(os.environ, {"PATH": f"{folder}:{os.environ.get('PATH', '')}"}):
                query.run(["switch", "--list", "--json"], allow_passwordless_sudo=True)
                self._wait(query.completed)
            self.assertEqual(len(results), 1)
            self.assertEqual(json.loads(results[0])[0]["id"], "profile-1")
            self.assertEqual(query.last_error, "")

    def test_runner_uses_passwordless_sudo_for_a_profile_without_operator(self):
        with tempfile.TemporaryDirectory() as folder:
            config.tailscale_path = self._fake_binary(folder, "print('ok')\n")
            config.custom_socket = ""
            config.force_no_sudo = False
            set_current_user_operator("")
            sudo = Path(folder) / "sudo"
            sudo.write_text("""#!/usr/bin/env python3
import os, sys
assert sys.argv[1] == '-n'
os.execv(sys.argv[2], sys.argv[2:])
""", encoding="utf-8")
            sudo.chmod(0o700)
            runner = CommandRunner()
            commands = []
            results = []
            runner.started.connect(commands.append)
            runner.finished.connect(results.append)
            with patch.dict(os.environ, {"PATH": f"{folder}:{os.environ.get('PATH', '')}"}):
                runner.run(["switch", "work"], needs_sudo=True)
                self._wait(runner.finished)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].success)
            self.assertTrue(commands[0].startswith("sudo -n "))

    def test_terminal_arguments_are_quoted_without_shell_interpolation(self):
        dangerous = 'host"; touch /tmp/should-never-exist; $(id)'
        script = build_macos_terminal_script(["/path with spaces/tailscale", "ssh", dangerous])
        self.assertNotIn(dangerous, script)
        encoded = script.split("printf %s ", 1)[1].split(" |", 1)[0]
        decoded = base64.b64decode(encoded).decode("utf-8")
        self.assertEqual(shlex.split(decoded), ["/path with spaces/tailscale", "ssh", dangerous])

        import app.core.runner as runner_module
        with patch.object(runner_module, "IS_LINUX", False), \
             patch.object(runner_module, "IS_MACOS", False), \
             patch.object(runner_module, "IS_WINDOWS", True), \
             patch.object(runner_module.subprocess, "CREATE_NEW_CONSOLE", 16, create=True), \
             patch.object(runner_module.subprocess, "Popen") as popen:
            self.assertTrue(CommandRunner.launch_in_external_terminal(["ssh", dangerous]))
            args = popen.call_args.args[0]
            self.assertEqual(args[-2:], ["ssh", dangerous])
            self.assertNotIn("cmd.exe", args)

    def test_required_choice_runs(self):
        dialog = CommandDialog(COMMANDS_BY_ID[34])
        with patch("app.ui.components.command_dialog.global_runner.run") as run, \
             patch.object(QMessageBox, "warning") as warning:
            dialog.run_command()
            run.assert_called_once_with(["get", "accept-routes"], needs_sudo=False)
            warning.assert_not_called()

    def test_secret_preview_and_input_are_cleared(self):
        secret = "TEST_ONLY_SECRET_987654321"
        for command_id, field in ((51, "auth_key"), (46, "secret")):
            dialog = CommandDialog(COMMANDS_BY_ID[command_id])
            widget = dialog.param_widgets[field][1]
            widget.setText(secret)
            self.assertNotIn(secret, dialog.preview_lbl.text())
            self.assertFalse(dialog.btn_copy.isEnabled())
            with patch("app.ui.components.command_dialog.global_runner.run") as run:
                dialog.run_command()
                self.assertTrue(run.called)
            self.assertEqual(widget.text(), "")


if __name__ == "__main__":
    unittest.main()
