"""La configuración de sudo se prueba sin tocar /etc."""
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import configure_passwordless_tailscale as setup


class PasswordlessSetupTests(unittest.TestCase):
    def test_installs_validated_user_rule_and_can_remove_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validator = root / "visudo"
            validator.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            validator.chmod(0o700)
            args = ["setup", "--user", "testuser", "--tailscale-path", "/usr/bin/tailscale"]
            with patch.object(setup, "SUDOERS_DIR", root), \
                 patch.object(setup.os, "geteuid", return_value=0), \
                 patch.object(setup, "valid_user", return_value="testuser"), \
                 patch.object(setup, "valid_tailscale_path", return_value="/usr/bin/tailscale"), \
                 patch.object(setup.shutil, "which", return_value=str(validator)), \
                 patch.object(sys, "argv", args):
                self.assertEqual(setup.main(), 0)
                rule = root / "tailnet-panel-testuser"
                self.assertEqual(stat.S_IMODE(rule.stat().st_mode), 0o440)
                self.assertIn("testuser ALL=(root) NOPASSWD: /usr/bin/tailscale", rule.read_text())
                with patch.object(sys, "argv", args + ["--remove"]):
                    self.assertEqual(setup.main(), 0)
                self.assertFalse(rule.exists())

    def test_refuses_to_overwrite_an_unmanaged_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rule = root / "tailnet-panel-testuser"
            rule.write_text("user ALL=(root) /bin/true\n", encoding="utf-8")
            with patch.object(setup, "SUDOERS_DIR", root), \
                 patch.object(setup.os, "geteuid", return_value=0), \
                 patch.object(setup, "valid_user", return_value="testuser"), \
                 patch.object(sys, "argv", ["setup", "--user", "testuser", "--remove"]):
                with self.assertRaises(SystemExit):
                    setup.main()
            self.assertTrue(rule.exists())


if __name__ == "__main__":
    unittest.main()
