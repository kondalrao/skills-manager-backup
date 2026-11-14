---
name: doc-coauthoring
description: Use when a user wants to co-author a substantial proposal, design document, decision record, or other structured document through discussion and revision.
---

# Document Co-authoring

Help the user create a document that its intended readers can use. Keep the user's goal, voice, and control of the final content. Use the stages below when they fit the task. The user can skip or change any stage.

## Choose the workflow

- Use this skill for collaborative drafting of substantial documents.
- For a short edit or a direct answer, do the requested work without starting this workflow.
- For an AI-ready specification, use `create-specification` for its specification rules. This skill can guide the collaboration around it.
- For a sourced article, tutorial, or case study, use `content-research-writer` for research and publication work. This skill can guide the collaboration around it.
- For a final reader review, use `first-reader` when its reading method fits the document and the user asks for that review.
- Use the available document tool or format skill when the user needs a specific file type or shared-document operation.

When a substantial document request does not state a process, offer a short choice: use a structured co-authoring flow or work directly. If the user chooses direct drafting, follow that choice. If the user asks to co-author or already requests iteration, begin without asking again.

## Stage 1: Gather context

Find the document's purpose, audience, desired reader action, format, constraints, and source material. Reuse facts already in the conversation or available files. Do not ask the user to repeat them.

Let the user share notes in any order. Organize them as needed. Ask one focused question at a time when an unknown can change the content or structure. State a recommended default and its effect when that helps the user decide.

Read linked or supplied source material when access is available and the task calls for it. Separate verified facts, user-provided claims, assumptions, and open questions. Do not fill gaps with invented facts.

Move to drafting when the goal, audience, and key constraints are clear enough to make a useful outline. If a gap still affects the result, ask about that gap first.

## Stage 2: Shape and draft

Agree on a suitable outline. Use the user's template or format when supplied. If the structure is unclear, suggest a short outline and ask for changes.

After the user agrees to the outline, create a scaffold with the section headings and brief placeholders when the user wants a document file or artifact. For inline work, use the outline as the scaffold. Do not create an unrequested file.

Draft the section with the most important open decision first. Leave the summary until the main content is stable. For each section:

1. Ask focused questions only about unresolved content.
2. Offer options or brainstorm ideas when the user needs help exploring choices.
3. Draft from the user's selected points and the available evidence.
4. Ask for review and revise the requested parts.

Use the user's feedback to guide later sections. The user can edit the file directly, give free-form feedback, or ask for specific changes. Preserve their edits and voice. Make focused changes; do not reprint or rewrite the whole document when a smaller edit is enough.

Keep each iteration useful. After repeated small edits, check whether the section is ready or can be shorter without losing needed meaning. The user decides when the content is complete.

## Stage 3: Check the reader's view

Offer reader checks when the document will guide a decision, implementation, or action. Let the user skip this stage.

Use a fresh context for the check when the environment supports it and the user has authorized delegation. Give the reviewer only the document and realistic reader questions. Check whether the document answers those questions, defines needed terms, and avoids ambiguity, contradictions, unsupported claims, and hidden assumptions. Do not claim a fresh-context check ran if it did not.

If a separate context is not available, perform a disclosed self-review. For prose meant to be read in order, offer `first-reader` when its method fits. For reference documents, test a few realistic lookup questions instead of treating the document as a story.

Report what the reader could and could not find. Suggest targeted changes. Make changes only as the user directs or has already authorized.

## Final review

Before handoff, review the full document for:

- Clear purpose and fit for the audience.
- Consistent terms and structure.
- Flow, missing links, repetition, and contradictions.
- Facts, links, and claims that need verification.
- Sections that can be shorter without losing useful meaning.

State which checks you completed and which remain open. The user owns the final document and decides when it is ready.
