#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_version_block(changelog: str, version: str) -> str:
    """
    Extracts the changelog block for the given version (excludes the version header).

    Matches headers like:
      ## [1.2.3]
      ## [1.2.3] - 2024-02-01
    """

    # Header for the requested version (e.g. "## [0.16.1]")
    header_pattern = rf"^##\s+\[{re.escape(version)}\].*$"

    # Any version header marks the start of another block
    next_header_pattern = r"^##\s+\[.*\].*$"

    lines = changelog.splitlines()
    start = None
    end = None

    # Locate the version header
    for i, line in enumerate(lines):
        if re.match(header_pattern, line):
            start = i
            break

    if start is None:
        return ""

    # Locate next header after this one
    for j in range(start + 1, len(lines)):
        if re.match(next_header_pattern, lines[j]):
            end = j
            break

    # Extract lines after the header
    content_lines = lines[start + 1 : end] if end else lines[start + 1 :]

    # Trim empty lines at start and end
    while content_lines and not content_lines[0].strip():
        content_lines = content_lines[1:]
    while content_lines and not content_lines[-1].strip():
        content_lines = content_lines[:-1]

    return "\n".join(content_lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_changelog.py <CHANGELOG.md> <version>", file=sys.stderr)
        sys.exit(1)

    changelog_path = Path(sys.argv[1])
    version = sys.argv[2]

    text = changelog_path.read_text(encoding="utf-8")
    result = extract_version_block(text, version)

    if not result:
        print(f"No changelog entry found for version {version}", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
