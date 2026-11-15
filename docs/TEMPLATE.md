# Article template

This site is plain static HTML. Pattern articles (everything under category folders except `decision-guides/` and `templates/`) share one layout so readers can scan any topic the same way.

## Page shell

Every article page includes:

| Region | Purpose |
|--------|---------|
| `<head>` | UTF-8, viewport, title `Topic — SA References`, meta description, `../assets/css/main.css`, inline theme bootstrap from `localStorage` / `prefers-color-scheme` |
| `.topnav` | Logo, search, theme toggle |
| `.sidebar` | Global library navigation; mark current section with `sidebar__link active` |
| `.breadcrumb` | Home → category index → current article |
| `.article-layout` | Two columns: `.article-body` + `.article-aside` (TOC) |
| `.article-nav` | Previous / next within the category |
| `footer` | Shared site footer |
| `../assets/js/main.js` | Theme, search, TOC highlight, reading progress |

Root-relative asset paths use `../` from category folders and `./` only on `index.html`.

## Article header

Inside `.article-body`:

```html
<div class="article-header">
  <div class="article-header__tags">
    <span class="badge badge--primary">Category Name</span>
    <span class="badge badge--muted">Optional label</span>
  </div>
  <h1 class="article-header__title">Pattern title</h1>
  <p class="article-header__desc">One-sentence summary: what it is and why it matters.</p>
  <div class="article-header__meta"><span>⏱ N min read</span></div>
</div>
```

## Body sections (standard pattern article)

All `h2` elements live in `.article-content` and use stable `id` attributes for the TOC:

| Order | `id` | Heading text |
|-------|------|----------------|
| 1 | `what-it-is` | What it is |
| 2 | `why-it-exists` | Why it exists |
| 3 | `when-to-use` | When to use |
| 4 | `when-not-to-use` | When not to use |
| 5 | `typical-architecture` | Typical architecture |
| 6 | `pros-and-cons` | Pros and cons |
| 7 | `implementation-notes` | Implementation notes |
| 8 | `common-failure-modes` | Common failure modes |
| 9 | `decision-checklist` | Decision checklist |
| 10 | `example-use-cases` | Example use cases |
| 11 | `related-patterns` | Related patterns |
| 12 | `further-reading` | Further reading |

**Writing order (lead with the decision):** In *What it is*, state the pattern in plain language first, then one concrete example. *When to use* / *When not to use* are bullet lists. *Implementation notes* are practical, not marketing copy.

### Typical architecture (diagram)

1. Optional short `<p>` explaining the diagram.
2. **Rendered Mermaid** plus a text fallback for accessibility and offline `file://` use:

```html
<figure class="architecture-diagram" role="group" aria-labelledby="typical-architecture-caption">
  <div class="architecture-diagram__render mermaid">flowchart TB
    …</div>
  <details class="architecture-diagram__fallback">
    <summary>View text diagram</summary>
    <pre class="architecture-diagram__canvas"><code>…original ASCII…</code></pre>
  </details>
  <figcaption id="typical-architecture-caption" class="architecture-diagram__caption">
    One sentence specific to this article’s diagram.
  </figcaption>
</figure>
```

Mermaid is vendored at `assets/vendor/mermaid.min.js` and initialized from `assets/js/main.js` (light/dark themes). Validate syntax with `cd scripts && npm install && node verify_mermaid.mjs` before merging.

### Pros and cons

```html
<div class="pros-cons">
  <div class="pros-cons__col pros-cons__col--pros"><h3>Pros</h3><ul>…</ul></div>
  <div class="pros-cons__col pros-cons__col--cons"><h3>Cons</h3><ul>…</ul></div>
</div>
```

### Decision checklist

```html
<ul class="checklist">…</ul>
```

### Further reading

Use a `<ul>` of external links with `target="_blank"` and `rel="noopener noreferrer"`. Prefer primary sources: Martin Fowler, microservices.io, Azure Architecture Center, AWS Well-Architected / Architecture Center, Google Cloud Architecture Framework, and original papers where relevant.

## Table of contents

Mirror every `h2` in `.article-aside`:

```html
<nav class="toc" aria-label="Table of contents">
  <div class="toc__title">On this page</div>
  <ul class="toc__list">
    <li><a href="#what-it-is" class="toc__link">What it is</a></li>
    …
  </ul>
</nav>
```

`main.js` adds scroll-spy highlighting; missing `id` values break deep links.

## Decision guides

Same shell, but section titles may differ (for example *The decision*, *Comparison*). Keep `id="typical-architecture"` on the comparison/diagram section when present so diagram CSS applies.

## Anti-patterns

Use the same section `id`s where possible. *When to use* maps to *When you see it* in prose; still expose `when-to-use` / `when-not-to-use` for TOC consistency.

## Templates (`templates/`)

Downloadable documents (ADR, RFC, etc.). They reuse the site chrome but are not required to include all twelve pattern sections.

## Checklist before publishing a new article

- [ ] All twelve section `id`s present (or documented exception in PR)
- [ ] Meta description matches the opening paragraph
- [ ] Diagram wrapped in `figure.architecture-diagram`
- [ ] TOC links match `h2` ids
- [ ] Further reading links verified (HTTP 200)
- [ ] Previous/next nav matches category `index.html` order