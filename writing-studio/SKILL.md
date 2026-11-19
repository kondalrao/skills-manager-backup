---
name: writing-studio
description: Use when a user wants to collect raw writing fragments or shape them into an article through a guided, step-by-step process.
---

# Writing Studio

Help the user move from loose ideas to a finished article. Keep exploration separate from drafting. Let the user choose when to move from one phase to the next.

Use this skill for the fragment-first method, especially for personal essays and narrative nonfiction. If the piece depends on outside sources or citations, route that research work to `content-research-writer`. Route fiction to `creative-writing`, substantial structured documents to `doc-coauthoring`, prose polish to `humanize`, and a final reader review to `first-reader` when those tasks fit better.

## Choose a mode

- **Explore:** The user wants to brainstorm, collect, or develop raw fragments, or has no source file yet.
- **Exploit:** The user provides a Markdown file of fragments and wants to shape it into an article.
- Move from Explore to Exploit when the user says the material is ready.
- Follow the user's requested mode when they name one.

File output is optional. If the user wants a file and has not named its path, ask once for the path. Reuse it for the rest of the session. If the user wants chat-only work, do not create a file.

Before every file write, re-read the target file from disk. Preserve the user's manual edits, deletions, and ordering. For in-place requests, change only the requested fragment or article block.

## Explore: collect fragments

Keep this phase open-ended. Help the user find useful material without forcing an outline or article structure.

- Ask focused questions that help the user discover details, examples, tension, or a point of view. Ask one question at a time. Do not make the user answer every question before you capture a useful fragment.
- Capture material from the user's first message, including the initial prompt.
- Fragments can be sentences, claims with a reason, scenes, code, examples, analogies, quotes, dialogue, partial thoughts, observations, complaints, or jokes.
- When an idea recurs, try to find a short phrase or metaphor that can hold the piece together. Offer it as an option, not as a decision made for the user.
- When writing to a fragments file, use one `# Working title` heading, then separate fragments with `---`. Do not add dates, metadata, a table of contents, internal headings, tags, or a required order.
- Add useful fragments as they emerge. Tell the user briefly when you add one. Do not interrupt the conversation to ask for save confirmation.
- Edit or remove a fragment at once when the user asks. Do not change nearby material.

## Exploit: shape the article

Treat the fragments file as a read-only quarry, not as an outline. You may split, combine, rewrite, or paraphrase its ideas in the article. Never edit the quarry during this phase.

Before drafting:

1. Read the whole quarry.
2. Ask what the intended reader already knows. Use the answer as the starting set of reader knowledge.
3. Ask the user to choose **Beats** or **Shape**, unless they already chose a mode.

Track reader knowledge as the article grows. A concept must be established before a later beat or block depends on it. Mark each concept as either known at the start or introduced earlier. Track the concept, not only its name. Balance needed definitions against an opening that does too much setup.

If the article needs material that is missing from the quarry, name the gap. Ask the user for an example or fact, or suggest removing the point. Do not invent facts or switch to open-ended brainstorming without the user's choice.

### Beats: build a narrative journey

Use Beats when the user wants a story-like or exploratory journey instead of a tight argument.

1. Propose 2–3 possible opening beats. Each must use only knowledge the reader has at the start. For each, say what it establishes and what later beats it makes possible.
2. Wait for the user's choice. Add only the chosen beat to the article, then stop.
3. Before the next turn of drafting, re-read the article file. If the user changed earlier beats, adapt to those changes.
4. Offer 2–3 next beats that use only knowledge already established. For each, say what it adds and what that makes possible.
5. Repeat until the article reaches a natural end.

A beat is one move in the journey. It can be a sentence, a paragraph, or a longer scene. Stop at a useful pivot point.

### Shape: build an argument

Use Shape when the user wants a thesis-driven article.

1. Draft 2–3 opening options with different claims or angles. Ask the user to choose one or combine them. The opening sets the promise that the article must keep.
2. Build one block at a time. After each block, ask what the reader needs next, given the opening.
3. Before adding a block, check its purpose, support, reader knowledge, and link to the previous block. Challenge weak transitions, repeated points, and sentences that try to do two jobs.
4. Discuss format choices when they affect the block: prose or list, inline point or callout, table or repeated structure, quote or paraphrase, and code block or inline code. Use the format that serves the reader.
5. Add only the block the user agreed to. Stop and wait for the next decision.

Use a table when the same fields repeat for at least three items. Use a callout only when an aside would disrupt the main argument. Quote when exact wording matters; otherwise paraphrase. Use a code block for multi-line or runnable code, and inline code for a short token or name.

## Finish and review

When the user says the article is complete, review it for a clear promise, logical order, grounded concepts, useful examples, unsupported claims, repetition, and a natural ending. Keep review focused on the requested scope. Do not add platform-specific formatting or metadata unless the user asks for it.
