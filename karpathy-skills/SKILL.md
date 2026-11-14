---
name: karpathy-skills
description: Use when the user asks to apply Karpathy-inspired methods to coding, research, learning, decisions, or AI workflows.
---

# Karpathy Skills Orchestrator

This pack contains 14 methods curated from Andrej Karpathy's public posts and Gists. It is an unofficial curation and is not endorsed by Karpathy. Keep the user's goal, constraints, and authorization in control; the methods do not grant permission to change files, prompts, dependencies, or external systems.

## Route the request

Choose the smallest set of methods that fits the user's request. Respect a method the user names. Read only the selected child `SKILL.md` files. For a short task that needs one method, apply it in the root agent.

| Task | Methods to consider |
|---|---|
| Coding or building | [agentic engineering](skills/karpathy-agentic-engineering/SKILL.md), [minimalism](skills/karpathy-minimalism/SKILL.md), [supply-chain hygiene](skills/karpathy-supply-chain-hygiene/SKILL.md) when dependencies are involved, and [understanding first](skills/karpathy-understanding-first/SKILL.md) for review or verification |
| Prototype hardening | [vibe to agentic](skills/karpathy-vibe-to-agentic/SKILL.md), then only the needed engineering, minimalism, security, or understanding methods |
| Research and knowledge work | [autoresearch](skills/karpathy-autoresearch/SKILL.md) for repeatable experiments, [LLM wiki](skills/karpathy-llm-wiki/SKILL.md) for durable knowledge, [output evolution](skills/karpathy-output-evolution/SKILL.md) for rendered deliverables, [education first](skills/karpathy-education-first/SKILL.md) when teaching |
| Important decision or challenge | [LLM simulator](skills/karpathy-llm-simulator/SKILL.md), then [understanding first](skills/karpathy-understanding-first/SKILL.md) |
| Capture an idea before implementation | [idea files](skills/karpathy-idea-files/SKILL.md) |
| Improve an agent strategy or prompt | [system prompt learning](skills/karpathy-system-prompt-learning/SKILL.md) |
| Build an evaluation or safe practice loop | [practice environments](skills/karpathy-practice-environments/SKILL.md) |
| Monthly career or skill reflection | [meta reflection](skills/karpathy-meta-reflection/SKILL.md), with learning or practice methods only when useful |

For the curated sequences and the full source index, read [methodology index](references/methodology-index.md). Run sequential workflow steps in order. Delegate only independent work.

## Orchestrate subagents when useful

Use subagents only when a task has independent, bounded workstreams and separate context or parallel work will materially help. Keep short tasks, tightly dependent steps, user-intent clarification, and final decisions in the root. Use no more than three concurrent subagents unless the runtime has a lower limit.

For each delegated workstream:

1. Assign one method and give the subagent the exact child `SKILL.md` path to read.
2. State the objective, relevant input, constraints, permitted side effects, ownership boundary, and expected result.
3. Avoid overlapping write ownership. Keep dependent stages sequential.
4. Request findings, evidence, uncertainties, and any proposed changes in a concise handoff.
5. Review the handoff against source files or other evidence. Resolve conflicts, integrate the results, verify the outcome, and give the user one coherent response.

The root owns task decomposition, user communication, sequencing, approval boundaries, integration, verification, and the final answer. Do not treat a subagent report as proof without checking material claims. If subagents are unavailable or do not improve the task, read and apply the selected child method directly; do not claim delegation occurred.

## Curated workflows

Use these sequences when they fit the request. Skip methods that do not add value, and keep dependent stages sequential.

- Idea to launch: idea files → agentic engineering → minimalism → supply-chain hygiene → vibe to agentic.
- Research to publication: autoresearch → LLM wiki → output evolution → education first.
- Bias-resistant decision: LLM simulator → understanding first → system prompt learning.
- Monthly review: meta reflection → understanding first → practice environments → education first.

## Source and attribution

Source: [LearnPrompt/andrej-karpathy-skills at commit `9e46dec`](https://github.com/LearnPrompt/andrej-karpathy-skills/tree/9e46dec18990f53edae7cbd6ddae1981fd477255). The bundled [MIT license](LICENSE) applies to the copied source files.
