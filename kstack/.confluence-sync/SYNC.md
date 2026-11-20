# KStack skill -> Confluence replica: sync runbook

On-demand, idempotent mirror of the **kstack** skill into the Confluence folder
**"KStack Skill"**. Re-run this whenever the skill changes; only changed pages
are updated.

## What / where

- Source of truth: `~/.agents/skills/kstack` (resolves to
  `/ws/kkomarag-sjc/.agents/skills/kstack`; NOT git-tracked).
- Target folder: `KStack Skill`, `folderId = 1504677719`.
- Space: `633077987` (personal). cloudId: `cc5672c2-37d3-438b-9543-58ff06df6f4c`.
- MCP server/tools: `plugin-atlassian-atlassian` -> `createConfluencePage`,
  `updateConfluencePage` (both with `contentFormat: "markdown"`).

Config lives in `sync_plan.py` (non-secret identifiers). No API token is stored;
the sync runs inside a Cursor/agent session via the MCP.

## Conversions applied

- Markdown tables -> native Confluence tables (via `contentFormat: "markdown"`).
- Mermaid diagrams -> ASCII, from `mermaid_ascii/<key>.<idx>.txt`, wrapped in a
  plain code fence. Currently mapped (4): `references/kim-mts-map.md#0`,
  `architecture/psinb-driver-architecture.md#0,#1,#2`.
- Python files -> language-tagged code fence.
- Every page gets an "auto-generated replica" header note pointing at the source.

## Page tree (parents first)

Root `KStack Skill (replica)` (under the folder) with children mirroring the
on-disk layout: `SKILL.md`, `KNOWLEDGE.md`, `USAGE_COUNTS.md`, `knowledge/`
(+ entries/methods/switch-commands), `references/` (README landing + flow refs,
including netbroker + monthly-pr-sweep), `architecture/` (4 architecture docs),
`scripts/` (README landing + trap_code.py, group_by_packet.py). Titles are the
relpath; landings use the trailing-slash key. Full manifest: `PAGE_TREE` in
`sync_plan.py`.

## Procedure (each run)

1. Compute the plan (also writes rendered bodies to `rendered/<safe-key>.txt`):

   ```
   cd ~/.agents/skills/kstack/.confluence-sync
   python3 sync_plan.py plan
   ```

   Each node has: `key`, `title`, `parent_key`, `action`
   (`create|update|skip`), `hash`, `page_id`, `parent_page_id`,
   `rendered_path`, `unmapped`.

2. Process nodes **in listed order** (parents before children). For each node
   whose `action` != `skip`:
   - Resolve the parent page id:
     - `parent_key` is null (root only) -> parent is the folder:
       `parentId = 1504677719`.
     - else -> `python3 sync_plan.py get <parent_key>` (already created this run).
   - Read the body: the file at `rendered_path` (or
     `python3 sync_plan.py body <key>`).
   - **Batch apply (preferred):** `python3 sync_apply.py /tmp/plan.json`
     runs create/update via `push_to_confluence.py` and records state.
   - **Manual MCP path:** `create`: call `createConfluencePage` with
     `{cloudId, spaceId, title, parentId, contentFormat:"markdown", body}`.
   - `update`: `pageId = python3 sync_plan.py get <key>`; call
     `updateConfluencePage` with `{cloudId, pageId, title,
     contentFormat:"markdown", body}`.
   - Record the result so re-runs skip unchanged pages:
     `python3 sync_plan.py record <key> <pageId> <hash>`.

3. Report: any `unmapped` mermaid (add the missing ASCII file, re-run), and any
   `orphans` (keys recorded previously but no longer in the tree -- a source file
   was removed; delete/archive that Confluence page manually, then remove its
   entry from `sync_state.json`). Deletions are never automatic.

## Folder-as-parent fallback

The MCP page API does not treat a folder id as a page. Creating the ROOT page
with `parentId = 1504677719` (the folder) may be rejected. If it is:
- create the root at space root (omit `parentId`, keep `spaceId`), then move
  `KStack Skill (replica)` into the `KStack Skill` folder once via the Confluence
  UI. Children nest under the root page (page parent -> always supported), so
  this one-time move carries the whole tree.

## Table fidelity

If native tables render wrong (escaped `\|`, inline code inside cells), switch
the converter to emit HTML `<table>` for table blocks and re-run. Not needed
unless a fidelity check shows breakage.

## Baseline

First full sync is complete: 26 pages (root + 25 descendants) live under folder
`1504677719`, all page ids + content hashes recorded in `sync_state.json`
(`{"pages": {relpath: {pageId, title, hash}}}`). A fresh `sync_plan.py plan`
returns every node as `skip` with zero `orphans` and zero `unmapped` mermaid.
Re-runs only touch pages whose source changed.

## Limits

On-demand only: changes reach Confluence on the next run of this procedure, not
instantly. The MCP works solely inside a Cursor/agent session (no unattended
daemon).
