# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("layer_runner", ROOT / "scripts/test-layers.py")
runner = importlib.util.module_from_spec(spec)
with patch.object(sys, "path", [str(ROOT / "scripts"), *sys.path]):
    spec.loader.exec_module(runner)


class LayerRunner(unittest.TestCase):
    def test_readonly_offline_native_test_command(self):
        paths = {name: Path("/tmp/layers") / name for name in runner.LAYERS}
        for platform in runner.bsp.PLATFORMS:
            with self.subTest(platform=platform), patch.object(
                    runner.bsp, "docker", return_value=["docker"]):
                command = runner.container_command("sha256:builder", paths, platform)
            self.assertEqual(command[command.index("--platform") + 1], platform)
            for value in ("--network=none", "--read-only", "--cap-drop=ALL",
                          "--security-opt=no-new-privileges", "1000:1000"):
                self.assertIn(value, command)
            for variable in runner.COMPILER_VARIABLES:
                self.assertIn(variable + "=/usr/bin/cc", command)
            mounts = [command[i + 1] for i, item in enumerate(command) if item == "--mount"]
            self.assertEqual(len(mounts), 3)
            self.assertTrue(all(mount.endswith(",readonly") for mount in mounts))
            for forbidden in ("--privileged", "--device", "dst=/dev", "docker.sock", ".ssh"):
                self.assertNotIn(forbidden, " ".join(command))
            for name in runner.LAYERS:
                self.assertIn("/layers/" + name + "/tests", command[-1])

    def test_missing_layer_fails_before_docker(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "Missing layer/tests"):
                runner.layer_paths(Path(folder))

    def test_selects_checked_out_or_local_layers(self):
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder) / "work"
            parent = Path(folder) / "repos"
            for base in (work / "layers", parent):
                for name in runner.LAYERS:
                    layer = base / name
                    (layer / "conf").mkdir(parents=True)
                    (layer / "conf/layer.conf").touch()
                    (layer / "tests").mkdir()
            with patch.object(runner.bsp, "ROOT", parent / "openh432-build"):
                for local, base in ((False, work / "layers"), (True, parent)):
                    self.assertEqual(runner.layer_paths(work, local),
                                     {name: base / name for name in runner.LAYERS})

    def test_skipped_tests_fail_the_ci_runner(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "test_example.py"
            for decorator, success in (("", True), ('@unittest.skip("compiler absent")', False)):
                source.write_text("import unittest\nclass Example(unittest.TestCase):\n" +
                                  ("    " + decorator + "\n" if decorator else "") +
                                  "    def test_example(self): pass\n")
                result = subprocess.run([sys.executable, "-B", "-c", runner.CHECK, folder],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode == 0, success, result.stderr)

    def test_workflow_uses_pinned_runner(self):
        workflow = (ROOT / ".github/workflows/metadata.yml").read_text()
        self.assertIn('python3 scripts/test-layers.py --work "$RUNNER_TEMP/openh432-work"', workflow)
        self.assertNotIn('unittest discover -s "$RUNNER_TEMP/openh432-work/layers/', workflow)


if __name__ == "__main__":
    unittest.main()
