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
            "nand-ab-ce-carrier/u-boot-ce.b000ff",
            "openh432-nand-b.img",
            "openh432-systembase-b-h432b.rootfs.squashfs-xz",
        ))
        with self.assertRaises(ValueError):
            artifacts.differences({"schema": 2, "artifacts": {
                name: {} for name in artifacts.ARTIFACTS}}, {})

    def test_compare_and_changed_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in artifacts.ARTIFACTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"test payload")
            reference = artifacts.manifest(root)
            self.assertEqual(reference["schema"], 3)
            self.assertEqual([], artifacts.differences(reference, artifacts.manifest(root)))
            (root / artifacts.ARTIFACTS[0]).write_bytes(b"new payload")
            self.assertEqual([artifacts.ARTIFACTS[0]], artifacts.differences(reference, artifacts.manifest(root)))
            with self.assertRaises(ValueError):
                artifacts.differences({"schema": 1, "artifacts": {}}, reference)

    def test_missing_artifact_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                artifacts.manifest(Path(folder))
