#!/usr/bin/env python3
"""Wrap ASCII diagrams under #typical-architecture in <figure class="architecture-diagram">."""

from __future__ import annotations

import re
import sys
from pathlib import Path

FIGURE_END = "</figure>"

WRAPPED_MARKER = 'class="architecture-diagram"'


def wrap_diagram_in_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if WRAPPED_MARKER in text:
        return False

    pattern = re.compile(
        r'(<h2 id="typical-architecture">[^<]+</h2>\s*)'
        r'(?:(<p>.*?</p>\s*))?'
        r'(<pre(?:\s[^>]*)?><code>(.*?)</code></pre>)',
        re.DOTALL,
    )

    def repl(match: re.Match[str]) -> str:
        heading_block = match.group(1)
        intro = match.group(2) or ""
        pre_block = match.group(3)
        pre_inner = pre_block
        if 'class="architecture-diagram__canvas"' not in pre_inner:
            pre_inner = pre_inner.replace("<pre", '<pre class="architecture-diagram__canvas"', 1)
        figure = (
            f'{heading_block}{intro}'
            f'<figure class="architecture-diagram" role="img" aria-labelledby="typical-architecture-caption">\n'
            f"          {pre_inner}\n"
            f'          <figcaption id="typical-architecture-caption" class="architecture-diagram__caption">'
            f"Text-based reference diagram for this pattern. "
            f"Read top to bottom; boxes show components and lines show data or call flow."
            f"</figcaption>\n"
            f"          </figure>"
        )
        return figure

    new_text, count = pattern.subn(repl, text, count=1)
    if count == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    updated = 0
    skipped = 0
    skip_dirs = {"templates", "glossary", "diagrams", ".git", "scripts", "docs"}
    for html in sorted(root.rglob("*.html")):
        if any(part in skip_dirs for part in html.parts):
            continue
        if html.name == "index.html" and html.parent.name in skip_dirs:
            continue
        if html.parent == root and html.name in {"index.html", "404.html"}:
            continue
        if wrap_diagram_in_file(html):
            updated += 1
            print("wrapped:", html.relative_to(root))
        else:
            skipped += 1
    print(f"Done. Updated {updated} files, skipped {skipped}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())