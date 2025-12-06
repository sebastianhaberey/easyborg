#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_version_block(changelog: str, version: str) -> str:
    """
    Extracts the changelog block for a given version.
    Always includes the version header.

    Matches headers like:
      ## [1.2.3]
      ## [1.2.3] - 2024-02-01
    """

    # Header for the version we want
    header_pattern = rf"^##\s+\[{re.escape(version)}\].*$"

    # Any version header (used as delimiter)
    next_header_pattern = r"^##\s+\[.*\].*$"

    lines = changelog.splitlines()
    start = None
    end = None

    # Locate start header
    for i, line in enumerate(lines):
        if re.match(header_pattern, line):
            start = i
            break

    if start is None:
        return ""

    # Locate next header after the start
    for j in range(start + 1, len(lines)):
        if re.match(next_header_pattern, lines[j]):
            end = j
            break

    # Extract block
    block_lines = lines[start:end] if end else lines[start:]

    # Remove trailing or leading blank lines
    while block_lines and not block_lines[0].strip():
        block_lines = block_lines[1:]
    while block_lines and not block_lines[-1].strip():
        block_lines = block_lines[:-1]

    return "\n".join(block_lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_changelog.py <CHANGELOG.md> <version>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    version = sys.argv[2]

    text = path.read_text(encoding="utf-8")
    result = extract_version_block(text, version)

    if not result:
        print(f"No changelog entry found for version {version}", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
