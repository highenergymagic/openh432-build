# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RuntimeDefaults(unittest.TestCase):
    def test_default_targets_are_separate_nand_kernel_and_base(self):
        manifest = json.loads((ROOT / "kas/h432b.yml").read_text())
        self.assertEqual(manifest["target"],
                         ["openh432-nand-b", "openh432-systembase-b"])

if __name__ == "__main__":
    unittest.main()
