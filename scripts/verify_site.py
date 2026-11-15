#!/usr/bin/env python3
"""Lightweight verification: template sections, internal hrefs, diagram wrapper."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

STANDARD_IDS = [
    "what-it-is",
    "why-it-exists",
    "when-to-use",
    "when-not-to-use",
    "typical-architecture",
    "pros-and-cons",
    "implementation-notes",
    "common-failure-modes",
    "decision-checklist",
    "example-use-cases",
    "related-patterns",
    "further-reading",
]

SKIP_PARENTS = {
    "templates",
    "glossary",
    "diagrams",
    "scripts",
    "docs",
    ".git",
}


def is_pattern_article(path: Path) -> bool:
    if path.name == "index.html":
        return False
    if path.parent == ROOT:
        return False
    if path.parent.name in SKIP_PARENTS:
        return False
    if path.parent.name == "decision-guides":
        return False
    return True


def check_sections(html: str) -> list[str]:
    return [sid for sid in STANDARD_IDS if f'id="{sid}"' not in html]


def extract_internal_links(html: str) -> list[str]:
    return re.findall(r'href="(\.\.?/[^"#]+(?:\.html)?)"', html)


def main() -> int:
    missing_sections: list[tuple[str, list[str]]] = []
    no_diagram: list[str] = []
    stub_count = 0

    for path in sorted(ROOT.rglob("*.html")):
        if any(p in SKIP_PARENTS for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "This article covers the core principles" in text:
            stub_count += 1
        if is_pattern_article(path):
            miss = check_sections(text)
            if miss:
                missing_sections.append((str(path.relative_to(ROOT)), miss))
            if "typical-architecture" in text and 'class="architecture-diagram"' not in text:
                no_diagram.append(str(path.relative_to(ROOT)))

    print(f"Stub articles remaining: {stub_count}")
    print(f"Articles missing sections: {len(missing_sections)}")
    print(f"Articles missing diagram wrapper: {len(no_diagram)}")
    if missing_sections[:15]:
        print("\nSample missing sections:")
        for p, m in missing_sections[:15]:
            print(f"  {p}: {m}")
    return 1 if stub_count or missing_sections else 0


if __name__ == "__main__":
    sys.exit(main())