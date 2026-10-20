# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("artifacts", ROOT / "scripts/artifact-manifest.py")
artifacts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifacts)

class Manifest(unittest.TestCase):
    def test_current_ab_deployment_set(self):
        self.assertEqual(artifacts.ARTIFACTS, (
            "modern-nand-ce-carrier/u-boot-ce.b000ff",
            "openh432-nand-b.img",
            "openh432-recovery.img",
            "openh432-systembase-b-h432b.rootfs.squashfs.verity",
            "openh432-systembase-b-h432b.rootfs.verity",
            "openh432-systemext-h432b.rootfs.erofs.verity",
            "openh432-systemext-h432b.rootfs.verity",
        ))
        with self.assertRaises(ValueError):
            artifacts.differences({"schema": 3, "artifacts": {
                name: {} for name in artifacts.ARTIFACTS}}, {})

    def test_compare_and_changed_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in artifacts.ARTIFACTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"test payload")
            reference = artifacts.manifest(root)
            self.assertEqual(reference["schema"], 8)
            self.assertEqual([], artifacts.differences(reference, artifacts.manifest(root)))
            (root / artifacts.ARTIFACTS[0]).write_bytes(b"new payload")
            self.assertEqual([artifacts.ARTIFACTS[0]], artifacts.differences(reference, artifacts.manifest(root)))
            with self.assertRaises(ValueError):
                artifacts.differences({"schema": 1, "artifacts": {}}, reference)

    def test_recovery_is_required_and_compared(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in artifacts.ARTIFACTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"test payload")
            reference = artifacts.manifest(root)
            recovery = root / "openh432-recovery.img"
            recovery.write_bytes(b"changed recovery")
            self.assertEqual(["openh432-recovery.img"],
                             artifacts.differences(reference, artifacts.manifest(root)))
            recovery.unlink()
            with self.assertRaises(FileNotFoundError):
                artifacts.manifest(root)
            with self.assertRaises(ValueError):
                artifacts.differences(dict(reference, schema=7), reference)

    def test_missing_artifact_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                artifacts.manifest(Path(folder))
