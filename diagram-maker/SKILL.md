---
name: diagram-maker
description: Use when creating an editable Excalidraw diagram; use diagram-design for editorial HTML/SVG visuals and archify for schema-validated technical diagrams.
metadata:
  openclaw:
    emoji: 🧭
  mcpmarket-version: 1.0.0
---
# Diagram Maker

Create editable `.excalidraw` diagrams as artifacts, not prose. Use this skill when the requested deliverable must remain an editable Excalidraw canvas.

For brand-matched editorial HTML/SVG/PNG, chart types, or redraws from Draw.io, Mermaid, or Excalidraw, use `diagram-design`. For deterministic JSON-backed architecture, workflow, sequence, dataflow, or lifecycle diagrams, use `archify`.

Choose one Excalidraw output mode:

- `clean-svg`: educational concepts, physical systems, processes, lifecycle, simple data flow.
- `architecture-svg`: software/cloud/infra topology, services, databases, queues, trust zones.
- `excalidraw`: editable hand-drawn whiteboard, flowchart, sequence, architecture sketch.

Routing

- User wants editable/collaborative: choose Excalidraw.
- User wants an editable whiteboard or collaborative sketch: choose Excalidraw.
- User asks for standalone browser output: route to `diagram-design` or `archify` using the rules above.
- If output format is unclear and changes the artifact, ask one short question; otherwise use Excalidraw.

Workflow

1. Extract nodes, groups, labels, and directed relationships.
2. Pick layout first: left-to-right, top-down, hub-spoke, swimlanes, layered stack, sequence.
3. Keep labels short. Prefer 5-9 main elements over dense diagrams.
4. Generate the `.excalidraw` file at the requested path, or `./diagram.excalidraw`.
5. Verify syntax by opening/parsing when feasible.

SVG/HTML rules

- Single standalone `.html` file with inline CSS and inline SVG.
- No external fonts, JS, images, gradients, glows, decorative blobs, or remote assets.
- Use semantic colors, not rainbow sequences: neutral, input, process, storage, external, risk.
- Draw connectors before nodes so arrows sit behind boxes.
- Every connector path has `fill="none"` and a marker arrow when directed.
- Leave 24px text padding inside boxes; do not let text touch borders.
- Legend only when symbols/colors are not obvious.

Excalidraw rules

- Save `.excalidraw` JSON with `type`, `version`, `source`, `elements`, and `appState`.
- Use bound text for shape labels. Do not use a nonstandard `label` property.
- Keep bound text immediately after its container in the elements array.
- Minimum labeled shape: 120x60. Minimum body text: 16px.
- Use roughness `1`, `fontFamily: 1`, and simple fills.

For exact Excalidraw element snippets, read `references/excalidraw-patterns.md`.
