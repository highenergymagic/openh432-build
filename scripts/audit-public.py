#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the exact Git index before publication; not a complete legal/secret audit."""
import argparse
from pathlib import Path
import re
import subprocess

FORBIDDEN_PARTS = {".ssh", ".git", "cache", "work", "out", "evidence", "private",
                   "node_modules", "target", "__pycache__"}
FORBIDDEN_SUFFIXES = {".bin", ".nb0", ".img", ".ubi", ".ubifs", ".dtb", ".elf",
                      ".exe", ".dll", ".zip", ".gz", ".xz", ".wav", ".log",
                      ".pem", ".key", ".p12", ".pyc", ".gpr"}
SECRET = re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|"
                    rb"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|"
                    rb"AKIA[A-Z0-9]{16}")
ALLOWED_SUFFIXES = {".md", ".py", ".bb", ".bbappend", ".bbclass", ".inc", ".conf",
                    ".config", ".patch", ".dts", ".dtsi", ".json", ".yml", ".yaml",
                    ".ktb", ".service", ".timer", ".rules", ".network", ".preset", ".sh", ".txt", ".c", ".h", ".S"}
ALLOWED_NAMES = {"LICENSE", "COPYING", "Dockerfile", "Makefile", "Makefile.in", ".gitignore",
                 ".gitattributes", "init", "series", "openh432-wifi-start", "GPL-2.0-only", "GPL-2.0-or-later"}

# Extensionless runtime helpers; approve reviewed paths, not arbitrary names.
ALLOWED_PATHS = {"recipes-core/openh432-boot-success/files/mark-good",
                 "recipes-core/openh432-root-handoff/files/early-sound",
                 "recipes-accessibility/openh432-speech/files/speech-audio",
                 "recipes-accessibility/openh432-braille/files/brltty.prefs"}


def audit(repo):
    names = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "--stage", "-z"]).split(b"\0")
    count = total = 0
    problems = []
    for entry in names:
        if not entry:
            continue
        metadata, encoded = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = encoded.decode()
        path = Path(name)
        if mode not in ("100644", "100755") or stage != "0":
            problems.append(name + ": symlink/submodule/conflict not approved")
            continue
        if (any(part in FORBIDDEN_PARTS for part in path.parts)
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
            or (path.suffix not in ALLOWED_SUFFIXES and path.name not in ALLOWED_NAMES
                and name not in ALLOWED_PATHS)
            or path.name.startswith(".env")):
            problems.append(name + ": not in source-only allowlist")
            continue
        data = subprocess.check_output(["git", "-C", str(repo), "cat-file", "blob", oid])
        if b"\0" in data or len(data) > 512 * 1024:
            problems.append(name + ": binary/oversized input")
        if SECRET.search(data):
            problems.append(name + ": possible credential")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            problems.append(name + ": not UTF-8 source")
        count += 1
        total += len(data)
    if not count:
        problems.append("Empty index")
    if problems:
        raise ValueError("\n".join(problems))
    return count, total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", nargs="+", type=Path)
    args = parser.parse_args()
    for repository in args.repositories:
        count, total = audit(repository)
        print(f"{repository.name}: PASS, {count} indexed text files, {total} bytes")
