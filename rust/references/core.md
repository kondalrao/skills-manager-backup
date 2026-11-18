# Core rules

Load this file for every Rust task. Use [the skill entry point](../SKILL.md) to select other files.

## R-CORE-01 — Establish the project contract

**MUST.** Read the applicable repository instructions, build configuration, manifests, lockfile policy, toolchain file, formatter configuration, and CI tasks before a change. Identify application code, reusable library code, and target-specific code. For a Linux kernel tree, load the [kernel profile](kernel-profile.md); Cargo commands are not its default build interface. Preserve unrelated work.

**Check:** State the affected packages, supported toolchain and targets, and the checks selected. Treat an absent MSRV as unknown. Do not infer it from a successful build on a newer compiler. [Cargo MSRV](https://doc.rust-lang.org/cargo/reference/rust-version.html)

## R-CORE-02 — Use the existing format and language

**SHOULD.** Use the repository formatter. For a new Cargo project, use `rustfmt` and normal Cargo layout. Use standard Rust names: `snake_case` for functions and modules, `UpperCamelCase` for types and traits, and `SCREAMING_SNAKE_CASE` for constants. Name the domain concept. Explain values whose units or purpose are unclear.

**Check:** Formatting passes. Names state the operation and ownership effect. Keep layout changes out of unrelated fixes. Read [Style and documentation](style-documentation.md) for manual checks and formatter edition selection. [Rust Style Guide](https://doc.rust-lang.org/style-guide/), [API naming](https://rust-lang.github.io/api-guidelines/naming.html), [Cargo layout](https://doc.rust-lang.org/cargo/guide/project-layout.html)

## R-CORE-03 — Keep the design proportional

**SHOULD.** Start with concrete types, functions, and modules. Add a trait, crate, builder, or macro for a present contract or measured need. Reusable libraries need a stable public boundary. Application internals can use a simpler boundary.

**Check:** Each new abstraction has a named caller or invariant. A one-implementation trait needs a real boundary, generic operation, or test requirement. See [Architecture and async](architecture-async.md). [API flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html)

## R-CORE-04 — Make public contracts visible

**MUST.** Document public behavior that a caller cannot learn from the signature. Include relevant units, invariants, ownership, error cases, panic cases, safety preconditions, and feature or target limits. For async operations, state cancellation and completion effects when they matter.

**SHOULD.** Provide a crate overview and runnable examples for important workflows. Use `///` for items and `//!` for modules. Explain design reasons where they help a caller; keep agent instructions out of API prose.

Use `?` in normal fallible examples unless the example specifically demonstrates a panic. Use intra-doc links for related items. Hide irrelevant rendered details when useful, but use Rust visibility for access control; `#[doc(hidden)]` does not make a public item private.

**Check:** Rustdoc links resolve and examples run. Documentation agrees with the code. A trivial item can link to a shared example. [API documentation](https://rust-lang.github.io/api-guidelines/documentation.html), [rustdoc tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)

## R-CORE-05 — Keep policy distinct from fact

**MUST.** Separate a language requirement, repository policy, performance observation, and design recommendation. Give measurements with workload and target. Verify an API against the project's version before use.

**Check:** No claim of universal speed, zero runtime cost, portability, or safety rests only on a tutorial. Consult the [source corrections](source-review.md) when the task touches a listed issue.

## R-CORE-06 — Report evidence and limits

**MUST.** At completion, report behavior changed, checks run, results, exceptions, and remaining risk. For a blocked check, state the missing tool, target, service, or decision. Passing compilation does not establish the business rule or the absence of undefined behavior.

**Check:** Each important claim has a test, source, measurement, or explicit limit. Use [Verification](verification.md).
