"""Shared helpers for site index, search, and coverage verification."""

from __future__ import annotations

import html as html_lib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_PARENTS = frozenset(
    {
        "templates",
        "glossary",
        "diagrams",
        "scripts",
        "docs",
        ".git",
        "assets",
    }
)

SEARCH_SKIP_PARENTS = frozenset(
    {
        "glossary",
        "diagrams",
        "scripts",
        "docs",
        ".git",
        "assets",
    }
)

CATEGORY_SKIP_FOR_LISTING = SKIP_PARENTS | {"decision-guides"}


def is_searchable_article(path: Path) -> bool:
    if path.suffix != ".html" or path.name == "index.html":
        return False
    if path.parent == ROOT:
        return False
    if any(part in SEARCH_SKIP_PARENTS for part in path.parts):
        return False
    return True


def is_category_indexable(path: Path) -> bool:
    """Articles that should appear on their category index.html listing."""
    if path.suffix != ".html" or path.name == "index.html":
        return False
    if path.parent == ROOT:
        return False
    if path.parent.name in CATEGORY_SKIP_FOR_LISTING:
        return False
    if path.parent.name == "decision-guides":
        return False
    return True


def category_dirs() -> list[Path]:
    dirs: list[Path] = []
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir():
            continue
        if child.name in CATEGORY_SKIP_FOR_LISTING or child.name.startswith("."):
            continue
        if (child / "index.html").is_file():
            dirs.append(child)
    return dirs


def articles_in_category(cat_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in cat_dir.glob("*.html")
        if p.name != "index.html" and is_category_indexable(p)
    )


def extract_title(page_html: str) -> str:
    m = re.search(
        r'<h1 class="article-header__title">([^<]+)</h1>', page_html, re.IGNORECASE
    )
    if m:
        return html_lib.unescape(m.group(1).strip())
    m = re.search(r"<title>([^<]+)</title>", page_html, re.IGNORECASE)
    if m:
        title = m.group(1).strip()
        title = re.sub(r"\s*—\s*SA References\s*$", "", title)
        return html_lib.unescape(title)
    return "Untitled"


def extract_what_it_is_summary(page_html: str) -> str:
    m = re.search(
        r'<h2 id="what-it-is">.*?</h2>\s*<p>(.*?)</p>',
        page_html,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", "", m.group(1))
    text = html_lib.unescape(re.sub(r"\s+", " ", text)).strip()
    if not text:
        return ""
    sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    if len(sentence) > 240:
        sentence = sentence[:237].rstrip() + "…"
    return sentence


def category_section_name(cat_dir: Path) -> str:
    idx = cat_dir / "index.html"
    if idx.is_file():
        text = idx.read_text(encoding="utf-8", errors="replace")
        m = re.search(
            r'<h1 class="section-header__title">([^<]+)</h1>', text, re.IGNORECASE
        )
        if m:
            return html_lib.unescape(m.group(1).strip())
    return cat_dir.name.replace("-", " ").title()


def build_search_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in sorted(ROOT.rglob("*.html")):
        if not is_searchable_article(path):
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        cat = path.parent.name
        if cat == "decision-guides":
            section = "Decision Guides"
        elif cat == "templates":
            section = "Templates"
        else:
            section = category_section_name(path.parent)
        entries.append(
            {
                "title": extract_title(html),
                "path": rel,
                "section": section,
                "description": extract_what_it_is_summary(html),
            }
        )
    return entries


def local_index_hrefs(index_html: str) -> set[str]:
    return set(re.findall(r'href="([a-z0-9][a-z0-9-]*\.html)"', index_html))


def expected_homepage_count(cat_slug: str, n: int) -> str:
    if cat_slug == "decision-guides":
        return f"{n} guides"
    if cat_slug == "templates":
        return f"{n} templates"
    return f"{n} articles"