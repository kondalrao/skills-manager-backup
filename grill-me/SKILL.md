---
name: grill-me
description: Use when clarifying an underspecified goal or stress-testing a plan or design before specification or implementation.
---

# Grill Me

## Purpose

What a user asks for and what they actually need are not always the same. A conventional request such as “build me a dashboard” can hide the real outcome, audience, constraint, or definition of success.

Use this skill to expose that gap before it becomes an incorrect plan, specification, or implementation. The output is a confirmed statement of intent, not a plan or code change.

## When to Use

Apply this skill when:

- The ask is missing an important part of the outcome, audience, motivation, success criteria, or binding constraint.
- The request is conventional rather than specific and unpacking the convention could change the work.
- You are about to fill in an assumption that could change the plan.
- Two reasonable values are in tension, such as simplicity versus flexibility or cost versus speed.
- The user explicitly asks to be interviewed, grilled, or challenged.
- The user asks whether a plan or design is sound and wants its assumptions stress-tested.

Do not use this skill when:

- The ask is unambiguous and self-contained.
- The user explicitly prioritizes speed over clarification and the risk is acceptable.
- The request is a pure information question or a mechanical operation.
- You already have enough information to execute without a decision-changing assumption.

## Interaction Boundary

This skill requires a live, responsive user. Do not invoke it in CI, scheduled runs, autonomous loops, or other non-interactive contexts. If an underspecified request blocks safe execution there, report the blocker instead of inventing the user's intent.

Use this skill only for intent clarification and stress-testing. Once the user confirms the intent, hand off to the narrowest downstream skill needed, such as `idea-refine`, `create-specification`, `create-implementation-plan`, or `grill-with-docs`.

When the user explicitly asks for devil's advocacy, critical challenge, or an
adversarial exercise, use the adversarial mode below instead of the ordinary
intent-confirmation sequence.

## Process

### 1. Form a hypothesis

Before asking a question, state your current best interpretation of the user's underlying goal in one sentence and give an honest confidence estimate:

```
HYPOTHESIS: You want a way to see which experiments are running and whether they show an early signal.
CONFIDENCE: ~40% — the audience, definition of “early signal,” and success condition are still unclear.
```

If confidence is below 70%, state the key missing information. Treat the number as a transparency heuristic, not as a hard mathematical gate.

### 2. Ask one question at a time

Ask one focused question, wait for the answer, then update the hypothesis before asking the next question. Include your recommended answer and its implication:

```
Q: Who needs this outcome: you, the engineering team, or an executive audience?
GUESS: You, because the request sounds like a personal tracking problem. If it is for executives, the measures and presentation will change.
```

Do not ask multiple questions in one turn. Maintain the design tree internally so dependent questions follow the answers that unlock them.

A question should resolve a decision that can change the outcome, plan, scope, risk, or acceptance criteria. Do not ask the user for facts that can be found in files, documentation, configuration, repository state, or available tools.

Attach a guess because it:

- Lets the user correct your framing quickly.
- Makes your assumptions visible.
- Gives you a falsifiable interpretation instead of a generic survey.

Remain willing to be wrong. A polite agreement with your guess may be agreement with the wording rather than the substance; probe again when the distinction matters.

### 3. Separate “want” from “should want”

Watch for answers that use convention or best-practice language without a concrete outcome:

- “It should be scalable.”
- “We should use the standard architecture.”
- “I probably need a modern solution.”
- “Good engineering practice says we should do X.”

When this distinction can change the work, ask:

> If you did not have to justify this choice to anyone, what would you actually want?

Do not challenge a clear user preference merely because it differs from a convention. Challenge it when the stated preference is a proxy for an unstated goal or constraint.

### 4. Restate the intent

When the interpretation is stable, write a concise restatement for line-by-line correction:

```
Here is what I now think you want:

- Outcome:      <what should exist or change>
- User:         <who benefits or decides>
- Why now:      <why this matters now>
- Success:      <how we know it worked>
- Constraint:   <binding limits or trade-offs>
- Out of scope: <what will not be done>

Yes / no / refine?
```

The restatement must include out-of-scope items. Silent disagreement about what is not being built is a common source of misalignment.

### 5. Confirm explicitly

The interview gate closes only when the user explicitly confirms the restatement or explicitly confirms that remaining branches are out of scope.

Treat these as ambiguous rather than as confirmation when the decision is material:

- “Whatever you think is best.”
- “Sounds good.”
- “Sure, let’s go.”
- Silence followed by a request to start.

If the user is delegating a routine, reversible choice, accept the delegation and proceed under a stated assumption. If the decision requires personal judgment or has material consequences, ask for a bounded choice.

If the user corrects the restatement, incorporate the correction and restate it again. Do not produce a plan or make changes while the interview gate remains open.

## Stop Conditions

Stop interviewing when all of the following are true:

- The underlying outcome is stated in the user's terms.
- The audience or beneficiary is known when relevant.
- Success criteria, constraints, and out-of-scope boundaries are explicit.
- Decision-changing assumptions and trade-offs have been surfaced.
- The user explicitly confirms the restatement, or confirms remaining branches are out of scope.

If several focused questions do not increase clarity, say that a foundational input is missing and identify the smallest missing decision or information needed to continue. Do not keep asking questions only to reach a numerical confidence target.

## Adversarial Mode

Use this mode only when the user wants an existing idea, plan, or decision
challenged.

1. State the proposal and the standard it must survive.
2. Present the strongest material objection first. Ask one focused question or
   objection at a time so the user can defend, revise, or concede it.
3. Test the defense against evidence, edge cases, long-term cost, reversibility,
   and affected stakeholders. Do not manufacture objections after the material
   risks are exhausted.
4. Stop when the user ends the exercise or the important objections are
   resolved. Summarize the strongest defenses, remaining vulnerabilities,
   concessions, and practical mitigations.

Challenge first, then make the result actionable. Do not withhold mitigations
or direct answers after the adversarial phase ends.

## Output and Handoff

The output of this skill is the confirmed statement of intent. Plans, specifications, task lists, and implementations are downstream outputs.

After confirmation:

- Use `idea-refine` when the user knows the outcome but needs alternatives or MVP shaping.
- Use `create-specification` when the confirmed intent needs a formal requirements contract.
- Use `create-implementation-plan` when the confirmed intent is ready for sequenced execution.
- Use `grill-with-docs` when the confirmed plan must be challenged against existing documentation, terminology, or decisions.

If the user wants the intent to persist across sessions, offer to save it as an intent document and save it only after confirmation.

## Common Failure Modes

- Starting implementation because the request sounds conventional.
- Asking for repository facts instead of inspecting them.
- Asking several dependent questions in one turn.
- Asking a question without exposing the current hypothesis.
- Accepting “scalable,” “modern,” or “best practice” as a complete goal.
- Treating delegation as confirmation for a consequential personal decision.
- Omitting the out-of-scope boundary from the restatement.
- Continuing the interview after the user has confirmed a clear, executable intent.

## Verification Checklist

- [ ] A one-sentence hypothesis and confidence estimate were stated before the first question.
- [ ] Missing information was identified when confidence was below 70%.
- [ ] Questions were asked one at a time and each included a recommended answer or guess.
- [ ] Discoverable facts were obtained from the environment rather than requested from the user.
- [ ] “Want” versus “should want” was examined when convention or best-practice language could hide the real goal.
- [ ] The restatement included outcome, user, why now, success, constraint, and out of scope.
- [ ] The user explicitly confirmed the restatement or confirmed remaining branches were out of scope.
- [ ] No plan or change was produced while the interview gate was open.
