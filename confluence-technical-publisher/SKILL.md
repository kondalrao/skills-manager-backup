---
name: confluence-technical-publisher
description: Use when publishing, updating, or polishing Atlassian Confluence technical documentation, especially specs, ADRs, Jira-linked project docs, Mermaid diagrams, attachment-backed SVG/PNG renders, storage-format page bodies, full-width layout, or live readback verification.
---

# Confluence Technical Publisher

Use this skill for Confluence technical documentation workflows that need repeatable publishing, Atlassian connector routing, diagram rendering, attachment upload, storage-format layout control, and verified readback.

## Default Workflow

1. Inspect the source material and current Confluence/Jira state before editing.
2. Select tools using the `Tool Selection` section.
3. Use bundled REST scripts only when `Tool Selection` indicates a REST-only gap.
4. Render Mermaid locally before publishing; do not rely on Confluence to render Mermaid source.
5. Publish diagrams as two-pane sections: Mermaid source on the left, rendered image on the right.
6. Apply the diagram embed policy defined in `Storage Patterns`.
7. Set published page width to max/full width with `content-appearance-published = full-width` when requested or when wide diagram tables are used.
8. Verify with live readback, not only update or upload success.

## Tool Selection

Use this priority order for routing:

| Priority | Tool path | Use when |
| --- | --- | --- |
| 1 | Atlassian Rovo tools | A Rovo tool and parameter set covers the operation end-to-end. |
| 2 | Bundled REST helpers/scripts | The operation needs attachment upload, storage-format body construction, page property read/write, or verification behavior that no Rovo tool parameter covers. |
| 3 | Hybrid | Use Rovo for discovery/Jira context and REST for publish/verify steps when a task spans both paths. |

Prefer the Atlassian Rovo plugin skills/tools when available:

- `atlassian-rovo:search-company-knowledge`: search Confluence, Jira, project context, or company knowledge before editing.
- `atlassian-rovo:spec-to-backlog`: convert Confluence specs into Jira epics/stories/tasks.
- `atlassian-rovo:triage-issue`: connect bug reports, logs, repro notes, or errors to Jira/Confluence context.
- `atlassian-rovo:generate-status-report`: summarize Jira issue state into a project/status report.
- `atlassian-rovo:capture-tasks-from-meeting-notes`: extract action items from notes and create Jira tasks.

For Confluence page read/create/update, use Rovo MCP tools when they preserve connector auth and support the needed body shape. Use REST helpers when Rovo MCP tools lack native support for attachment upload, storage-format body construction, or page property read/write - i.e., when no Rovo tool parameter covers the operation.

## Related Skills

- Use `markdown-mermaid-writing` when drafting Markdown or Mermaid source before publishing to Confluence.
- Use `create-specification` when the source artifact is an AI-ready specification.
- Use `architecture-decision-records` when the source artifact is an ADR or decision log.
- Do not use `obsidian-vault` as a general companion unless its configured vault path matches the current workspace; follow the active workspace instructions instead.

## Token Handling

- Never place Atlassian API tokens in commands, files, logs, continuity notes, or final answers.
- Prefer secure prompt/getpass. For automation, use `--stdin-token` or a process-scoped `ATLASSIAN_API_TOKEN`.
- If a token is detected in chat or a visible log, immediately warn the user, redact it from any further output, recommend rotation, and ask whether to continue the current task with a new token before proceeding.

## Bundled Scripts

- `scripts/render_mermaid_images.py`: render one or more `.mmd` files to validated SVG and PNG outputs using Mermaid CLI.
- `scripts/upload_confluence_attachments.py`: upload attachments to a Confluence page with runtime token prompting.
- `scripts/confluence_rest.py`: generic Confluence REST operations for page storage, attachment listing, page-width properties, and property verification.
- `scripts/confluence_storage_snippets.py`: generate storage XML snippets for TOC and two-pane diagram tables.
- `scripts/verify_confluence_page.py`: verify title, attachments, body content, page-width property, and embedded media references.
- `scripts/propose_skill_update.py`: produce a non-mutating proposal for future skill improvements based on user feedback.
- `scripts/install_mermaid_cli.sh`: user-approved Mermaid CLI setup helper.

## Storage Patterns

Read `references/confluence-storage-patterns.md` when composing storage-format bodies, inserting TOCs, choosing SVG-only versus PNG fallback diagrams, or setting page-width properties.

Default diagram policy:

- Use SVG-only embeds when the user asks for one image, vector output, or no duplicate image formats.
- Use PNG preview plus SVG attachment only when Confluence rendering reliability matters more than having one visible image.
- Keep Mermaid source visible beside the rendered image unless the user explicitly asks to hide source.

## Verification

Before reporting completion:

- Confirm REST update/upload responses are HTTP 2xx.
- Confirm expected attachment filenames exist on the page.
- Confirm the page body contains Mermaid source blocks and embedded attachment references.
- Confirm old generated sections or duplicate diagram blocks are absent when replacing them.
- Confirm `content-appearance-published` readback is `full-width` when max width was requested.
- Report connector/tooling boundaries honestly; do not claim visible embeds unless readback shows media/image nodes or the page has been visually checked.
- If readback fails (non-2xx, missing attachments, or absent body references), halt and report the specific failure before proceeding. Do not mark the task complete or attempt a silent retry without user confirmation.

## Self-Learning Protocol

When the user corrects the workflow or gives a reusable preference, treat it as a skill enhancement candidate, not an automatic edit.

1. Decide whether the feedback is global or project-specific. If project-specific, do not globalize it unless the user confirms.
2. Present a short "Skill Enhancement Candidate" with the feedback summary, affected skill files, exact behavioral change, and validation commands.
3. Wait for explicit user approval before editing any skill file, script, or `references/learning-backlog.md`.
4. After approval, update the relevant file, append the rationale to `references/learning-backlog.md`, run validation, and report the result.

Use `scripts/propose_skill_update.py` to draft the candidate when the feedback is non-trivial.
