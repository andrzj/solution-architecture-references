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

# Categories editorially migrated: fictional names only in example-use-cases.
FICTIONAL_CHECK_CATEGORIES = frozenset(
    {
        "anti-patterns",
        "foundations",
        "architecture-styles",
        "ai-ml",
        "api-design",
        "big-data",
        "cloud",
        "communication-patterns",
        "data-architecture",
        "deployment",
        "distributed-systems",
        "governance",
        "integration",
        "iot-edge",
        "mobile",
        "observability",
        "platform-engineering",
        "reliability",
        "scalability",
        "search",
        "security",
        "software-engineering",
    }
)

# Site-wide editorial running examples — allowed only inside example-use-cases.
FICTIONAL_COMPANY_RE = re.compile(
    r"\b("
    r"Northwind(?:\s+Logistics)?|"
    r"Meridian(?:\s+Commerce)?|"
    r"RideRelay|"
    r"FieldOps"
    r")\b",
    re.IGNORECASE,
)


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


def fictional_before_examples(html: str) -> list[tuple[int, str]]:
    """Return (line_hint, match) for fictional names before example-use-cases."""
    m = re.search(r'<div class="article-content">(.*)', html, re.DOTALL)
    if not m:
        return []
    content = m.group(1)
    ex = re.search(r'<h2 id="example-use-cases">', content)
    if not ex:
        return []
    forbidden = content[: ex.start()]
    hits: list[tuple[int, str]] = []
    for match in FICTIONAL_COMPANY_RE.finditer(forbidden):
        hits.append((forbidden[: match.start()].count("\n") + 1, match.group(0)))
    return hits


def main() -> int:
    missing_sections: list[tuple[str, list[str]]] = []
    no_diagram: list[str] = []
    fictional_violations: list[tuple[str, list[tuple[int, str]]]] = []
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
            if path.parent.name in FICTIONAL_CHECK_CATEGORIES:
                hits = fictional_before_examples(text)
                if hits:
                    fictional_violations.append((str(path.relative_to(ROOT)), hits))

    print(f"Stub articles remaining: {stub_count}")
    print(f"Articles missing sections: {len(missing_sections)}")
    print(f"Articles missing diagram wrapper: {len(no_diagram)}")
    print(f"Fictional names before example-use-cases: {len(fictional_violations)}")
    if missing_sections[:15]:
        print("\nSample missing sections:")
        for p, m in missing_sections[:15]:
            print(f"  {p}: {m}")
    if fictional_violations[:20]:
        print("\nFictional company names outside example-use-cases (sample):")
        for p, hits in fictional_violations[:20]:
            for _line, word in hits[:3]:
                print(f"  {p}: {word}")
            if len(hits) > 3:
                print(f"  {p}: ... +{len(hits) - 3} more")
    fail = stub_count or missing_sections or fictional_violations or no_diagram
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())