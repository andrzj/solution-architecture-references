# Solution Architecture References Library

A curated reference library for architects and engineering teams — covering patterns, principles, trade-offs, and implementation guidance across the full architecture landscape.

## Overview

This is a static HTML site containing 200+ articles organized into 24 categories. Every article follows a consistent structure: what it is, why it exists, when to use / not use, typical architecture, pros/cons, implementation notes, failure modes, decision checklist, example use cases, related patterns, and further reading.

## Structure

| Section | Category | Articles |
|---------|----------|----------|
| 1 | [Architecture Foundations](foundations/) | 12 |
| 2 | [Architecture Styles](architecture-styles/) | 14 |
| 3 | [Distributed Systems](distributed-systems/) | 14 |
| 4 | [Communication Patterns](communication-patterns/) | 14 |
| 5 | [Reliability & Resilience](reliability/) | 14 |
| 6 | [Scalability & Performance](scalability/) | 14 |
| 7 | [API & Interface Design](api-design/) | 14 |
| 8 | [Integration Patterns](integration/) | 10 |
| 9 | [Data Architecture](data-architecture/) | 15 |
| 10 | [Search & Retrieval](search/) | 8 |
| 11 | [Security Architecture](security/) | 14 |
| 12 | [Observability & Operations](observability/) | 11 |
| 13 | [Deployment & Delivery](deployment/) | 10 |
| 14 | [Cloud Architecture](cloud/) | 12 |
| 15 | [Platform Engineering](platform-engineering/) | 7 |
| 16 | [Software Engineering Practices](software-engineering/) | 10 |
| 17 | [Mobile Architecture](mobile/) | 6 |
| 18 | [IoT & Edge](iot-edge/) | 5 |
| 19 | [Big Data & Analytics](big-data/) | 7 |
| 20 | [AI & ML Systems](ai-ml/) | 9 |
| 21 | [Governance & Enterprise Standards](governance/) | 7 |
| 22 | [Anti-Patterns](anti-patterns/) | 9 |
| — | [Decision Guides](decision-guides/) | 10 |
| — | [Templates](templates/) | 9 |
| — | [Diagram Library](diagrams/) | — |
| — | [Glossary](glossary/) | — |

## Usage

Open `index.html` in a browser, or serve the folder with any static file server:

```bash
# Python
python3 -m http.server 8080

# Node.js (npx)
npx serve .
```

Then navigate to `http://localhost:8080`.

## How to Use the Library

- **Lookup by Problem** — Use the search bar or browse by category to find patterns relevant to your current problem.
- **Compare Trade-offs** — Every article includes a pros/cons analysis and decision checklist for structured trade-off discussions.
- **Use Templates** — Grab ready-to-use ADR templates, production readiness checklists, or threat model templates from the [Templates](templates/) section.
- **Decision Guides** — For common architectural forks (e.g. REST vs GraphQL, SQL vs NoSQL), consult the [Decision Guides](decision-guides/) for structured comparisons.

## Assets

- `assets/css/` — Stylesheets (light/dark theme, responsive layout)
- `assets/js/` — Search, theme toggle, reading progress, and navigation scripts
