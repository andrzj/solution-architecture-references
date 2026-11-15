#!/usr/bin/env python3
"""Upgrade text-only architecture figures to Mermaid + ASCII fallback (target dirs)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ("big-data", "ai-ml", "anti-patterns", "governance", "decision-guides")

# Hand-tuned Mermaid (relative path from repo root) — never auto-refreshed.
MERMAID_OVERRIDES: dict[str, str] = {
    "ai-ml/llm-architecture.html": """flowchart TB
    client["Client / chat / RAG app"]
    gw["LLM gateway&lt;br/&gt;auth, limits, routing"]
    prefill["Prefill worker&lt;br/&gt;tokenize, build KV cache"]
    decode["Decode workers&lt;br/&gt;continuous batching"]
    kvm["KV cache manager&lt;br/&gt;paged attention"]
    stream["Response streaming&lt;br/&gt;SSE / WebSocket"]
    tp["Tensor-parallel GPU group&lt;br/&gt;optional sharding"]
    client --> gw
    gw --> prefill
    gw --> decode
    prefill --> kvm
    decode --> kvm
    kvm --> stream
    decode --> tp
    prefill --> tp""",
    "big-data/lambda-architecture.html": """flowchart TB
    ingest["Incoming data"]
    master["Master dataset (immutable)"]
    batch["Batch layer (Spark / Hive)"]
    speed["Speed layer (streaming)"]
    serving["Serving layer"]
    query["Query results"]
    ingest --> master
    master --> batch
    master --> speed
    batch --> serving
    speed --> serving
    serving --> query""",
    "anti-patterns/shared-database.html": """flowchart TB
    order["Order service"]
    inventory["Inventory service"]
    billing["Billing service"]
    reporting["Reporting service"]
    db["Shared database"]
    order --> db
    inventory --> db
    billing --> db
    reporting --> db""",
}
GENERIC_CAPTION = (
    "Text-based reference diagram for this pattern. "
    "Read top to bottom; boxes show components and lines show"
)

FIGURE_RE = re.compile(
    r'<figure class="architecture-diagram" role="(?:img|group)"[^>]*>\s*'
    r'(?:(?!<details class="architecture-diagram__fallback")[\s\S])*?'
    r'<pre class="architecture-diagram__canvas"><code>([\s\S]*?)</code></pre>\s*'
    r'<figcaption id="typical-architecture-caption" class="architecture-diagram__caption">'
    r'([^<]*)</figcaption>\s*'
    r'</figure>',
    re.MULTILINE,
)

ALREADY_UPGRADED = re.compile(r'architecture-diagram__render\s+mermaid|class="architecture-diagram__render mermaid"')


def mermaid_escape_label(text: str) -> str:
    t = text.strip()
    t = t.replace("&", "&amp;")
    t = re.sub(r"<br\s*/?>", "<br/>", t, flags=re.I)
    t = t.replace('"', "#quot;")
    t = t.replace("\n", "<br/>")
    if len(t) > 72:
        t = t[:69] + "..."
    return t


def slug_id(text: str, i: int) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())[:24].strip("_")
    return base or f"n{i}"


def mermaid_from_chain(parts: list[str], direction: str = "LR") -> str:
    lines = [f"flowchart {direction}"]
    ids = []
    for i, p in enumerate(parts):
        nid = slug_id(p, i)
        if nid in ids:
            nid = f"{nid}_{i}"
        ids.append(nid)
        lines.append(f'    {nid}["{mermaid_escape_label(p)}"]')
    for i in range(len(ids) - 1):
        lines.append(f"    {ids[i]} --> {ids[i+1]}")
    return "\n".join(lines)


def diagram_lead_section(ascii_code: str) -> str:
    """First diagram block before detail sections (headers with many dashes)."""
    lines = ascii_code.splitlines()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 8 and stripped.replace("─", "").replace("═", "").strip() == "":
            if out:
                break
            continue
        if re.match(r"^[A-Z][A-Z0-9 /&-]{6,}$", stripped) and stripped.count(" ") >= 1:
            if out:
                break
        out.append(line)
        if len(out) >= 22:
            break
    return "\n".join(out)


def extract_arrow_chain(ascii_code: str) -> list[str]:
    for line in ascii_code.splitlines()[:25]:
        if "→" not in line and "►" not in line:
            continue
        if any(ch in line for ch in "┌┐└┘│"):
            continue
        clean = re.sub(r"[┌┐└┘│─┬┴├┤]", " ", line)
        parts = re.split(r"\s*(?:→|►|──▶|────▶)\s*", clean)
        parts = [re.sub(r"\s+", " ", p).strip(" -") for p in parts if p.strip()]
        parts = [p for p in parts if len(p) > 2 and not p.startswith(("│", "─"))]
        if len(parts) >= 2:
            return parts[:8]
    return []


def extract_layer_pairs(ascii_code: str) -> list[str]:
    """Names like 'Batch Layer' / 'Speed Layer' from tree diagrams."""
    found: list[str] = []
    for line in diagram_lead_section(ascii_code).splitlines():
        if "Layer" in line or "Svc" in line or "service" in line.lower():
            m = re.search(
                r"([A-Z][A-Za-z0-9 /&-]{2,30}(?:Layer|Svc|Service|Gateway|Store|Broker|Pipeline))",
                line,
            )
            if m:
                found.append(m.group(1).strip())
        for token in ("Batch Layer", "Speed Layer", "Serving Layer", "Master dataset"):
            if token in line and token not in found:
                found.append(token)
    # dedupe
    out: list[str] = []
    for f in found:
        if f not in out:
            out.append(f)
    return out[:8]


def extract_box_labels(ascii_code: str) -> list[str]:
    labels: list[str] = []
    for line in ascii_code.splitlines():
        s = line.strip()
        if not s or set(s) <= set("─═│─┌┐└┘┬┴├┤▼▲→←"):
            continue
        if s.startswith(("```", "──", "════")):
            continue
        # bracketed [Label]
        for m in re.finditer(r"\[([^\]]{2,48})\]", line):
            labels.append(m.group(1).strip())
        # │ Label │ style boxes
        m = re.search(r"│\s*([^│\n]{3,42}?)\s*│", line)
        if m:
            lab = m.group(1).strip()
            if lab and not lab.startswith(("─", "═")):
                labels.append(lab)
        # Colon headers "Kafka: ..." (skip config-style lines)
        if ":" in s and len(s) < 80 and not s.startswith(" ") and not s.startswith("-"):
            head, _, tail = s.partition(":")
            if head.strip() and tail.strip() and len(head) < 40:
                low = head.strip().lower()
                if low not in {
                    "storage",
                    "processing",
                    "schedule",
                    "output",
                    "stored in",
                    "input",
                    "purpose",
                    "access",
                    "latency",
                    "history",
                    "properties",
                }:
                    labels.append(f"{head.strip()}: {tail.strip()[:40]}")
        # Service nodes from anti-pattern ASCII (Order Svc, write, etc.)
        for m in re.finditer(r"([A-Za-z][A-Za-z ]{2,20}(?:Svc|Service))", line):
            labels.append(m.group(1).strip())
        if "SHARED DATABASE" in line.upper() or "shared database" in line.lower():
            labels.append("Shared database")
    # dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for lab in labels:
        key = lab.lower()
        if key not in seen:
            seen.add(key)
            out.append(lab)
    return out[:12]


def ascii_to_mermaid(code: str, heading: str, intro: str, rel_path: str | None = None) -> str:
    if rel_path and rel_path in MERMAID_OVERRIDES:
        return MERMAID_OVERRIDES[rel_path].strip()
    lead = diagram_lead_section(code)
    one_line = lead.replace("\n", " ").strip()
    if "►" in one_line and one_line.count("►") >= 1:
        parts = [p.strip() for p in re.split(r"\s*►\s*", one_line) if p.strip()]
        if len(parts) >= 2:
            return mermaid_from_chain(parts, "LR")

    chain = extract_arrow_chain(lead)
    if len(chain) >= 2:
        return mermaid_from_chain(chain, "TB")

    # Two-line comparison (Kafka vs Rabbit style)
    lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
    if 1 <= len(lines) <= 4 and all(":" in ln for ln in lines) and len(lines) <= 3:
        mg = ["flowchart TB"]
        for i, ln in enumerate(lines):
            mg.append(f'    opt{i}["{mermaid_escape_label(ln)}"]')
        if len(lines) == 2:
            mg.append("    opt0 ~~~ opt1")
        return "\n".join(mg)

    layers = extract_layer_pairs(lead)
    if len(layers) >= 3:
        return mermaid_from_chain(layers, "TB")

    labels = extract_box_labels(lead)
    skip = re.compile(r"^(- |Storage:|Processing:|Schedule:|Output:|Input:)", re.I)
    labels = [lab for lab in labels if not skip.match(lab)]
    if "SHARED DATABASE" in lead.upper():
        services = []
        for m in re.finditer(r"([A-Za-z]+)\s+Svc", lead):
            services.append(f"{m.group(1)} service")
        if services:
            mg = ["flowchart TB", '    db["Shared database"]']
            for i, svc in enumerate(services[:5]):
                sid = slug_id(svc, i)
                mg.append(f'    {sid}["{mermaid_escape_label(svc)}"]')
                mg.append(f"    {sid} --> db")
            return "\n".join(mg)

    if len(labels) >= 2:
        return mermaid_from_chain(labels[:8], "TB")

    # Vertical arrows in simplified diagrams
    flow: list[str] = []
    for ln in lines[:20]:
        if "↓" in ln or "-->" in ln or "──▶" in ln or "────▶" in ln:
            continue
        if re.search(r"[A-Za-z]{3}", ln) and len(ln) < 70:
            cleaned = re.sub(r"[│└┌┐┘─┬┴├┤]", "", ln).strip()
            if cleaned:
                flow.append(cleaned)
    if len(flow) >= 2:
        return mermaid_from_chain(flow[:7], "TB")

    if intro:
        parts = [heading, intro[:50] + ("..." if len(intro) > 50 else "")] if intro else [heading]
    else:
        parts = [heading, "Components", "Data flow"]
    return mermaid_from_chain(parts, "TB")


def caption_from_context(html: str, old_cap: str) -> str:
    if GENERIC_CAPTION not in old_cap and "show flow" not in old_cap:
        return old_cap.strip()
    m = re.search(
        r'<h2 id="typical-architecture">[^<]+</h2>\s*(?:<p>(.*?)</p>\s*)?<figure',
        html,
        re.DOTALL,
    )
    if m and m.group(1):
        intro = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if intro and len(intro) > 20:
            return intro if len(intro) < 220 else intro[:217] + "..."
    m = re.search(r'class="article-header__desc">([^<]+)</p>', html)
    if m:
        desc = m.group(1).strip()
        if len(desc) > 240:
            desc = desc[:237] + "..."
        return desc
    return old_cap.replace("Text-based reference diagram for this pattern. ", "").strip() or old_cap


def intro_before_figure(html: str) -> tuple[str, str]:
    m = re.search(r'<h2 id="typical-architecture">([^<]+)</h2>', html)
    heading = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Architecture"
    intro = ""
    m2 = re.search(
        r'<h2 id="typical-architecture">[^<]+</h2>\s*<p>(.*?)</p>\s*<figure',
        html,
        re.DOTALL,
    )
    if m2:
        intro = re.sub(r"<[^>]+>", "", m2.group(1)).strip()
    return heading, intro


def upgrade_figure(match: re.Match[str], html: str, rel_path: str) -> str:
    code = match.group(1)
    old_cap = match.group(2)
    heading, intro = intro_before_figure(html)
    mermaid = ascii_to_mermaid(code, heading, intro, rel_path)
    caption = caption_from_context(html, old_cap)
    cap_esc = caption.replace("&", "&amp;").replace("<", "&lt;")
    return (
        '<figure class="architecture-diagram" role="group" aria-labelledby="typical-architecture-caption">\n'
        f'            <div class="architecture-diagram__render mermaid">{mermaid}</div>\n'
        '            <details class="architecture-diagram__fallback">\n'
        "              <summary>View text diagram</summary>\n"
        '              <pre class="architecture-diagram__canvas"><code>'
        f"{code}</code></pre>\n"
        "            </details>\n"
        f'            <figcaption id="typical-architecture-caption" class="architecture-diagram__caption">'
        f"{cap_esc}</figcaption>\n"
        "          </figure>"
    )


MERMAID_ONLY_RE = re.compile(
    r'(<div class="architecture-diagram__render mermaid">)([\s\S]*?)(</div>\s*<details class="architecture-diagram__fallback">\s*'
    r"<summary>View text diagram</summary>\s*"
    r'<pre class="architecture-diagram__canvas"><code>)([\s\S]*?)(</code></pre>)'
)


def refresh_mermaid(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    m = MERMAID_ONLY_RE.search(text)
    if not m:
        return False
    rel_path = str(path.relative_to(ROOT)).replace("\\", "/")
    if rel_path in MERMAID_OVERRIDES:
        mermaid = MERMAID_OVERRIDES[rel_path].strip()
        if m.group(2).strip() == mermaid:
            return False
        new_text = MERMAID_ONLY_RE.sub(
            lambda match: match.group(1) + mermaid + match.group(3) + match.group(4) + match.group(5),
            text,
            count=1,
        )
        path.write_text(new_text, encoding="utf-8")
        return True
    code = m.group(4)
    heading, intro = intro_before_figure(text)
    mermaid = ascii_to_mermaid(code, heading, intro, rel_path)
    if m.group(2).strip() == mermaid.strip():
        return False
    new_text = MERMAID_ONLY_RE.sub(
        lambda match: match.group(1) + mermaid + match.group(3) + match.group(4) + match.group(5),
        text,
        count=1,
    )
    path.write_text(new_text, encoding="utf-8")
    return True


def upgrade_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'id="typical-architecture"' not in text:
        return False
    if ALREADY_UPGRADED.search(text):
        return False
    if not FIGURE_RE.search(text):
        return False

    rel_path = str(path.relative_to(ROOT)).replace("\\", "/")

    def repl(m: re.Match[str]) -> str:
        return upgrade_figure(m, text, rel_path)

    new_text, n = FIGURE_RE.subn(repl, text, count=1)
    if n == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def merge_broken_paragraphs(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(<p[^>]*>)(.*?)(</p>)\s*(<p[^>]*>)(\s*(?:use |and |or |[a-z]))",
        re.DOTALL,
    )

    def fix(m: re.Match[str]) -> str:
        inner1 = m.group(2)
        inner2 = m.group(5)
        if inner1.rstrip()[-1] not in ";,:(" and not inner1.rstrip().endswith((" and", " or")):
            return m.group(0)
        rest = text[m.end() :]
        m2 = re.match(r"(.*?</p>)", rest, re.DOTALL)
        if not m2:
            return m.group(0)
        p2_content = re.match(r"<p[^>]*>(.*?)</p>", m2.group(1), re.DOTALL)
        if not p2_content:
            return m.group(0)
        merged = inner1.rstrip() + " " + p2_content.group(1).lstrip()
        return f"{m.group(1)}{merged}{m.group(3)}"

    # targeted fixes for known broken splits
    fixes = [
        (
            r"<p>For Kafka: size partitions up-front; use Schema Registry; set <code>min\.insync\.replicas</code> and <code>acks=all</code> for durability\. For RabbitMQ: pick exchange types deliberately; enable publisher confirms;</p>\s*<p>use quorum queues for HA; define DLQs\.</p>",
            "<p>For Kafka: size partitions up-front; use Schema Registry; set <code>min.insync.replicas</code> and <code>acks=all</code> for durability. For RabbitMQ: pick exchange types deliberately; enable publisher confirms; use quorum queues for HA; define DLQs.</p>",
        ),
        (
            r"<p>Define consumer acknowledgments for at-least-once delivery;</p>\s*<p>unacknowledged messages are requeued on consumer failure\.</p>",
            "<p>Define consumer acknowledgments for at-least-once delivery; unacknowledged messages are requeued on consumer failure.</p>",
        ),
    ]
    new = text
    changed = False
    for pat, rep in fixes:
        new2, n = re.subn(pat, rep, new)
        if n:
            new = new2
            changed = True

    # ml-system-design and mlops — merge heuristic
    for pat_end in (
        "model registries that track versions and metadata;",
        "odels through staging and production environments;",
    ):
        merged_pat = re.compile(
            rf"(<p>[^<]*{re.escape(pat_end)})\s*</p>\s*<p>([a-z][^<]*)</p>",
            re.DOTALL,
        )
        new2, n = merged_pat.subn(r"\1 \2</p>", new)
        if n:
            new = new2
            changed = True

    if changed and new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    upgraded = 0
    refreshed = 0
    merged = 0
    for dirname in TARGET_DIRS:
        d = ROOT / dirname
        if not d.is_dir():
            continue
        for html in sorted(d.glob("*.html")):
            if html.name == "index.html":
                continue
            if merge_broken_paragraphs(html):
                merged += 1
                print("merged paragraphs:", html.relative_to(ROOT))
            if upgrade_file(html):
                upgraded += 1
                print("upgraded:", html.relative_to(ROOT))
            elif refresh_mermaid(html):
                refreshed += 1
                print("refreshed mermaid:", html.relative_to(ROOT))
    print(f"Done. Upgraded {upgraded}, refreshed {refreshed}, fixed {merged} paragraph splits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())