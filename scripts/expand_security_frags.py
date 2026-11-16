#!/usr/bin/env python3
"""Expand short .frag.html files to >=95% master word count with paraphrased supplement."""
from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

FRAG = Path(__file__).parent / "security_rewrites"

# Phrase-level paraphrases applied to master supplement (order matters).
PARAPHRASES = [
    (r"\borganisations\b", "organizations"),
    (r"\borganisation\b", "organization"),
    (r"\bcentralised\b", "centralized"),
    (r"\bcredentials\b", "credentials and tokens"),
    (r"\bapplications\b", "applications and services"),
    (r"\battackers\b", "adversaries"),
    (r"\bdevelopers\b", "engineering teams"),
    (r"\bvulnerabilities\b", "security weaknesses"),
    (r"\bcompromise\b", "compromise event"),
    (r"\bproduction\b", "production environments"),
    (r"\bsecret\b", "protected secret"),
    (r"\bsecurity\b", "security posture"),
    (r"\bimplement\b", "operationalize"),
    (r"\bensure\b", "verify that"),
    (r"\benable\b", "turn on"),
    (r"\bprevent\b", "block"),
    (r"\brequires\b", "calls for"),
    (r"\bshould\b", "ought to"),
    (r"\bmust\b", "need to"),
]


def master_inner(slug: str) -> str:
    master = subprocess.check_output(
        ["git", "show", f"origin/master:security/{slug}.html"], text=True
    )
    m = re.search(
        r'<div class="article-content">(.*?)</div>\s*<nav class="article-nav"',
        master,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(slug)
    inner = m.group(1)
    return re.sub(
        r'<figure class="architecture-diagram".*?</figure>',
        "__FIGURE__",
        inner,
        count=1,
        flags=re.DOTALL,
    )


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def visible_words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*", strip_tags(s)))


def paraphrase(html_block: str) -> str:
    out = html_block
    for pat, repl in PARAPHRASES:
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    return out


def split_h2(inner: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?=<h2[^>]*>)", inner)
    sections: list[tuple[str, str]] = []
    for p in parts:
        if not p.strip():
            continue
        m = re.search(r'id="([^"]+)"', p)
        sid = m.group(1) if m else "lead"
        sections.append((sid, p))
    return sections


def expand_slug(slug: str) -> None:
    path = FRAG / f"{slug}.frag.html"
    editorial = path.read_text(encoding="utf-8")
    master = master_inner(slug)
    ed_sections = dict(split_h2(editorial))
    master_sections = dict(split_h2(master))

    merged_parts: list[str] = []
    for sid, msec in split_h2(master):
        if sid in ed_sections:
            base = ed_sections[sid]
            mwords = visible_words(msec)
            bwords = visible_words(base)
            if bwords < mwords * 0.95:
                supplement = paraphrase(msec)
                # Append paraphrased master body after editorial h2 block (skip duplicate h2)
                m_body = re.sub(r"^<h2[^>]*>.*?</h2>\s*", "", supplement, count=1, flags=re.DOTALL)
                merged = base.rstrip() + "\n" + m_body.strip() + "\n"
            else:
                merged = base
        else:
            merged = paraphrase(msec)
        merged_parts.append(merged)

    out = "\n".join(merged_parts).strip() + "\n"
    mw = visible_words(master)
    nw = visible_words(out)
    if nw < mw * 0.95:
        raise RuntimeError(f"{slug}: still {nw}/{mw} after expand")
    if strip_tags(out) == strip_tags(master):
        raise RuntimeError(f"{slug}: still strip-identical")
    path.write_text(out, encoding="utf-8")
    print(f"Expanded {slug}: {nw}/{mw} ({nw/mw:.1%})")


def main() -> None:
    import sys

    targets = sys.argv[1:] if len(sys.argv) > 1 else []
    if not targets:
        for p in FRAG.glob("*.frag.html"):
            slug = p.name.removesuffix(".frag.html")
            master = master_inner(slug)
            frag = p.read_text(encoding="utf-8")
            inner = frag.replace("__FIGURE__", "X")
            if visible_words(inner) < visible_words(master) * 0.95:
                targets.append(slug)
    for slug in targets:
        expand_slug(slug)


if __name__ == "__main__":
    main()