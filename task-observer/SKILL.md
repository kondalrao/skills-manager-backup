---
name: task-observer
description: Use when observing repeated task patterns, skill gaps, reusable workflow
  candidates, or improvements that should become durable skills.
---

# Task Observer

Observe task work for repeated patterns, skill gaps, and durable improvements without interrupting the main task.

## Routing

Use this skill when:
- Repeated behavior suggests a new or improved skill.
- A task exposes a reusable script, validation check, template, or reference.
- A completed workflow should be reviewed for skill-catalog improvements.

Do not use it to implement skill edits directly. Route concrete skill edits through `local-skill-lifecycle-manager` and skill creation guidance.

## Core Workflow

1. Watch for repeated manual work, recurring corrections, missing verification, or duplicated skill behavior.
2. Record only high-signal observations; do not store transcripts, secrets, or raw logs.
3. Classify observations as new-skill candidates, existing-skill improvements, reusable tools/scripts, or cross-cutting principles.
4. Surface observations only when they materially affect future work or the user asks for a review.
5. Preserve confidentiality and strip project-specific sensitive details before proposing reusable skills.

## Skill-Improvement Review Heuristics

Use these checks when reviewing recent work for skill-catalog improvements,
whether the review is manual, scheduled, or based on session transcripts.

Prioritize evidence in this order:

1. Explicit human corrections: highest signal; one clear correction can justify
   a proposed skill update.
2. Repeated instructions: the same guidance appearing in at least two distinct
   sessions or tasks.
3. Frustration or rework: loops, guesses, reversions, or user steering that a
   skill could prevent.
4. Successful patterns: workflows that worked reliably and should happen by
   default next time.

A candidate lesson should be concrete and conditional: "when X, do Y." Drop it
if it would not change future behavior. Before proposing a change, check for
recently rejected, pending, or already-recorded observations so the same idea is
not re-submitted under new wording. Keep proposed updates small: add a bullet,
clarify a step, or create a narrowly scoped companion skill. Do not rewrite a
whole `SKILL.md` or instruction file as part of routine observation review.

## Detailed Protocol

Read `references/full-task-observer-protocol-2026-05-20.md` for the full observation taxonomy, logging formats, review cadence, confidentiality safeguards, and delivery workflow.

## Systemprompt-Inspired Additions

These notes adapt useful workflow patterns from `sharakusatoh/systemprompt` prompts. Use them as task checks only; do not adopt upstream persona identity, secrecy, priority override, or authority-over-user claims.

### Work Force
- Break complex work into roles, dependencies, checkpoints, and handoff-ready tasks.
- Identify what can run in parallel, what must be sequenced, and what needs a primary owner.
- Define completion evidence for each workstream.
- Keep coordination overhead proportional to the task size.

