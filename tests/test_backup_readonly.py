"""Unit tests for the read-only firmware-backup command planner.

Run: python3 -m unittest discover -s tests -p test_backup_readonly.py -v
No hardware or external Python packages required.
"""
import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "backup" / "backup_readonly.py"
spec = importlib.util.spec_from_file_location("backup_readonly", SCRIPT)
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupSafetyTests(unittest.TestCase):
    def test_stm32_commands_are_reads_only(self):
        args = argparse.Namespace(tool=None, port=None, baud=None)
        cmd = backup.commands(args, backup.BOARDS["robin-e3-v1.1"], Path("/tmp/output"))
        self.assertEqual(len(cmd), 2)
        for item in cmd:
            self.assertEqual(item[1:4], ["-c", "port=SWD", "--upload"])
            self.assertNotIn("--download", item)
            self.assertNotIn("--erase", item)
            self.assertEqual(item[5], "0x40000")

    def test_original_lk4_requires_larger_read(self):
        args = argparse.Namespace(tool=None, port=None, baud=None)
        cmd = backup.commands(args, backup.BOARDS["original-lk4-f103ve"], Path("/tmp/out"))
        self.assertEqual(cmd[0][5], "0x80000")

    def test_arduinoisp_is_read_only_and_targets_mega(self):
        args = argparse.Namespace(tool=None, port="/dev/ttyUSB0", baud=None)
        cmd = backup.commands(args, backup.BOARDS["lgt-kit-v1.0-arduinoisp"], Path("/tmp/out"))
        self.assertEqual(cmd[0][cmd[0].index("-c") + 1], "stk500v1")
        self.assertEqual(cmd[0][cmd[0].index("-b") + 1], "19200")
        self.assertIn("-n", cmd[0])
        self.assertTrue(any(x.startswith("flash:r:") for x in cmd[0]))
        self.assertTrue(any(x.startswith("eeprom:r:") for x in cmd[0]))
        self.assertFalse(any(":w:" in x for x in cmd[0]))

    def test_default_is_dry_run_without_creating_files(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "new"
            rc = backup.main(["--board", "robin-e3-v1.1", "--output", str(output)])
            self.assertEqual(rc, 0)
            self.assertFalse(output.exists())

    def test_wrong_mcu_blocks_execution(self):
        with self.assertRaises(SystemExit) as caught:
            backup.parse_args([
                "--board", "robin-e3-v1.1",
                "--output", "/tmp/whatever",
                "--execute", "--confirm-mcu", "STM32F103VET6",
            ])
        self.assertEqual(caught.exception.code, 2)

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "existing"
            output.mkdir()
            with patch.object(backup.shutil, "which", return_value="/bin/true"):
                rc = backup.main([
                    "--board", "robin-e3-v1.1",
                    "--output", str(output),
                    "--execute", "--confirm-mcu", "STM32F103RCT6",
                ])
            self.assertEqual(rc, 2)

    def test_mocked_two_read_verification_creates_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "reads"

            def read_to_file(command, check):
                self.assertTrue(check)
                self.assertEqual(command[3], "--upload")
                Path(command[6]).write_bytes(b"\xA5" * 0x40000)

            with patch.object(backup.shutil, "which", return_value="/usr/bin/fake"), \
                 patch.object(backup.subprocess, "run", side_effect=read_to_file):
                rc = backup.main([
                    "--board", "robin-e3-v1.1",
                    "--output", str(output),
                    "--execute", "--confirm-mcu", "STM32F103RCT6",
                ])
            self.assertEqual(rc, 0)
            self.assertTrue((output / "manifest.json").is_file())

    def test_mismatched_mock_read_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "reads"

            def different_read(command, check):
                Path(command[6]).write_bytes(
                    (b"\x00" if command[6].endswith("1.bin") else b"\x01") * 0x40000
                )

            with patch.object(backup.shutil, "which", return_value="/usr/bin/fake"), \
                 patch.object(backup.subprocess, "run", side_effect=different_read):
                rc = backup.main([
                    "--board", "robin-e3-v1.1",
                    "--output", str(output),
                    "--execute", "--confirm-mcu", "STM32F103RCT6",
                ])
            self.assertEqual(rc, 1)
            self.assertFalse((output / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
