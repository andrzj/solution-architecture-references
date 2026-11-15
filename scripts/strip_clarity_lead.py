#!/usr/bin/env python3
"""Remove scripted clarity-pass opener: '<strong>Title</strong> is the pattern to use when...'."""

from __future__ import annotations

import re
import sys
from pathlib import Path

LEAD_PATTERNS = [
    re.compile(
        r"(<p(?:\s[^>]*)?>\s*)"
        r"<strong>[^<]+</strong>\s+is the pattern to use when\s+[^.<]*(?:\.[^<]*)?\.\s*",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"(<p(?:\s[^>]*)?>\s*)"
        r"<strong>[^<]+</strong>\s+is the decision to use when\s+[^.<]*(?:\.[^<]*)?\.\s*",
        re.IGNORECASE | re.DOTALL,
    ),
]

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "scripts", "docs", "templates", "glossary", "diagrams"}


def strip_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new = text
    n_total = 0
    for pat in LEAD_PATTERNS:
        new, n = pat.subn(r"\1", new, count=1)
        n_total += n
        if n:
            break
    if n_total == 0:
        return False
    # Collapse empty <p></p>
    new = re.sub(r"<p>\s*</p>", "", new)
    path.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for html in sorted(ROOT.rglob("*.html")):
        if any(p in SKIP for p in html.parts):
            continue
        if html.name == "index.html" and html.parent != ROOT:
            continue
        if strip_file(html):
            changed += 1
    print(f"Stripped templated opener from {changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())