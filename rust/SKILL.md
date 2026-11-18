---
name: rust
description: Use when writing, debugging, refactoring, or reviewing Rust code, public APIs, macros, async tasks, unsafe boundaries, or Linux kernel Rust.
---

# Rust

Complete the requested Rust task against the repository's contracts. Keep the change proportional to the defect or requirement. Use the bundled rules as a reviewed baseline, with project-specific choices made explicit.

## Establish the contract

Read [Core rules](references/core.md). Inspect the applicable instructions, changed paths, build files, toolchain, edition, minimum supported Rust version (MSRV), targets, features, and relevant CI tasks. Treat missing support information as unknown. Distinguish an application, reusable library, kernel runtime, and host tool before choosing APIs or commands.

Rust language and safety contracts constrain the design. Within those limits, follow the user request and repository policy. The API Guidelines and company guides supply advice with scope; they do not establish universal language requirements. A nightly documentation URL does not authorize a toolchain change.

## Use subagents for bounded work

When subagent tools are available and permitted, delegate independent research, separate implementation paths, and focused review or verification when that split can reduce delay or add useful evidence. Keep a small local change with one agent. For unsafe abstractions, FFI contracts, or public async/trait changes, seek an independent review when available.

Read [Subagent coordination](references/subagents.md) before dispatch. One main agent owns shared contracts, integration, and the final result. If delegation is unavailable or prohibited, perform the applicable work in sequence and state any planned independent review that could not run.

## Load by task

Read every matching topic. Keep unrelated topics and source audits out of the normal load path.

| Task condition | Read |
| --- | --- |
| Change ownership, lifetimes, data types, conversions, or collection use | [Types and ownership](references/types-ownership.md) |
| Expose or change a reusable library API | [Library API](references/library-api.md), plus the relevant behavior topic |
| Return, translate, report, or recover from failure | [Errors](references/errors.md) |
| Change traits, adapters, async tasks, cancellation, or shared state | [Architecture and async](references/architecture-async.md) |
| Define, export, or change a macro | [Macros](references/macros.md) |
| Use unsafe code, raw pointers, native code, or an FFI boundary | [Unsafe and FFI](references/unsafe-ffi.md) |
| Change allocation, speed, numeric units, or time models | [Performance and numeric models](references/performance-numerics.md) |
| Change formatting, imports, comments, or documentation layout | [Style and documentation](references/style-documentation.md) |
| Work in a Linux kernel tree or on a kernel module | [Kernel profile](references/kernel-profile.md) before selecting tools; distinguish runtime code from host tools |

Use [Verification](references/verification.md) to select completion checks. For a question-only task, report the relevant contract and evidence without creating an unrelated patch or running unrelated checks.

## Apply and verify

Establish the cause or requirement in the affected path, make the smallest coherent change, and verify the observable behavior. Apply MUST rules when their conditions hold. Follow SHOULD defaults unless project evidence supports an exception; record the reason. MAY rules are options, not extra work requirements.

Select checks from the changed behavior and project profile. Cargo commands apply to Cargo projects. Kernel work uses the target tree's build, configuration, and test instructions. Do not install tools, change MSRV, add dependencies, or restructure a project merely to satisfy a generic checklist.

For unsafe code, provide the safety argument and applicable adversarial checks. For performance claims, give a workload and before/after measurements. Dynamic checks, Miri, and compilation each have limits. Keep an unrun check distinct from a passed check.

Finish with the changed behavior or finding, verification results, justified exceptions, and remaining limits. In a review, lead with actionable findings and precise locations. Do not claim that a change, build, or test ran when it did not.

## Source questions and maintenance

Read [Source review](references/source-review.md) when a claim conflicts with a tutorial or company rule. Use [source coverage](references/coverage.md), [API coverage](references/api-coverage.md), [style coverage](references/style-coverage.md), and [link records](references/link-ledger.md) for an audit of scope. The [provenance record](references/provenance.md) identifies the bundled snapshot; the [manifest](references/manifest.json) indexes its 65 rules and 12 requested sources.

For a version-sensitive implementation, check the project's selected compiler and crate documentation. Preserve rule IDs when updating a reference. Change the rule at its owning file, update its source record, and repeat the affected behavior checks. Do not load the whole source audit for a local code fix.
