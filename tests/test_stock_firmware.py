# SPDX-License-Identifier: MIT
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


stock = module("stock_firmware", "stock_firmware.py")
bsp = module("bsp_stock", "bsp.py")
BASE = 0x80020000
PAYLOAD = b"x" * 129816


def image(compressed=False, duplicate=False, missing=False):
    memory = bytearray(0x400 + len(PAYLOAD))
    struct.pack_into("<II", memory, 0x40, 0x43454345, BASE + 0x100)
    fields = [0] * 22
    fields[12] = 2 if duplicate else 1
    struct.pack_into("<17IHH3I", memory, 0x100, *fields)
    name = b"other.bin\0" if missing else b"rtl8712fw.bin\0"
    memory[0x200:0x200 + len(name)] = name
    for i in range(fields[12]):
        struct.pack_into("<7I", memory, 0x154 + i * 28,
                         0, 0, 0, len(PAYLOAD), len(PAYLOAD) - int(compressed),
                         BASE + 0x200, BASE + 0x400)
    memory[0x400:] = PAYLOAD
    return record_image([(BASE, bytes(memory))])


def record_image(records):
    output = b"B000FF\n" + struct.pack("<II", BASE, 0x100000)
    for address, payload in records:
        output += struct.pack("<III", address, len(payload), sum(payload) & 0xffffffff) + payload
    return output + struct.pack("<III", 0, BASE, 0)


class StockFirmware(unittest.TestCase):
    def test_extracts_named_file(self):
        self.assertEqual(stock.Rom(image()).firmware(), PAYLOAD)

    def test_manufacturer_trailer(self):
        self.assertEqual(stock.Rom(image() + b"HIMS\0H432B\0" + b"\0" * 19).firmware(), PAYLOAD)

    def test_cross_record_reads(self):
        rom = stock.Rom(record_image([(BASE, b"abc"), (BASE + 3, b"def")]))
        self.assertEqual(rom.read(BASE + 1, 4), b"bcde")

    def test_corruption(self):
        data = bytearray(image())
        data[100] ^= 1
        with self.assertRaisesRegex(ValueError, "checksum"):
            stock.Rom(bytes(data))

    def test_truncation_and_trailing_data(self):
        data = image()
        for broken in (b"", data[:20], data[:-1], data + b"junk"):
            with self.subTest(length=len(broken)), self.assertRaises(ValueError):
                stock.Rom(broken)

    def test_overlap_and_gap(self):
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            stock.Rom(record_image([(BASE, b"abc"), (BASE + 1, b"def")]))
        rom = stock.Rom(record_image([(BASE, b"a"), (BASE + 2, b"c")]))
        with self.assertRaisesRegex(ValueError, "Unmapped"):
            rom.read(BASE, 3)

    def test_missing_duplicate_compressed(self):
        for kwargs in ({"missing": True}, {"duplicate": True}, {"compressed": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                stock.Rom(image(**kwargs)).firmware()

    def test_stock_and_payload_hashes(self):
        data = image()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "nk.bin"
            source.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "Unsupported stock"):
                stock.extract(source)
            with patch.object(stock, "STOCK_SHA256", hashlib.sha256(data).hexdigest()):
                with self.assertRaisesRegex(ValueError, "Extracted firmware"):
                    stock.extract(source)
                with patch.object(stock, "FIRMWARE_SHA256", hashlib.sha256(PAYLOAD).hexdigest()):
                    payload, provenance = stock.extract(source)
                    self.assertEqual(payload, PAYLOAD)
                    self.assertEqual(provenance["stock_nk_sha256"], hashlib.sha256(data).hexdigest())

    def test_atomic_private_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "firmware"
            unrelated = Path(directory) / "unrelated"
            unrelated.write_bytes(b"keep")
            target.symlink_to(unrelated)
            stock.private_write(target, PAYLOAD)
            self.assertEqual(unrelated.read_bytes(), b"keep")
            self.assertFalse(target.is_symlink())
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_required_for_fetch_and_build(self):
        for action in ("fetch", "build"):
            with self.assertRaisesRegex(ValueError, "--stock-nk"):
                bsp.require_stock_input(action, None, False)
            bsp.require_stock_input(action, "nk.bin", False)
            bsp.require_stock_input(action, None, True)
        for action in ("checkout", "parse", "graph", "image"):
            bsp.require_stock_input(action, None, False)

    def test_extraction_is_offline_in_selected_container(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "nk.bin"
            source.write_bytes(b"fixture")
            result = Mock(stdout=json.dumps({"firmware_sha256": "fixture"}))
            with patch.object(bsp, "docker", return_value=["docker"]), patch.object(bsp, "run", return_value=result) as run:
                bsp.extract_stock_firmware("sha256:builder", Path(directory), source, "linux/arm64")
            argv = run.call_args.args[0]
            self.assertIn("--network=none", argv)
            self.assertIn("linux/arm64", argv)
            self.assertIn("type=bind,src=" + str(source) + ",dst=/input/nk.bin,readonly", argv)
            self.assertLess(argv.index("--mount"), argv.index("sha256:builder"))
            self.assertIn("/repo/scripts/stock_firmware.py", argv)
            self.assertNotIn("--privileged", argv)


if __name__ == "__main__":
    unittest.main()
