# Rust Style Guide coverage

Reviewed: 2026-11-15. The complete print book, introduction, and nine numbered chapters were read. This table records coverage; [Style and documentation](style-documentation.md) defines the selected rules. New syntax and nightly options remain conditional on the target project.

| Chapter | Subchapters reviewed | Treatment |
| --- | --- | --- |
| [Introduction](https://doc.rust-lang.org/nightly/style-guide/) | Indentation, block indent, width, commas, blank lines, whitespace, sorting, comments, doc comments, attributes, small-item rules | Use formatter defaults for new work unless the project has a policy. Review comments and semantic order by hand. |
| [1. Items](https://doc.rust-lang.org/nightly/style-guide/items.html) | Functions; tuples; enums; structs; unions; traits; impls; extern crate; modules; macro_rules; generics; where clauses; aliases; associated types; all six import subsections | Keep item layout consistent. Preserve import group boundaries and order-sensitive attributes or macro declarations. |
| [2. Statements](https://doc.rust-lang.org/nightly/style-guide/statements.html) | Let, let-else, statement macros, expression statements | Let the formatter select line breaks. Preserve statement/value semantics when handling semicolons. |
| [3. Expressions](https://doc.rust-lang.org/nightly/style-guide/expressions.html) | Blocks, closures, aggregate literals, indexing, operators, casts, control flow, calls, macros, chains, matches, combined expressions, ranges, hex literals, patterns | Use normal call/chain/block layout. Review macro syntax and semantic changes separately. |
| [4. Types and Bounds](https://doc.rust-lang.org/nightly/style-guide/types.html) | Single-line layout, line breaks, precise capturing bounds | Break complex types at their outer structure. Use the parser edition and toolchain that support the syntax. |
| [5. Other style advice](https://doc.rust-lang.org/nightly/style-guide/advice.html) | Expression-based assignment, identifier case, reserved identifiers, module paths | Use standard Rust naming and clear expressions. Keep the project's module convention. |
| [6. Cargo.toml](https://doc.rust-lang.org/nightly/style-guide/cargo.html) | Sections, key order, arrays, inline tables, strings, package metadata | Follow the existing TOML formatter and Cargo semantics. A Rust source-format pass does not check manifest formatting. |
| [7. Principles](https://doc.rust-lang.org/nightly/style-guide/principles.html) | Readability, plain-text access, aesthetics, diff quality, indentation drift, tool simplicity | Prefer readable source and small diffs over a new cosmetic rule. |
| [8. Style editions](https://doc.rust-lang.org/nightly/style-guide/editions.html) | Edition mechanism, next style, 2024 style, archived 2015/2018/2021 style | Record language and style editions separately. Treat style migration as an explicit change. |
| [9. Nightly-only syntax](https://doc.rust-lang.org/nightly/style-guide/nightly.html) | Frontmatter location, fences, spacing, feature-gate status | Load only when the selected project syntax requires it. |


Language edition, style edition, and formatter version are separate inputs. See [source review](source-review.md) for stale edition and metadata advice.
