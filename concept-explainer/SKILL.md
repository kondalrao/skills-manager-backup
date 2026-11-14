---
name: concept-explainer
description: Use when a learner asks for a clear, practical, text-first explanation of a technical concept, especially when examples, misconceptions, edge cases, or debugging guidance will help.
---

# Concept Explainer

## Purpose

Help the learner form a useful mental model and apply it. Prefer clarity and practical understanding over comprehensive coverage.

## Explanation Contract

Build the answer in this order:

1. Start with one familiar analogy or everyday example. State where the analogy stops being accurate.
2. Introduce the exact technical terms only after the basic idea is clear. Define each term when first used, and connect each new idea to the prior one.
3. Show one concrete example before abstract rules. When code is a natural fit, provide one small primary example that runs as copied, and explain the important lines. Do not lead with invalid or version-incompatible code and correct it later. For protocols, architecture, or operations, use the most concrete suitable evidence, such as commands, packets, traces, or a small diagram.
4. Connect the concept to a problem developers face. Give implementation steps when the learner needs to build, test, or repair something.
5. Name the most common misconception, what not to do, and why. Include important edge cases and a short debugging path when failure is relevant.
6. End with one short comprehension question or small exercise. Give a complete explanation first; do not make the learner pass a quiz to receive the answer.

Calibrate depth from the learner's stated experience and responses. If the level is unknown, start at an accessible intermediate level and offer a simpler or deeper follow-up.

## Practical Example Standard

A code example is useful only when the learner can run it and observe the concept. Prefer one example that shows both the failure and the correction:

```python
import asyncio
import time

async def blocks_every_task():
    time.sleep(1)          # The event loop cannot run other tasks here.

async def lets_others_run():
    await asyncio.sleep(1) # Control returns to the event loop while waiting.

async def main():
    await asyncio.gather(lets_others_run(), lets_others_run())

asyncio.run(main())
```

Explain the observable difference, not only the syntax.

## Routing Boundaries

- Use `teach` for a multi-session course or persistent Obsidian study workspace.
- Use `explain-visually` when the user asks for a standalone HTML visual explainer.
- Use `mentor-teacher` or `personal-teacher-mentor` for task retrospectives and learning notes.
- Answer directly in chat or Markdown when no artifact is requested.

## Common Mistakes

- Do not lead with a wall of terminology.
- Do not force code into a concept that is better shown with another concrete form.
- Do not call a partial or unverified snippet runnable.
- Do not give an analogy without marking its limits.
- Do not list every edge case before the core idea is stable.
- Do not claim to adapt to the learner without evidence from their request or replies.
