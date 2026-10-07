#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract the qualified radio firmware from a private stock CE image."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile

STOCK_SHA256 = "aa1f108511a39303ee37f531e49fc8f7dd7db3cf11960a5e592cfb1fb2283315"
FIRMWARE_SHA256 = "a586c6d2253d2890f8a853c3d98dfc0f880be1b0c9a420057a2436fc6523a4d7"
MAX_IMAGE = 128 * 1024 * 1024


class Rom:
    """Bounded B000FF record reader; never executes or decompresses input."""

    def __init__(self, data):
        if len(data) < 15 or not data.startswith(b"B000FF\n"):
            raise ValueError("Expected a stock B000FF CE image")
        self.records = []
        offset = 15
        while True:
            if offset + 12 > len(data):
                raise ValueError("Truncated CE record header")
            address, size, checksum = struct.unpack_from("<III", data, offset)
            offset += 12
            if address == 0 and checksum == 0:
                trailer = data[offset:]
                if trailer and (len(trailer) != 30 or not trailer.startswith(b"HIMS\x00H432B\x00")):
                    raise ValueError("Unexpected CE manufacturer trailer")
                break
            if not size or address + size > 2**32 or offset + size > len(data):
                raise ValueError("Invalid CE record extent")
            payload = data[offset:offset + size]
            if sum(payload) & 0xffffffff != checksum:
                raise ValueError("CE record checksum mismatch")
            self.records.append((address, payload))
            if len(self.records) > 65536:
                raise ValueError("Excessive CE record count")
            offset += size
        self.records.sort(key=lambda entry: entry[0])
        end = 0
        for address, payload in self.records:
            if address < end:
                raise ValueError("Overlapping CE records")
            end = address + len(payload)

    def read(self, address, size):
        if size < 0 or size > MAX_IMAGE or address < 0 or address + size > 2**32:
            raise ValueError("Invalid CE address range")
        result = bytearray()
        cursor = address
        for start, payload in self.records:
            end = start + len(payload)
            if end <= cursor:
                continue
            if start > cursor:
                break
            take = min(size - len(result), end - cursor)
            result.extend(payload[cursor - start:cursor - start + take])
            cursor += take
            if len(result) == size:
                return bytes(result)
        raise ValueError("Unmapped CE address range")

    def name(self, address):
        result = bytearray()
        for offset in range(260):
            value = self.read(address + offset, 1)[0]
            if not value:
                return result.decode("ascii").lower()
            result.append(value)
        raise ValueError("Unterminated CE filename")

    def firmware(self):
        signature, header = struct.unpack("<II", self.read(0x80020040, 8))
        if signature != 0x43454345:
            raise ValueError("Missing CE ROM signature")
        fields = struct.unpack("<17IHH3I", self.read(header, 0x54))
        modules, files = fields[4], fields[12]
        if modules > 4096 or files > 4096:
            raise ValueError("Invalid CE directory count")
        directory = header + 0x54 + modules * 32
        matches = []
        for index in range(files):
            entry = struct.unpack("<7I", self.read(directory + index * 28, 28))
            _, _, _, real, stored, name, load = entry
            if self.name(name) == "rtl8712fw.bin":
                if real != stored:
                    raise ValueError("Compressed radio firmware is not supported")
                if real != 129816:
                    raise ValueError("Unexpected radio firmware length")
                matches.append(self.read(load, stored))
        if len(matches) != 1:
            raise ValueError("Expected exactly one rtl8712fw.bin in stock CE file table")
        return matches[0]


def extract(source):
    with Path(source).open("rb") as stream:
        data = stream.read(MAX_IMAGE + 1)
    if len(data) > MAX_IMAGE:
        raise ValueError("Stock image exceeds size limit")
    stock_digest = hashlib.sha256(data).hexdigest()
    if stock_digest != STOCK_SHA256:
        raise ValueError("Unsupported stock nk.bin: expected the qualified nk_200617.bin SHA-256")
    payload = Rom(data).firmware()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != FIRMWARE_SHA256:
        raise ValueError("Extracted firmware does not match the qualified SHA-256")
    return payload, {"stock_nk_sha256": stock_digest, "firmware_sha256": digest,
                     "firmware_bytes": len(payload), "extractor_schema": 1}


def private_write(path, data):
    """Atomic replacement; do not follow an existing output symlink."""
    fd, temporary = tempfile.mkstemp(prefix=".extract-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-nk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload, provenance = extract(args.stock_nk)
    if args.output.is_symlink():
        parser.error("Private output directory must not be a symlink")
    args.output.mkdir(mode=0o700, parents=True, exist_ok=True)
    args.output.chmod(0o700)
    private_write(args.output / "rtl8712s.bin", payload)
    private_write(args.output / "provenance.json",
                  (json.dumps(provenance, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps(provenance, sort_keys=True))


if __name__ == "__main__":
    main()
