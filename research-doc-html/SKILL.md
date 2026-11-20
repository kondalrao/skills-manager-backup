---
name: research-doc-html
description: Use when writing orchestrator pipeline HTML deliverables under docs/<run-slug>/ — full pages with nav, shared CSS, and rendered Mermaid diagrams.
---

# Research doc HTML

Use for **orchestrator suite stage HTML** (`debate.html`, `root-cause.html`, `knowledge-base.html`, `review.html`, `intake.html`, `index.html`, `delegations.html`).

Do **not** use `minimalist-ui` for pipeline research docs.

## Required assets (per run)

Create `docs/<run-slug>/assets/`:

- `research-doc.css` — copy from an existing run or reuse shared template
- `research-doc.js` — Mermaid init

## Page template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Title — run-slug</title>
  <link rel="stylesheet" href="assets/research-doc.css">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script defer src="assets/research-doc.js"></script>
</head>
<body data-page="debate.html">
<div class="layout">
  <nav class="doc-nav">...</nav>
  <main>
    <article>...</article>
  </main>
</div>
</body>
</html>
```

## Diagrams (mandatory rendering)

- Use `<div class="mermaid">` with Mermaid source inside — **not** `<pre class="diagram-source">`.
- Wrap in `<figure class="diagram-block"><figcaption>...</figcaption></figure>` when helpful.
- Supported: `flowchart`, `sequenceDiagram`, `graph TD`, etc.

## Navigation

Every page includes the same nav links to all artifacts in the run folder. Set `data-page` on `<body>` for active link highlighting.

## Content rules

- Semantic sections: `header.page-header`, `section#summary`, `section#details`, etc.
- Tables for comparisons and verification checklists.
- External links on claims; tag `#requires-lab` / `#unverified` per evidence hierarchy.
- Self-contained HTML (works via `python3 -m http.server` + browser); no `file://` dependency for Mermaid.

## Pandoc

Optional export: `pandoc page.html -t markdown -o page.md` — diagrams remain as Mermaid fenced blocks if needed.
