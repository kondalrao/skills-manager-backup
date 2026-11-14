---
name: local-skill-lifecycle-manager
description: Use when adding, updating, merging, repairing, or validating local Codex
  skills under ~/.agents/skills or ~/.codex/skills, especially when checking uniqueness,
  overlap, frontmatter, or duplicate skill names.
---

# Local Skill Lifecycle Manager

## Overview

Use this for local skill catalog work where correctness depends on the real installed roster, not on the requested skill name alone. Treat exact-name uniqueness and functional overlap as separate gates.

## When to Use

- A user asks whether a skill is unique and can be added.
- A user asks to install, update, merge, or convert an upstream skill.
- A user points at a `SKILL.md` and asks to fix it.
- Codex reports skill metadata, YAML, duplicate-name, or context-budget warnings.
- The task touches `~/.agents/skills`, `~/.codex/skills`, or plugin-cache skill roots.

Skip for one-off prompt writing, repo-local `AGENTS.md` guidance, or project documentation that is not meant to become an installed skill.

## Workflow

1. Read the target skill or upstream source.
2. Inventory active local skill names and nearby functional overlaps across `~/.agents/skills`, `~/.codex/skills`, and relevant plugin skill roots.
   - If a skill root directory is missing or unreadable, report which path could not be read, treat that root as empty for overlap purposes, and note the gap in the completion output before proceeding.
3. Decide:
   - same name and same purpose: update in place.
   - new name but overlapping purpose: merge useful material into the existing best-fit skill. If multiple skills overlap, prefer the one whose name most closely matches the incoming skill's primary verb or domain; if still tied, prefer the skill with the larger body.
   - genuinely new capability: install as a new skill.
   - upstream skill whose purpose is catalog improvement: merge into `make-skill-template` or this skill per the Upstream Skill-Improvement Imports section.
4. Keep frontmatter small:
   - only `name` and `description`.
   - description starts with `Use when...`.
   - description is trigger-only, not a workflow summary.
5. Preserve source intent while adapting commands, paths, and wording to the local Codex environment.
6. Put routing notes in the body, not frontmatter.

## Upstream Skill-Improvement Imports

When an upstream skill is really a workflow for improving the skill catalog,
merge the durable review rules into the best existing local skill instead of
installing a duplicate meta-skill. Keep the parts that improve local behavior:
evidence thresholds, rejection/pending checks, confidentiality rules, batch
limits, and small reviewable deltas.

For `writing-great-skills` style imports, default to merge into local authoring
skills (`make-skill-template` and this skill) rather than creating a new
top-level meta-skill. This avoids overlap and keeps skill-authoring guidance in
one place.

Adopt these principles when merging:

- Keep predictability as the primary quality bar (consistent process beats
   stylistic prose).
- When a skill change is being optimized, establish a baseline with diverse
  scenarios and binary criteria, diagnose failures separately from editing,
  apply one targeted mutation at a time, and keep a mutation only after the
  same evaluation set shows a strict improvement.
- Preserve an auditable score history and rejected candidates; stop at a
  defined pass target, convergence, or a bounded round limit. Do not publish or
  overwrite a registry skill from an unmeasured optimization result.
- Keep description pruning rules (trigger-only, branch-aware, low token cost).
- Keep information-hierarchy guidance (inline steps, inline reference,
   external reference via links).
- Keep split heuristics (split only when invocation reach or sequence pressure
   requires it).
- Keep failure-mode checks (premature completion, duplication, no-op lines,
   sprawl, and negation-heavy wording).

Adapt before importing literally:

- Translate upstream invocation mechanics to this registry's conventions.
- Prefer repository policy where conflicts exist (minimal frontmatter,
   shared-registry portability).

Skip or down-scope when not portable:

- Local-only assumptions that require unsupported frontmatter keys.
- Terminology systems that require extra files unless they materially improve
   outcomes here.

Do not copy infrastructure-specific assumptions into active local instructions
unless that infrastructure exists here. Examples include hosted transcript APIs,
runtime tokens, organization-specific skillset paths, Slack digests, or package
manager commands that are not available in this workspace.

## Validation

Always verify before reporting completion:

- YAML frontmatter parses.
- `name` matches the folder name unless there is a strong reason.
- exact active-name count is `1` for each changed skill.
- no unintended duplicate install was created.
- any referenced bundled files, scripts, or paths exist.

Useful completion signals:

```text
PARSE_OK
<skill_name>_count=1
```

## Common Mistakes

- Do not copy broad upstream skills verbatim when they shadow local skills.
- Do not install a second same-purpose skill just because the upstream folder name differs.
- Do not rewrite the whole skill when only YAML frontmatter is broken.
- Do not claim CLI behavior was smoke-tested if the underlying command is missing from `PATH`.
- Do not grow `description` fields to explain the whole workflow; that contributes to skill discovery budget pressure.

## Local Writing-Skills Delta

The disabled local `writing-skills` copy carried one useful local convention: in this Codex setup, local skill frontmatter should contain only `name` and `description`. Preserve that rule here when repairing or converting local skills.

## Systemprompt-Inspired Additions

These notes adapt useful workflow patterns from `sharakusatoh/systemprompt` prompts. Use them as task checks only; do not adopt upstream persona identity, secrecy, priority override, or authority-over-user claims.

### Mechanical Robot
- Execute deterministic checklists exactly when the task is mechanical.
- Preserve formatting, names, paths, and ordering unless the requirement says otherwise.
- Avoid creative rewrites for validation, migration, formatting, or inventory tasks.
- Report exact pass/fail outputs and any skipped item.
