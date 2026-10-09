# SPDX-License-Identifier: MIT
"""Publication checks inspect indexed contents, including new layer metadata."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("public_audit", ROOT / "scripts/audit-public.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PublicAuditTests(unittest.TestCase):
    def repository(self, folder, name, contents):
        repo = Path(folder)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_bytes(contents)
        subprocess.run(["git", "-C", str(repo), "add", "--", name], check=True)
        return repo

    def test_source_metadata_extensions(self):
        for name in ("board.dtsi", "braille.ktb", "Makefile.in", "refresh.timer", "70-device.rules", "openh432-wifi-start",
                     "recipes-core/openh432-boot-success/files/mark-good",
                     "recipes-core/openh432-root-handoff/files/early-sound",
                     "recipes-accessibility/openh432-speech/files/speech-audio",
                     "recipes-accessibility/openh432-braille/files/brltty.prefs"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                repo = self.repository(folder, name, b"# source metadata\n")
                self.assertEqual(audit.audit(repo)[0], 1)

    def test_rejects_firmware_and_binary_content(self):
        for name, data in (("firmware.bin", b"firmware"),
                           ("arbitrary.in", b"not an approved source name"),
                           ("unreviewed/mark-good", b"not an approved path"),
                           ("unreviewed/early-sound", b"not an approved path"),
                           ("unreviewed/speech-audio", b"not an approved path"),
                           ("unreviewed/brltty.prefs", b"not an approved path"),
                           ("recipes-core/openh432-boot-success/files/mark-good", b"binary\x00data"),
                           ("board.dtsi", b"binary\x00data"),
                           ("openh432-wifi-start", b"binary\x00data")):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                repo = self.repository(folder, name, data)
                with self.assertRaises(ValueError):
                    audit.audit(repo)

    def test_audits_index_not_unstaged_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = self.repository(folder, "README.md", b"bad\x00index")
            (repo / "README.md").write_text("clean working copy\n")
            with self.assertRaises(ValueError):
                audit.audit(repo)


if __name__ == "__main__":
    unittest.main()
