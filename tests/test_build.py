# SPDX-License-Identifier: MIT
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bsp", ROOT / "scripts/bsp.py")
bsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bsp)


class BuildContract(unittest.TestCase):
    def test_pins(self):
        cfg = bsp.configuration()
        self.assertEqual(cfg["machine"], "h432b")
        self.assertEqual(cfg["distro"], "openh432")
        self.assertEqual(cfg["repos"]["openembedded-core"]["commit"],
                         "ef022bf82d79015802309d14c28b13373ebe53f5")
        self.assertEqual(bsp.lock()["toolchain_provider"], "openembedded-core")

    def test_container_has_no_external_target_compiler(self):
        dockerfile = (ROOT / "container/Dockerfile").read_text()
        self.assertNotIn("ARM_GNU", dockerfile)
        self.assertNotIn("/opt/arm-gnu", dockerfile)
        self.assertNotIn("arm_gnu", bsp.lock())
        for host in bsp.PLATFORMS:
            self.assertNotIn("arm-build-host", bsp.configuration(build_platform=host)["local_conf_header"])

    def test_repository_checkouts_do_not_overlap(self):
        paths = [Path(repo["path"]) for repo in bsp.configuration()["repos"].values()]
        for index, path in enumerate(paths):
            for other in paths[index + 1:]:
                self.assertNotEqual(path, other)
                self.assertNotIn(path, other.parents)
                self.assertNotIn(other, path.parents)

    def test_ci_covers_maintenance_and_nand_root(self):
        text = (ROOT / ".github/workflows/metadata.yml").read_text()
        for target in ("u-boot-h432b-maintenance-chain", "openh432-battery-test",
                       "openh432-nand-b", "openh432-systembase-b"):
            self.assertIn(target, text)

    def test_no_hardware_or_credentials(self):
        with patch.object(bsp, "docker", return_value=["docker"]):
            argv = bsp.container_args("sha256:test", Path("/tmp/yocto"), False)
        text = " ".join(map(str, argv))
        for forbidden in ("--privileged", "--device", "dst=/dev", ".ssh",
                          "docker.sock", "hosts.yml"):
            self.assertNotIn(forbidden, text)
        self.assertIn("--network=none", argv)
        self.assertIn("--cap-drop=ALL", argv)
        self.assertIn("1000:1000", argv)

    def test_fetch_network_separate(self):
        with patch.object(bsp, "docker", return_value=["docker"]):
            argv = bsp.container_args("sha256:test", Path("/tmp/yocto"), True)
        self.assertIn("--network=bridge", argv)

    def test_pinned_epoch_and_space_floor(self):
        cfg = bsp.configuration()
        self.assertIn('1791158400', cfg["local_conf_header"]["reproducibility"])
        self.assertIn("10G", cfg["local_conf_header"]["resources"])

    def test_not_auto_revisions(self):
        manifest = (ROOT / "kas/h432b.yml").read_text()
        self.assertNotIn("AUTOREV", manifest)
        for repo in json.loads(manifest)["repos"].values():
            self.assertRegex(repo["commit"], r"^[a-f0-9]{40}$")

    def test_public_audit_accepts_text_source_not_build_outputs(self):
        spec = importlib.util.spec_from_file_location("audit", ROOT / "scripts/audit-public.py")
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        self.assertTrue({".c", ".h", ".S", ".network"}.issubset(audit.ALLOWED_SUFFIXES))
        self.assertTrue({".bin", ".elf", ".img"}.issubset(audit.FORBIDDEN_SUFFIXES))
        self.assertIn("private", audit.FORBIDDEN_PARTS)

    def test_nand_profile_is_explicit_and_defaults_readonly(self):
        default = bsp.configuration()
        self.assertIn('H432B_NAND_PROFILE = "readonly"',
                      default["local_conf_header"]["nand-profile"])
        for profile in ("readonly", "scratch", "ubi"):
            cfg = bsp.configuration(nand_profile=profile)
            self.assertIn('H432B_NAND_PROFILE = "' + profile + '"',
                          cfg["local_conf_header"]["nand-profile"])
        with self.assertRaises(ValueError):
            bsp.configuration(nand_profile="whole-chip")

    def test_public_audit_rejects_credentials(self):
        spec = importlib.util.spec_from_file_location("audit", ROOT / "scripts/audit-public.py")
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        self.assertTrue(audit.SECRET.search(b"ghp_" + b"x" * 36))
        self.assertTrue(audit.SECRET.search(b"-----BEGIN " + b"OPENSSH PRIVATE" + b" KEY-----"))
        self.assertFalse(audit.SECRET.search(b"normal source text"))


if __name__ == "__main__":
    unittest.main()
