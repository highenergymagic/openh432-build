# SPDX-License-Identifier: MIT
"""Restricted speech inputs are explicit and fail closed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("bsp", Path(__file__).resolve().parents[1] / "scripts/bsp.py")
bsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bsp)


class OpenEVVInput(unittest.TestCase):
    def test_backend_requires_explicit_input(self):
        cfg = {"local_conf_header": {}}
        with self.assertRaises(ValueError):
            bsp.configure_speech_backend(cfg, "openevv")
        bsp.configure_speech_backend(cfg, "openevv", bsp.OPENEVV_SOURCE_SHA256)
        self.assertEqual(cfg["local_conf_header"]["speech-backend"], 'OPENH432_SPEECH_BACKEND = "openevv"\n')

    def test_absent_does_not_enable_recipe(self):
        cfg = {"local_conf_header": {}}
        with tempfile.TemporaryDirectory() as path:
            self.assertIsNone(bsp.configure_openevv(cfg, Path(path)))
            self.assertEqual(cfg["local_conf_header"], {})
            self.assertFalse((Path(path) / "private-openevv").exists())

    def test_unknown_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            source = Path(path) / "input.tar"
            source.write_bytes(b"unqualified")
            with self.assertRaises(ValueError):
                bsp.configure_openevv({"local_conf_header": {}}, Path(path), source)
            self.assertFalse((Path(path) / "private-openevv").exists())

    def test_accepted_input_is_private_not_image_policy(self):
        import hashlib
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            source = root / "input.tar"
            source.write_bytes(b"test-only")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            cfg = {"local_conf_header": {}}
            with patch.object(bsp, "OPENEVV_SOURCE_SHA256", digest):
                self.assertEqual(bsp.configure_openevv(cfg, root, source), digest)
            dest = root / "private-openevv/openevv.tar"
            self.assertEqual(dest.read_bytes(), source.read_bytes())
            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
            self.assertNotIn("IMAGE_INSTALL", str(cfg))

    def test_copy_replaces_destination_symlink_without_overwriting_target(self):
        import hashlib
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            source = root / "input.tar"
            source.write_bytes(b"test-only")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            folder = root / "private-openevv"
            folder.mkdir()
            unrelated = root / "unrelated"
            unrelated.write_bytes(b"preserve")
            destination = folder / "openevv.tar"
            destination.symlink_to(unrelated)
            with patch.object(bsp, "OPENEVV_SOURCE_SHA256", digest):
                bsp.configure_openevv({"local_conf_header": {}}, root, source)
            self.assertEqual(unrelated.read_bytes(), b"preserve")
            self.assertFalse(destination.is_symlink())
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(folder.glob(".openevv-*")), [])

    def test_failed_replace_preserves_existing_archive(self):
        import hashlib
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            source = root / "input.tar"
            source.write_bytes(b"test-only")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            folder = root / "private-openevv"
            folder.mkdir()
            destination = folder / "openevv.tar"
            destination.write_bytes(b"previous")
            with patch.object(bsp, "OPENEVV_SOURCE_SHA256", digest):
                with patch.object(bsp.os, "replace", side_effect=OSError("test")):
                    with self.assertRaises(OSError):
                        bsp.configure_openevv({"local_conf_header": {}}, root, source)
            self.assertEqual(destination.read_bytes(), b"previous")
            self.assertEqual(list(folder.glob(".openevv-*")), [])
