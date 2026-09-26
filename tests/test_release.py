"""Comprobaciones del paquete fuente y sus recursos públicos."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PyQt6.QtSvg import QSvgRenderer

from app.config import ConfigManager
from build_executable import PROJECT_ROOT, build_command
from install_desktop import desktop_entry, desktop_exec_path, remove_legacy_launcher


class ReleaseTests(unittest.TestCase):
    def test_build_includes_the_app_mark_and_icon_fonts(self):
        command = build_command()
        self.assertIn(f"--add-data={PROJECT_ROOT / 'app' / 'assets'}:app/assets", command)
        self.assertIn("--collect-data=qtawesome", command)
        self.assertIn(str(PROJECT_ROOT / "app" / "main.py"), command)
        self.assertNotIn("pip", command)
        self.assertTrue(QSvgRenderer(str(PROJECT_ROOT / "app" / "assets" / "panel-mark.svg")).isValid())

    def test_desktop_launcher_quotes_a_path_with_spaces(self):
        launcher = PROJECT_ROOT / "run.sh"
        self.assertIn(f"Exec={desktop_exec_path(launcher)}", desktop_entry())
        self.assertIn('"/tmp/carpeta con espacios/run.sh"',
                      desktop_exec_path(Path("/tmp/carpeta con espacios/run.sh")))
        self.assertIn("%%", desktop_exec_path(Path("/tmp/porcentaje%/run.sh")))

    def test_old_settings_are_migrated_without_overwriting_new_settings(self):
        backing = {
            ("TailscalePanelOrg", "Tailscale Panel"): {
                "theme": "light", "custom_socket": "/tmp/old.sock", "unexpected": "ignore"
            },
            ("TailnetPanelOrg", "Tailnet Panel"): {"theme": "dark"},
        }

        class MemorySettings:
            def __init__(self, organization, app_name):
                self.data = backing.setdefault((organization, app_name), {})

            def contains(self, key):
                return key in self.data

            def value(self, key):
                return self.data[key]

            def setValue(self, key, value):
                self.data[key] = value

            def sync(self):
                pass

        with patch("app.config.QSettings", MemorySettings):
            ConfigManager()
        new = backing[("TailnetPanelOrg", "Tailnet Panel")]
        self.assertEqual(new["theme"], "dark")
        self.assertEqual(new["custom_socket"], "/tmp/old.sock")
        self.assertNotIn("unexpected", new)

    def test_old_launcher_is_removed_only_if_it_runs_this_project(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "tailnet-panel.desktop"
            old = target.with_name("tailscale-panel.desktop")
            old.write_text("[Desktop Entry]\nName=Tailscale Panel\nExec=/other/run.sh\n")
            remove_legacy_launcher(target)
            self.assertTrue(old.exists())
            old.write_text(
                f"[Desktop Entry]\nName=Tailscale Panel\nExec={desktop_exec_path(PROJECT_ROOT / 'run.sh')}\n"
            )
            remove_legacy_launcher(target)
            self.assertFalse(old.exists())


if __name__ == "__main__":
    unittest.main()
