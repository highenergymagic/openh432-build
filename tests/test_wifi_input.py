# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bsp_wifi", ROOT / "scripts/bsp.py")
bsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bsp)


class WifiInput(unittest.TestCase):
    def test_default_does_not_add_firmware(self):
        cfg = {"local_conf_header": {}}
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(bsp.configure_wifi(cfg, Path(folder)))
            self.assertEqual(list(Path(folder).iterdir()), [])
        self.assertNotIn("private-wifi-firmware", cfg["local_conf_header"])

    def test_rejects_injected_country(self):
        for country in ('NZ"\nOTHER=1', "nz", "NZ;id", "ABC"):
            with self.assertRaises(ValueError):
                bsp.configure_wifi({"local_conf_header": {}}, Path("."), country=country)

    def test_rejects_unqualified_blob(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input"
            source.write_bytes(b"not firmware")
            with self.assertRaises(ValueError):
                bsp.configure_wifi({"local_conf_header": {}}, Path(folder), source)

    def test_private_copy_and_explicit_package(self):
        digest = "a586c6d2253d2890f8a853c3d98dfc0f880be1b0c9a420057a2436fc6523a4d7"
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input"
            source.write_bytes(b"fixture")
            cfg = {"local_conf_header": {}}
            with patch.object(bsp.hashlib, "sha256", return_value=Mock(hexdigest=lambda: digest)):
                self.assertEqual(bsp.configure_wifi(cfg, Path(folder), source, "NZ"), digest)
            copied = Path(folder) / "private-wifi-firmware/rtl8712s.bin"
            self.assertEqual(copied.read_bytes(), b"fixture")
            self.assertEqual(copied.stat().st_mode & 0o777, 0o600)
            self.assertIn("h432b-wifi-firmware", cfg["local_conf_header"]["private-wifi-firmware"])


if __name__ == "__main__":
    unittest.main()
