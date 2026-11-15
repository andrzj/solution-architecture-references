#!/usr/bin/env python3
"""Apply Mermaid diagrams + captions to communication/integration/data-architecture/search articles."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).with_name("comm_data_mermaid.json")

FIGURE_RE = re.compile(
    r"<figure class=\"architecture-diagram\"[^>]*>\s*"
    r"<pre class=\"architecture-diagram__canvas\"><code>(.*?)</code></pre>\s*"
    r"<figcaption[^>]*>.*?</figcaption>\s*</figure>",
    re.DOTALL,
)

OPENER_REPLACEMENTS: dict[str, tuple[str, str]] = {
    "communication-patterns/pub-sub.html": (
        r"<p>Publish/Subscribe \(Pub/Sub\) is an asynchronous messaging model where message producers \(publishers\) send events to a named channel \(a <strong>topic</strong>\) without knowing who will consume them, and message consumers \(subscribers\) declare interest in a topic and receive all matching messages\. The broker — Kafka, Google Pub/Sub, AWS SNS, Redis Pub/Sub, or NATS — sits between producers and consumers and is responsible for routing, storing \(optionally\), and delivering messages\. This model removes the direct coupling present in request-response: the publisher does not know how many subscribers exist, does not wait for any acknowledgment, and continues publishing regardless of whether consumers are online\.</p>",
        "<p>When one business event must wake several downstream services — notify the customer, update inventory, and feed analytics — pub/sub lets the order service publish once to a topic while each consumer group reads at its own pace without the producer knowing who subscribed.</p>",
    ),
    "search/hybrid-search.html": (
        r"<p>Hybrid search is a retrieval strategy that combines results from two or more retrieval methods — most commonly <strong>BM25 sparse retrieval</strong> and <strong>dense vector \(semantic\) retrieval</strong> — into a single ranked list\. Neither method alone is optimal: BM25 excels at exact keyword matches \(product codes, names, technical terms\) but fails on paraphrastic or intent-based queries\. Dense vector search handles meaning and synonymy but can miss exact terms and struggles with short queries\.</p>",
        "<p>Product search for “noise cancelling headphones under $200” needs exact token hits for SKUs and prices plus semantic matching for paraphrases — hybrid retrieval runs BM25 and vector kNN in parallel, then fuses ranks so neither signal dominates.</p>",
    ),
    "search/faceted-search.html": (
        r"<p>Faceted search is a navigation paradigm that combines free-text search with a set of facets — pre-computed categorical fields \(brand, category, price range, rating bucket\) — that users can apply as filters\. Each facet returns a count of matching documents for each value \(e\.g\., “Dell \(142\)”, “HP \(89\)”\), enabling discovery-oriented browsing alongside keyword search\.</p>",
        "<p>E-commerce laptop search combines a keyword query with filter chips for brand, price band, and rating — faceted search returns matching products plus per-facet counts so shoppers narrow results without memorising syntax.</p>",
    ),
    "search/full-text-search.html": (
        r"<p>Full-text search is a technique for querying large collections of natural-language documents by matching terms in their text content rather than exact key lookups\. The engine tokenises documents and queries \(stemming, stop-word removal, synonym expansion\), builds an inverted index mapping terms to document IDs, and scores matches \(classically TF-IDF; in modern engines BM25\) to return ranked results\.</p>",
        "<p>Support teams searching a million-ticket archive need ranked hits on problem descriptions, not just ticket IDs — full-text search tokenises bodies, builds an inverted index, and scores BM25 matches for relevance.</p>",
    ),
    "search/semantic-search.html": (
        r"<p>Semantic search retrieves documents based on the meaning of a query rather than its exact keywords\. Documents and queries are embedded into a high-dimensional vector space using a trained embedding model; similarity in that space \(typically cosine similarity\) indicates semantic relevance even when vocabulary differs\.</p>",
        "<p>A query like “ways to reduce cloud spend” should surface FinOps and rightsizing docs that never mention those exact words — semantic search embeds query and chunks, then ranks by vector similarity.</p>",
    ),
    "data-architecture/graph-databases.html": (
        r"<p>A graph database stores data as nodes \(entities\) and edges \(relationships between entities\), both of which carry properties\. Queries traverse the graph by following edges rather than joining tables, making multi-hop relationship patterns \(friends-of-friends, shortest paths, recommendation subgraphs\) efficient where relational joins would explode in complexity\.</p>",
        "<p>“People your friends follow who bought this product” is a two-hop graph walk — Neo4j and similar stores model users and purchases as nodes and edges so Cypher traversals beat deep SQL joins.</p>",
    ),
    "data-architecture/vector-databases.html": (
        r"<p>A vector database stores embeddings — dense numerical vectors \(typically 384–3072 dimensions\) that encode semantic meaning of text, images, or other data — and supports fast approximate nearest neighbour \(ANN\) search to find the most similar vectors to a query embedding\. It is the retrieval backbone of semantic search, RAG pipelines, recommendation systems, and duplicate detection\.</p>",
        "<p>RAG pipelines chunk documentation, embed each chunk, and at query time find the nearest vectors to the question embedding — a vector database holds those embeddings and serves sub-100ms ANN lookups.</p>",
    ),
    "integration/etl-vs-elt.html": (
        r"<p>ETL \(Extract-Transform-Load\) is a data integration pattern in which data is first extracted from source systems, transformed into the target schema in an intermediate staging area using a dedicated transformation engine \(Informatica, Talend, SSIS, Spark\), and then loaded into the destination data warehouse\. ELT \(Extract-Load-Transform\) reverses the last two steps: raw data is extracted and loaded directly into the warehouse \(typically cloud object storage or a cloud warehouse\), and transformation runs inside the warehouse using SQL or Spark against the loaded data\.</p>",
        "<p>Nightly CRM extracts can land raw JSON in cloud storage and let Snowflake SQL reshape it (ELT), or be scrubbed in Spark staging before warehouse load (ETL) — the trade-off is where compute runs and how much raw history you keep.</p>",
    ),
    "data-architecture/normalization-vs-denormalization.html": (
        r"<p>Normalization is the process of organizing a relational database schema to reduce data redundancy and dependency by decomposing tables into smaller, well-structured relations following normal forms \(1NF, 2NF, 3NF, BCNF\)\. Each fact is stored once, updates are atomic, and anomalies \(insertion, update, deletion\) are eliminated\. Denormalization deliberately reintroduces redundancy — duplicating columns or embedding related data — to optimise read performance at the cost of write complexity and storage\.</p>",
        "<p>OLTP order entry stays in 3NF so line items update once; a BI dashboard may denormalize customer name onto order rows to avoid joins at report time.</p>",
    ),
    "data-architecture/oltp-vs-olap.html": (
        r"<p>OLTP \(Online Transaction Processing\) databases are designed for high-frequency, short-duration read and write transactions — thousands of concurrent users inserting, updating, and retrieving individual rows with ACID guarantees\. OLAP \(Online Analytical Processing\) systems are optimised for complex analytical queries over large historical datasets: aggregations, rollups, and scans across millions or billions of rows with minimal locking on concurrent writes\.</p>",
        "<p>Checkout updates one order row thousands of times per second (OLTP); finance runs year-over-year revenue by region over billions of rows (OLAP) — row stores vs columnar layouts follow that split.</p>",
    ),
    "data-architecture/data-cataloging.html": (
        r"<p>A data catalog is a metadata management system that inventories an organization's data assets — databases, tables, columns, files, dashboards, ML models — and makes them discoverable and governable through search, lineage, ownership, quality scores, and access policies\. Modern catalogs \(Alation, Collibra, DataHub, OpenMetadata, AWS Glue Data Catalog\) integrate with data platforms to automatically harvest technical metadata and enrich it with business context \(glossary terms, stewards, PII classifications\)\.</p>",
        "<p>When analysts cannot find which table holds “active subscriber count,” a data catalog indexes schemas, owners, and lineage so self-service discovery replaces Slack archaeology.</p>",
    ),
    "data-architecture/data-contracts.html": (
        r"<p>A data contract is a formal specification, owned by the data producer, that defines what a dataset guarantees: schema, semantics, SLAs for freshness and completeness, quality thresholds, and versioning rules\. Consumers depend on those guarantees when building downstream pipelines, ML features, or dashboards — breaking a contract is a producer defect, not a consumer surprise\.</p>",
        "<p>Downstream ML features assume the orders stream includes currency and arrives within five minutes — a data contract documents that schema and SLA so breaking changes trigger review, not silent drift.</p>",
    ),
}


def apply_opener_edits(html: str, rel: str) -> tuple[str, int]:
    if rel not in OPENER_REPLACEMENTS:
        return html, 0
    old_pat, new_para = OPENER_REPLACEMENTS[rel]
    new, n = re.subn(old_pat, new_para, html, count=1)
    return new, n


def upgrade_figure(html: str, mermaid: str, caption: str) -> str:
    m = FIGURE_RE.search(html)
    if not m:
        raise ValueError("figure block not found")
    ascii_block = m.group(1)
    replacement = (
        '<figure class="architecture-diagram" role="group" aria-labelledby="typical-architecture-caption">\n'
        f'            <div class="architecture-diagram__render mermaid">{mermaid.strip()}</div>\n'
        '            <details class="architecture-diagram__fallback">\n'
        '              <summary>View text diagram</summary>\n'
        f'              <pre class="architecture-diagram__canvas"><code>{ascii_block}</code></pre>\n'
        "            </details>\n"
        f'            <figcaption id="typical-architecture-caption" class="architecture-diagram__caption">{caption}</figcaption>\n'
        "          </figure>"
    )
    return html[: m.start()] + replacement + html[m.end() :]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    updated = 0
    opener_edits = 0
    errors: list[str] = []

    for rel, entry in sorted(data.items()):
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing: {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if "architecture-diagram__render" in html:
            continue
        try:
            new_html = upgrade_figure(html, entry["mermaid"], entry["caption"])
            new_html, n_op = apply_opener_edits(new_html, rel)
            opener_edits += n_op
            path.write_text(new_html, encoding="utf-8")
            updated += 1
        except Exception as e:
            errors.append(f"{rel}: {e}")

    print(f"Updated diagrams: {updated}")
    print(f"Editorial opener fixes: {opener_edits}")
    if errors:
        print(f"Errors: {len(errors)}", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())