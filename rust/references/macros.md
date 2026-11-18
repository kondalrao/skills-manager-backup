# Macros

Load for a macro definition, export, expansion, or procedural macro change.

## R-MAC-01 — Establish the need

**SHOULD.** Prefer ordinary Rust types, functions, and traits. Use `macro_rules!` when token matching and repetition meet the need. Use a procedural macro when parsing or item transformation requires it. Keep runtime logic in ordinary functions where practical.

**Check:** State what syntax or generated structure the macro provides. Compare its maintenance cost with an ordinary API. Do not create a new language for a small reduction in call-site text. [Rust macro overview](https://doc.rust-lang.org/book/ch20-05-macros.html)

## R-MAC-02 — Specify expansion behavior

**MUST.** Document accepted syntax, output context, generated items, visibility, ownership, evaluation count, and error behavior. When one evaluation is promised, bind the input once with the intended move or borrow behavior.

**Check:** Use side-effecting expressions and non-`Copy` values. Check zero, one, and several repeated inputs, trailing separators, attributes, visibility, and supported generic forms. A macro must not hide a changed function contract or an unexpected public item. [API macro guidance](https://rust-lang.github.io/api-guidelines/macros.html), [assert_eq](https://doc.rust-lang.org/std/macro.assert_eq.html)

For item macros, keep input syntax close to the generated Rust structure. Accept and forward the relevant attributes, including per-item `cfg`, and use normal visibility syntax with a private default. Test intended module and function item contexts. Type inputs need the supported primitive, borrowed, relative, absolute, parent, and generic forms.

## R-MAC-03 — Make exported paths work for consumers

**MUST.** In `macro_rules!`, use `$crate::...` for items in the defining crate. Make referenced helpers reachable with the required visibility. `$crate` does not bypass privacy. Qualify other paths so caller imports do not decide the expansion. For procedural macros, use an explicit facade or dependency path strategy, including dependency rename support where required; `$crate` is not their path mechanism.

**SHOULD.** Re-export expansion-only dependency helpers through a documented internal module when consumers must not name those dependencies. Treat that module as an implementation contract for the macro. Its public visibility does not make it a supported user API.

**Check:** Invoke from a separate crate. Rename the dependency and use colliding local names. Test supported `no_std` consumers when relevant. Declarative macros use mixed-site hygiene; procedural macros are unhygienic. Neither permits an assumption that all generated names are isolated. [Declarative hygiene](https://doc.rust-lang.org/reference/macros-by-example.html#hygiene), [procedural hygiene](https://doc.rust-lang.org/reference/procedural-macros.html#procedural-macro-hygiene)

## R-MAC-04 — Respect matching and edition rules

**MUST.** For `macro_rules!`, choose the narrow fragment that matches the intended syntax. Respect arm order, repetition shape, forwarding rules, and follow sets. Check the edition of the macro definition. Rust 2024 broadens `expr`; use `expr_2021` only when the old match behavior is required.

**SHOULD.** In declarative macros, keep internal dispatch arms clear and ensure they terminate before broad catch-all recursion. An `@` prefix is a convention; callers can still supply it. Bound complex token parsing and check expansion cost for both macro forms.

**Check:** Test ambiguous inputs and edition migrations. `format_args!` requires a format string literal; an arbitrary runtime string expression is insufficient. [Macro Reference](https://doc.rust-lang.org/reference/macros-by-example.html), [2024 fragments](https://doc.rust-lang.org/edition-guide/rust-2024/macro-fragment-specifiers.html), [format_args](https://doc.rust-lang.org/std/macro.format_args.html)

## R-MAC-05 — Verify diagnostics and crate compatibility

**MUST.** Check valid expansion behavior and useful failure diagnostics. Test from a downstream crate. A snapshot of tokens alone cannot establish that the result compiles or behaves correctly.

**SHOULD.** Use `trybuild` or the existing UI test system when diagnostic stability matters. For complex procedural macros, keep parsing and transformation testable outside the compiler entry point. Use a separate implementation crate when its benefit justifies another package. Keep tightly coupled generated code and helper versions compatible; exact pinning is a project decision for lockstep internals.

**Check:** Cover compile-pass, meaningful compile-fail, runtime, and documentation cases as applicable. Review emitted code for hidden dependencies and target assumptions. [trybuild](https://docs.rs/trybuild/latest/trybuild/), [procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html)

## Case-study limit

Tokio `join!` provides concurrency within the current task, not parallel execution. A blocking branch can stop other branches from making progress. It waits for all branches; an early `Err` does not give it `try_join!` behavior. Check the selected Tokio release before using historical expansion details. [Tokio join](https://docs.rs/tokio/latest/tokio/macro.join.html)
