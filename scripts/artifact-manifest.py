#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hash deployed target images; compare payload bytes, not host/container IDs."""
import argparse
import hashlib
import json
from pathlib import Path

# Current NAND deployment set. Historical comparisons use their pinned
# orchestration revision and schema-1 manifest (docs/cross-host-validation.md).
ARTIFACTS = (
    "nand-ab-ce-carrier/u-boot-ce.b000ff",
    "openh432-nand-b.img",
    "openh432-systembase-b-h432b.rootfs.squashfs",
)

def manifest(deploy):
    deploy = Path(deploy).resolve()
    result = {}
    for name in ARTIFACTS:
        path = (deploy / name).resolve(strict=True)
        if not path.is_relative_to(deploy) or not path.is_file():
            raise ValueError("Artifact escapes deploy directory or is not a file: " + name)
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(block)
        result[name] = {"bytes": path.stat().st_size, "sha256": sha.hexdigest()}
    return {"schema": 4, "artifacts": result}

def differences(reference, actual):
    if reference.get("schema") != 4 or set(reference.get("artifacts", {})) != set(ARTIFACTS):
        raise ValueError("Reference must contain the complete schema-4 A/B NAND artifact set")
    return [name for name in ARTIFACTS
            if reference["artifacts"][name] != actual["artifacts"][name]]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deploy", type=Path)
    parser.add_argument("--compare", type=Path, help="Reference manifest; exit 1 if any bytes differ")
    args = parser.parse_args()
    result = manifest(args.deploy)
    if args.compare:
        mismatch = differences(json.loads(args.compare.read_text()), result)
        for name in mismatch:
            print("MISMATCH " + name)
        if mismatch:
            return 1
        print(f"All {len(ARTIFACTS)} target artifacts match in size and SHA256.")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
