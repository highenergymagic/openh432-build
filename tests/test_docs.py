# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_docs", ROOT / "scripts/audit-docs.py")
audit_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_docs)

class PublicDocs(unittest.TestCase):
    def test_public_docs(self):
        self.assertEqual([], audit_docs.audit(ROOT))

    def test_context_and_links(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text(
                "The owner's supplied hashes.\n[missing](docs/missing.md)\n",
                encoding="utf-8")
            self.assertEqual(2, len(audit_docs.audit(root)))
            (root / "README.md").write_text(
                "Artifact nand51-raw is a USB-shell bootstrap.\n"
                "[external](https://example.org/test)\n", encoding="utf-8")
            self.assertEqual([], audit_docs.audit(root))

    def test_session_narration(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text(
                "The user confirmed the last test.\n"
                "Next we will try the other port.\n", encoding="utf-8")
            self.assertEqual(2, len(audit_docs.audit(root)))
