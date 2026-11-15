#!/usr/bin/env python3
"""Insert Mermaid diagrams into security/, observability/, deployment/ articles."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from mermaid_sod_data import DIAGRAMS

ROOT = Path(__file__).resolve().parents[1]

FIGURE_RE = re.compile(
    r'<figure class="architecture-diagram" role="img" aria-labelledby="typical-architecture-caption">\s*'
    r'<pre class="architecture-diagram__canvas"><code>(.*?)</code></pre>\s*'
    r'<figcaption id="typical-architecture-caption" class="architecture-diagram__caption">.*?</figcaption>\s*'
    r"</figure>",
    re.DOTALL,
)


def build_figure(code: str, mermaid: str, caption: str) -> str:
    mermaid_block = mermaid.strip()
    caption_esc = caption
    return (
        '          <figure class="architecture-diagram" role="group" aria-labelledby="typical-architecture-caption">\n'
        f'            <div class="architecture-diagram__render mermaid">{mermaid_block}</div>\n'
        '            <details class="architecture-diagram__fallback">\n'
        '              <summary>View text diagram</summary>\n'
        f"              <pre class=\"architecture-diagram__canvas\"><code>{code}</code></pre>\n"
        "            </details>\n"
        f'            <figcaption id="typical-architecture-caption" class="architecture-diagram__caption">{caption_esc}</figcaption>\n'
        "          </figure>"
    )


def transform_file(path: Path, rel: str) -> bool:
    if rel not in DIAGRAMS:
        print(f"skip (no diagram): {rel}")
        return False
    text = path.read_text(encoding="utf-8")
    if "architecture-diagram__render mermaid" in text:
        return False
    m = FIGURE_RE.search(text)
    if not m:
        print(f"skip (no figure): {rel}")
        return False
    entry = DIAGRAMS[rel]
    new_fig = build_figure(m.group(1), entry["mermaid"], entry["caption"])
    new_text = text[: m.start()] + new_fig + text[m.end() :]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    updated = 0
    for rel in sorted(DIAGRAMS):
        path = ROOT / rel
        if not path.is_file():
            print(f"missing: {rel}")
            continue
        if transform_file(path, rel):
            updated += 1
            print(f"updated: {rel}")
    print(f"Done. Updated {updated} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())