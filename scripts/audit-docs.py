#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check public landing pages/docs for private lab context and broken local links.

This is a regression check, not a substitute for editorial or secret review.
Technical artifact identifiers are permitted; document their roles explicitly.
"""
import argparse
from pathlib import Path
import re

PATTERNS = (
    r"(?i)\bssh\s+[^\s@]+@[^\s]+",
    r"(?i)(?:/home/[^/\s]+/|[CP]:\\Users\\|P:\\archives\\)",
    r"(?i)\b(?:this conversation|our discussion|owner's supplied|user's hard)\b",
    r"(?i)\b(?:currently NAND\d+|yesterday|just now)\b",
    r"(?i)evidence/private/",
    r"(?i)\b(?:the user confirmed|the user reported|next we will|left the device running)\b",
)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")

def audit(root):
    root = Path(root).resolve()
    files = [p for p in (root / "README.md",) if p.is_file()]
    if (root / "docs").is_dir():
        files += sorted((root / "docs").rglob("*.md"))
    errors = []
    for path in files:
        content = path.read_text(encoding="utf-8")
        for number, line in enumerate(content.splitlines(), 1):
            for pattern in PATTERNS:
                if re.search(pattern, line):
                    errors.append(f"{path.relative_to(root)}:{number}: conversation/private context")
            for target in LINK.findall(line):
                target = target.split("#", 1)[0]
                if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                if not (path.parent / target).exists():
                    errors.append(f"{path.relative_to(root)}:{number}: broken local link {target}")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", nargs="+", type=Path)
    args = parser.parse_args()
    errors = []
    for root in args.repositories:
        if not (root / ".git").exists():
            parser.error(f"Not a repository: {root}")
        errors.extend(f"{root.name}/{error}" for error in audit(root))
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"Public documentation checks passed for {len(args.repositories)} repositories.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
