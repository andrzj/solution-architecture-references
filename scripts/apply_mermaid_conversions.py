#!/usr/bin/env python3
"""Apply Mermaid diagram wrappers and light prose edits to target articles."""
import json
import re
from pathlib import Path

from mermaid_conversions import DIAGRAMS, WHAT_IT_IS_LEADS

ROOT = Path(__file__).resolve().parent.parent

FIGURE_RE = re.compile(
    r'<figure class="architecture-diagram"[^>]*>\s*'
    r'<pre class="architecture-diagram__canvas"><code>(.*?)</code></pre>\s*'
    r'<figcaption[^>]*>.*?</figcaption>\s*'
    r'</figure>',
    re.DOTALL,
)

ALREADY_MERMAID = re.compile(
    r'<figure class="architecture-diagram" role="group"',
    re.DOTALL,
)


def build_figure(ascii_code: str, mermaid: str, caption: str) -> str:
    ascii_stripped = ascii_code.strip("\n")
    # Preserve HTML entities in fallback ASCII as stored in file
    return f"""<figure class="architecture-diagram" role="group" aria-labelledby="typical-architecture-caption">
            <div class="architecture-diagram__render mermaid">{mermaid.strip()}</div>
            <details class="architecture-diagram__fallback"><summary>View text diagram</summary><pre class="architecture-diagram__canvas"><code>{ascii_stripped}</code></pre></details>
            <figcaption id="typical-architecture-caption">{caption}</figcaption>
          </figure>"""


def fix_microservices(html: str) -> str:
    html = html.replace(
        '<figcaption id="typical-architecture-caption" class="architecture-diagram__caption">',
        '<figcaption id="typical-architecture-caption">',
    )
    html = html.replace('role="img"', 'role="group"', 1)
    return html


def apply_what_it_is(html: str, rel: str) -> str:
    if rel not in WHAT_IT_IS_LEADS:
        return html
    lead = WHAT_IT_IS_LEADS[rel]
    pattern = re.compile(
        r'(<h2 id="what-it-is">What it is</h2>\s*)(.*?)(\s*<h2 id="why-it-exists">)',
        re.DOTALL,
    )
    def repl(m):
        body = m.group(2).strip()
        if body.startswith("<p>"):
            return m.group(1) + lead + "\n          " + m.group(3)
        return m.group(1) + lead + "\n          " + body + "\n\n          " + m.group(3)
    return pattern.sub(repl, html, count=1)


def strip_templated_figcaption(html: str) -> str:
    return re.sub(
        r"Text-based reference diagram for this pattern\.[^<]*",
        "",
        html,
    )


def process_file(path: Path) -> bool:
    rel = str(path.relative_to(ROOT))
    html = path.read_text(encoding="utf-8")
    original = html

    if rel == "architecture-styles/microservices.html":
        html = fix_microservices(html)
        if html != original:
            path.write_text(html, encoding="utf-8")
            return True
        return False

    if rel not in DIAGRAMS:
        print(f"SKIP (no definition): {rel}")
        return False

    spec = DIAGRAMS[rel]
    mermaid_div = re.search(
        r'<div class="architecture-diagram__render mermaid">([\s\S]*?)</div>',
        html,
    )
    if mermaid_div:
        new_mermaid = spec["mermaid"].strip()
        old = mermaid_div.group(1).strip()
        if old == new_mermaid:
            return False
        html = (
            html[: mermaid_div.start(1)]
            + new_mermaid
            + html[mermaid_div.end(1) :]
        )
        path.write_text(html, encoding="utf-8")
        return True

    m = FIGURE_RE.search(html)
    if not m:
        print(f"SKIP (no figure): {rel}")
        return False

    ascii_code = m.group(1)
    new_fig = build_figure(ascii_code, spec["mermaid"], spec["caption"])
    html = html[: m.start()] + new_figure_indent(new_fig) + html[m.end() :]

    html = apply_what_it_is(html, rel)
    html = remove_filler_opener(html)

    path.write_text(html, encoding="utf-8")
    return True


def new_figure_indent(fig: str) -> str:
    return "          " + fig.replace("\n", "\n          ").rstrip() + "\n"


def remove_filler_opener(html: str) -> str:
    html = re.sub(
        r"<p>\s*The typical architecture below[^<]*</p>\s*",
        "",
        html,
        flags=re.IGNORECASE,
    )
    return html


def main():
    changed = []
    for rel in sorted(DIAGRAMS.keys()):
        path = ROOT / rel
        if process_file(path):
            changed.append(rel)
    # microservices
    ms = ROOT / "architecture-styles/microservices.html"
    if process_file(ms):
        changed.append("architecture-styles/microservices.html")
    print(json.dumps({"changed": len(changed), "files": changed}, indent=2))


if __name__ == "__main__":
    main()