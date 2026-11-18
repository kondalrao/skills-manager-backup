# Style and documentation layout

Load for formatting, imports, comments, documentation layout, or a style migration. This file compiles the default style principles. The [chapter map](style-coverage.md) records the full reviewed scope. Let the selected formatter implement mechanical layout.

## R-STYLE-01 — Select the formatter contract

**MUST.** Inspect the project toolchain, formatter configuration, CI command, and editor invocation. Keep the selected formatter and style unless the task includes a migration. A URL under `nightly` does not authorize nightly tools or unstable options.

**SHOULD.** For new Rust source with no override, use the default Rust style: four-space indentation, block indentation, and the formatter's normal width and comma rules. Let it choose layout for items, statements, expressions, closures, chains, types, and bounds.

**Check:** Run the project format check and review the diff. In a Cargo project, `cargo fmt --all -- --check` is a useful starting command. It does not establish successful compilation or correct behavior. [Style introduction](https://doc.rust-lang.org/nightly/style-guide/), [rustfmt](https://github.com/rust-lang/rustfmt#verifying-code-is-formatted)

## R-STYLE-02 — Separate language edition from style edition

**MUST.** Treat the parser edition and `style_edition` as separate choices. Cargo supplies package edition information to `cargo fmt`. A direct formatter invocation can use a different default. Check the installed tool's support before setting either option.

**SHOULD.** Keep a format migration separate from a language edition migration when practical. If editor and CI results differ, compare their toolchains, arguments, and inherited configuration before changing source layout.

**Check:** Record the formatter version and effective edition choices for a migration. Do not repeat the style book's stale statement that 2024 style is still awaiting release. [Style editions](https://doc.rust-lang.org/nightly/style-guide/editions.html), [current Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/rustfmt-style-edition.html)

## R-STYLE-03 — Preserve semantic order

**MUST.** Preserve order that can affect macro visibility, expansion, or attributes. Keep derive order when combining attributes. Do not reorder `#[macro_use]` modules as a cosmetic change. Do not assume a changed macro delimiter or semicolon is only a format change.

**SHOULD.** Preserve existing import-group boundaries and apply the selected formatter's sorting inside each group. Style-edition sorting can differ from plain lexical sorting. Use explicit imports under the project's policy.

**Check:** Review macro, attribute, and value-expression changes separately from whitespace. Run relevant compile checks if semantics can change. Formatter import options can be unstable; verify support rather than copy another organization's configuration. [Items and imports](https://doc.rust-lang.org/nightly/style-guide/items.html), [attributes](https://doc.rust-lang.org/nightly/style-guide/#attributes), [formatter options](https://github.com/rust-lang/rustfmt/blob/main/Configurations.md)

## R-STYLE-04 — Review content outside formatter coverage

**MUST.** Review comments, documentation examples, macro syntax, and skipped regions separately. Use `///` for item documentation and `//!` for crate or module documentation. Put documentation before attributes. Preserve string values and token meaning when removing whitespace.

**SHOULD.** Use short, useful sentences for comments. Explain the reason or invariant rather than repeat the expression. Keep a `rustfmt::skip` narrow and give a concrete layout or tool reason.

**Check:** A format pass does not prove that comments, macros, or documentation examples are correct or complete. Run documentation and behavior checks selected in [Verification](verification.md). [Style comments](https://doc.rust-lang.org/nightly/style-guide/#comments), [expressions](https://doc.rust-lang.org/nightly/style-guide/expressions.html), [formatter limits](https://github.com/rust-lang/rustfmt#limitations)

## R-STYLE-05 — Review manifests separately

**SHOULD.** Preserve the project's TOML layout for tables, keys, arrays, dependencies, and strings. Use its TOML formatter if one is selected. Keep metadata and dependency changes separate from formatting work.

**MUST.** Use current Cargo semantics for metadata. Do not add deprecated author fields or personal email data to satisfy older style advice. Apply the project's license policy and publication requirements.

**Check:** Validate a changed manifest with Cargo and the relevant build profile. `cargo fmt` does not format `Cargo.toml`. Review changed dependency strings and feature lists for meaning. [Cargo style](https://doc.rust-lang.org/nightly/style-guide/cargo.html), [Cargo manifest](https://doc.rust-lang.org/cargo/reference/manifest.html)
