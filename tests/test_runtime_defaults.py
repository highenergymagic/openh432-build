# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RuntimeDefaults(unittest.TestCase):
    def test_default_targets_include_managed_loader_kernel_and_base(self):
        manifest = json.loads((ROOT / "kas/h432b.yml").read_text())
        self.assertEqual(manifest["target"],
                         ["openh432-nand-b", "openh432-systembase-b",
                          "u-boot-h432b-ab-chain"])

if __name__ == "__main__":
    unittest.main()
