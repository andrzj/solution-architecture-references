#!/usr/bin/env python3
"""Apply security editorial rewrites; preserve master mermaid/canvas byte-identical."""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAG = Path(__file__).parent / "security_rewrites"

SLUGS = [
    "zero-trust-architecture",
    "defense-in-depth",
    "threat-modeling",
    "identity-and-access-management",
    "authentication",
    "authorization-models",
]


def master_figure(slug: str) -> str:
    master = subprocess.check_output(
        ["git", "show", f"origin/master:security/{slug}.html"], text=True
    )
    m = re.search(
        r'<figure class="architecture-diagram".*?</figure>', master, re.DOTALL
    )
    if not m:
        raise RuntimeError(f"No figure in master {slug}")
    return m.group(0)


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def visible_words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*", strip_tags(s)))


def master_article_inner(slug: str) -> str:
    master = subprocess.check_output(
        ["git", "show", f"origin/master:security/{slug}.html"], text=True
    )
    m = re.search(
        r'<div class="article-content">(.*?)</div>\s*<nav class="article-nav"',
        master,
        re.DOTALL,
    )
    return m.group(1) if m else ""


def apply_slug(slug: str) -> None:
    frag_path = FRAG / f"{slug}.frag.html"
    if not frag_path.is_file():
        raise FileNotFoundError(frag_path)
    inner = frag_path.read_text(encoding="utf-8")
    if "__FIGURE__" not in inner:
        raise ValueError(f"{slug}: missing __FIGURE__ placeholder")
    inner = inner.replace("__FIGURE__", master_figure(slug))

    path = ROOT / "security" / f"{slug}.html"
    text = path.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r"(<div class=\"article-content\">).*?(</div>\s*<nav class=\"article-nav\")",
        r"\1\n" + inner + r"\n        \2",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        raise RuntimeError(f"Could not patch article-content for {slug}")
    path.write_text(new_text, encoding="utf-8")

    mw = visible_words(master_article_inner(slug))
    nw = visible_words(inner)
    ratio = nw / mw if mw else 0
    if strip_tags(inner) == strip_tags(master_article_inner(slug)):
        raise RuntimeError(f"{slug}: strip-tag identical to master")
    if ratio < 0.95:
        raise RuntimeError(f"{slug}: word ratio {ratio:.2%} < 95% ({nw}/{mw})")
    # byte-identical diagram check
    master = subprocess.check_output(
        ["git", "show", f"origin/master:security/{slug}.html"], text=True
    )
    for blob, name in [
        (master_figure(slug), "figure"),
    ]:
        fig_m = re.search(
            r'<div class="architecture-diagram__render mermaid">(.*?)</div>',
            master,
            re.DOTALL,
        )
        fig_n = re.search(
            r'<div class="architecture-diagram__render mermaid">(.*?)</div>',
            new_text,
            re.DOTALL,
        )
        if fig_m.group(1) != fig_n.group(1):
            raise RuntimeError(f"{slug}: mermaid not byte-identical")
        can_m = re.search(
            r'<pre class="architecture-diagram__canvas"><code>(.*?)</code></pre>',
            master,
            re.DOTALL,
        )
        can_n = re.search(
            r'<pre class="architecture-diagram__canvas"><code>(.*?)</code></pre>',
            new_text,
            re.DOTALL,
        )
        if can_m.group(1) != can_n.group(1):
            raise RuntimeError(f"{slug}: canvas not byte-identical")
    print(f"OK {slug}: words {nw}/{mw} ({ratio:.1%})")


def main() -> int:
    for slug in SLUGS:
        apply_slug(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())