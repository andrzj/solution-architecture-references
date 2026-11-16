#!/usr/bin/env python3
"""Lightweight verification: template sections, internal hrefs, diagram wrapper."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from site_index_lib import (  # noqa: E402
    ROOT,
    articles_in_category,
    build_search_entries,
    category_dirs,
    expected_homepage_count,
    local_index_hrefs,
)

SEARCH_INDEX_JSON = ROOT / "assets" / "data" / "search-index.json"

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


def check_category_indexes() -> list[str]:
    errors: list[str] = []
    for cat_dir in category_dirs():
        idx = cat_dir / "index.html"
        html = idx.read_text(encoding="utf-8", errors="replace")
        linked = local_index_hrefs(html)
        for art in articles_in_category(cat_dir):
            if art.name not in linked:
                errors.append(
                    f"{idx.relative_to(ROOT)}: missing listing for {art.name}"
                )
        for href in linked:
            target = cat_dir / href
            if not target.is_file():
                errors.append(
                    f"{idx.relative_to(ROOT)}: broken local link {href}"
                )
    return errors


def check_homepage_counts() -> list[str]:
    homepage = ROOT / "index.html"
    html = homepage.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for block in re.findall(
        r'<a href="([^"]+/index\.html)" class="category-card"[^>]*>(.*?)</a>',
        html,
        flags=re.DOTALL,
    ):
        href, body = block
        cat = href.replace("/index.html", "").strip("./")
        m = re.search(r'<span class="category-card__count">([^<]+)</span>', body)
        if not m:
            continue
        displayed = m.group(1).strip()
        cat_dir = ROOT / cat
        if not cat_dir.is_dir():
            errors.append(f"index.html: unknown category {cat}")
            continue
        n = len([p for p in cat_dir.glob("*.html") if p.name != "index.html"])
        expected = expected_homepage_count(cat, n)
        if displayed != expected:
            errors.append(
                f"index.html: {cat} shows {displayed!r}, expected {expected!r}"
            )
    return errors


def check_search_index() -> list[str]:
    errors: list[str] = []
    expected = {e["path"] for e in build_search_entries()}
    if not SEARCH_INDEX_JSON.is_file():
        return [f"Missing {SEARCH_INDEX_JSON.relative_to(ROOT)}"]
    data = json.loads(SEARCH_INDEX_JSON.read_text(encoding="utf-8"))
    indexed = {item["path"] for item in data}
    missing = expected - indexed
    extra = indexed - expected
    for path in sorted(missing):
        errors.append(f"search-index.json missing {path}")
    for path in sorted(extra):
        errors.append(f"search-index.json extra entry {path}")
    for path in sorted(indexed):
        if not (ROOT / path).is_file():
            errors.append(f"search-index.json path not found: {path}")
    main_js = (ROOT / "assets" / "js" / "main.js").read_text(
        encoding="utf-8", errors="replace"
    )
    paths_in_js = set(re.findall(r'path: "([^"]+)"', main_js))
    if paths_in_js != indexed:
        only_js = paths_in_js - indexed
        only_json = indexed - paths_in_js
        for path in sorted(only_js):
            errors.append(f"main.js SEARCH_INDEX missing {path} (not in JSON)")
        for path in sorted(only_json):
            errors.append(f"main.js SEARCH_INDEX extra {path} (not in JSON)")
    return errors


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

    index_errors = check_category_indexes()
    homepage_errors = check_homepage_counts()
    search_errors = check_search_index()

    print(f"Stub articles remaining: {stub_count}")
    print(f"Articles missing sections: {len(missing_sections)}")
    print(f"Articles missing diagram wrapper: {len(no_diagram)}")
    print(f"Fictional names before example-use-cases: {len(fictional_violations)}")
    print(f"Category index coverage errors: {len(index_errors)}")
    print(f"Homepage count errors: {len(homepage_errors)}")
    print(f"Search index errors: {len(search_errors)}")
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
    if index_errors[:20]:
        print("\nCategory index issues (sample):")
        for line in index_errors[:20]:
            print(f"  {line}")
    if homepage_errors:
        print("\nHomepage count issues:")
        for line in homepage_errors:
            print(f"  {line}")
    if search_errors[:20]:
        print("\nSearch index issues (sample):")
        for line in search_errors[:20]:
            print(f"  {line}")

    fail = (
        stub_count
        or missing_sections
        or fictional_violations
        or no_diagram
        or index_errors
        or homepage_errors
        or search_errors
    )
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())