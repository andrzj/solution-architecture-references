#!/usr/bin/env python3
"""Restore further-reading hrefs from master when current URL differs (revert vaguer replacements)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HREF_RE = re.compile(
    r'<li><a href="(https?://[^"]+)"[^>]*>([^<]*)</a></li>',
    re.IGNORECASE,
)


def master_hrefs(path: Path) -> dict[str, str]:
    rel = path.relative_to(ROOT).as_posix()
    try:
        text = subprocess.check_output(
            ["git", "show", f"master:{rel}"], cwd=ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="replace")
    except subprocess.CalledProcessError:
        return {}
    out: dict[str, str] = {}
    for url, title in HREF_RE.findall(text):
        out[title.strip()] = url
    return out


def main() -> int:
    fixes = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        master = master_hrefs(path)
        if not master:
            continue
        text = path.read_text(encoding="utf-8")

        def repl(match: re.Match[str]) -> str:
            nonlocal fixes
            url, title = match.group(1), match.group(2).strip()
            old = master.get(title)
            if old and old != url and title:
                fixes += 1
                return match.group(0).replace(url, old, 1)
            return match.group(0)

        new = HREF_RE.sub(repl, text)
        if new != text:
            path.write_text(new, encoding="utf-8")
    print(f"Restored {fixes} link URLs from master by matching link titles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())