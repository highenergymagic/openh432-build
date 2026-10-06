# SPDX-License-Identifier: MIT
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("platform_bsp", ROOT / "scripts/bsp.py")
bsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bsp)

class Platforms(unittest.TestCase):
    def test_native_uses_docker_daemon(self):
        for reported, expected in (("linux/x86_64", "linux/amd64"),
                                   ("linux/aarch64", "linux/arm64"),
                                   ("linux/arm64", "linux/arm64")):
            with patch.object(bsp, "docker", return_value=["docker"]), patch.object(
                    bsp, "run", return_value=SimpleNamespace(stdout=reported+"\n")) as run:
                self.assertEqual(expected, bsp.resolve_platform("native"))
                self.assertIn("info", run.call_args.args[0])

    def test_explicit_and_unsupported_platforms(self):
        with patch.object(bsp, "run") as run:
            self.assertEqual("linux/arm64", bsp.resolve_platform("linux/arm64"))
            run.assert_not_called()
            with self.assertRaises(ValueError):
                bsp.resolve_platform("linux/riscv64")
        with patch.object(bsp, "docker", return_value=["docker"]), patch.object(
                bsp, "run", return_value=SimpleNamespace(stdout="windows/amd64\n")):
            with self.assertRaises(ValueError):
                bsp.resolve_platform("native")

    def test_platform_specific_pins_and_provenance(self):
        for platform, host in (("linux/amd64", "x86_64"), ("linux/arm64", "aarch64")):
            data = bsp.lock(platform)
            self.assertEqual(platform, data["platform"])
            self.assertEqual("openembedded-core", data["toolchain_provider"])
            self.assertNotIn("arm_gnu", data)
            self.assertRegex(data["base_image"], r"@sha256:[a-f0-9]{64}$")
            cfg = bsp.configuration(build_platform=platform)
            self.assertNotIn("arm-build-host", cfg["local_conf_header"])
            with patch.object(bsp, "docker", return_value=["docker"]):
                argv = bsp.container_args("sha256:test", Path("/test"), False,
                                          build_platform=platform)
            self.assertEqual(platform, argv[argv.index("--platform")+1])
            self.assertIn("--network=none", argv)

    def test_work_directory_cannot_change_architecture(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bsp.bind_work_platform(root, "linux/arm64")
            bsp.bind_work_platform(root, "linux/arm64")
            with self.assertRaises(ValueError):
                bsp.bind_work_platform(root, "linux/amd64")

    def test_legacy_build_is_not_assumed_arm64(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "build").mkdir()
            with self.assertRaises(ValueError):
                bsp.bind_work_platform(root, "linux/arm64")
            bsp.bind_work_platform(root, "linux/amd64")

    def test_cached_image_platform_is_verified(self):
        selected = "linux/arm64"
        fingerprint = hashlib.sha256(
            (ROOT / "container/Dockerfile").read_bytes()
            + (ROOT / "container/lock.json").read_bytes()
            + selected.encode("ascii")).hexdigest()
        info = [{"Os": "linux", "Architecture": "amd64", "Id": "sha256:test",
                 "Config": {"Labels": {"org.fractalmicro.recipe": fingerprint}}}]
        with patch.object(bsp, "docker", return_value=["docker"]), patch.object(
                bsp.subprocess, "run", return_value=SimpleNamespace(
                    returncode=0, stdout=json.dumps(info))):
            with self.assertRaisesRegex(RuntimeError, "platform mismatch"):
                bsp.image(selected)

    def test_default_acl_work_is_refused(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(
                bsp.os, "listxattr", return_value=["system.posix_acl_default"]):
            with self.assertRaisesRegex(ValueError, "default ACLs"):
                bsp.bind_work_platform(Path(folder), "linux/arm64")
