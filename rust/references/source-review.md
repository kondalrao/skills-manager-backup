# Source review and decisions

Reviewed: 2026-11-15. The rules in this set are an original synthesis. They do not reproduce any guide in full.

## What the twelve sources establish

| Source | Review and useful scope | Limit |
| --- | --- | --- |
| [Microsoft aggregate](https://microsoft.github.io/rust-guidelines/agents/all.txt) | All 90 rule sections reviewed. Site version 2026.6. Broad library, application, documentation, FFI, macro, and performance advice. | An organizational guide with selectable policy. [About and applicability](https://microsoft.github.io/rust-guidelines/) |
| [Rust in Space](https://www.howtocodeit.com/guides/rust-in-space) | Version 1.0.7. Introduction and 24 speaker-note sections reviewed. Useful time-scale types, validated numbers, marker types, and data providers. | A mission-simulator modeling case. No flight software assurance. Current Lox representation differs. |
| [Production macro_rules](https://www.howtocodeit.com/guides/writing-production-rust-macros-with-macro-rules) | Version 1.0.7. Reviewed standard assertion, axum tuple, Tokio join, internal dispatch, counting, and exercise sections. | Historical expansions illustrate techniques; they do not define current crate contracts. |
| [Error handling](https://www.howtocodeit.com/guides/the-definitive-guide-to-rust-error-handling) | Version 1.1.2. Parts I–III reviewed: error traits, reports, typed recovery, conversions, composition, and I/O errors. | Part IV is a placeholder. It does not supply the promised panic, FFI, or no_std guidance. |
| [Hexagonal architecture](https://www.howtocodeit.com/guides/master-hexagonal-architecture-in-rust) | Version 1.1.7. Parts I–IV reviewed: ports, adapters, async contracts, composition, tests, and costs. | Part V is a placeholder, including deferred retry advice. Its layout and framework choices are examples. |
| [Ownership and linked lists](https://www.howtocodeit.com/guides/rust-ownership-explained-merging-linked-lists) | Version 1.1.2. All code variants reviewed through the iterative solution and linked correction discussion. | An ownership exercise. It does not establish that linked lists are the right storage choice. |
| [Newtypes](https://www.howtocodeit.com/guides/ultimate-guide-rust-newtypes) | Version 1.0.15. Reviewed construction, privacy, mutation, traits, conversions, derive tools, and exercises. | Several safety, domain, and current crate claims need correction below. |
| [Google Rust guide](https://google.github.io/styleguide/rustguide.html) | All sections reviewed. Useful API, ownership, naming, documentation, and review practices. | Google policy. Chromium and Fuchsia rules have local scope. Apply library rules and application rules in context. |
| [Nightly Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/) | Complete print book, introduction, and all nine numbered chapters reviewed. | Default formatting guidance. Check the project formatter and style edition. Some edition and metadata prose is stale. |
| [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) | All 11 topic chapters, 54 checklist IDs, and relevant linked references reviewed. | Library design advice. The landing page explicitly rejects a mandate. Current API and Cargo contracts resolve old examples. |
| [Beginner rules of thumb](https://joshua-laughner.io/posts/rust-beginning-rules-of-thumb/) | Three defaults, their exceptions, and the graph-ID example reviewed. | Teaching heuristics. Ownership and duplication still depend on the type's real contract. |
| [Linux kernel coding guidelines](https://docs.kernel.org/rust/coding-guidelines.html) | Full page and relevant kernel build, API, and test documentation reviewed. | Kernel-tree policy. Use the target revision and configuration. Keep it separate from Cargo application defaults. |

## Technical corrections

Entries cover source statements and risks when applying their examples. They are not verbatim quotations. The source name identifies the guide to inspect.

| Source claim or risk | Treatment in this set | Owning evidence |
| --- | --- | --- |
| **Microsoft**: Every library error should be a backtrace-bearing struct. | Select enum or struct from recovery and evolution needs. Keep cause chains available. | [Error](https://doc.rust-lang.org/std/error/trait.Error.html) |
| **Error handling**: A result error must implement `Error`. | `Result<T, E>` has no such type bound. Our reusable-error policy adds it for interoperability. | [Result](https://doc.rust-lang.org/std/result/enum.Result.html) |
| **Error handling**: An error report always has a useful backtrace. | Capture and display depend on configuration and support. | [Anyhow details](https://docs.rs/anyhow/latest/anyhow/#details) |
| **Error handling**: `'static` means a value lives until program exit. | A type bound constrains borrowed data. An owned value can be dropped earlier. | [Static lifetime and bounds](https://doc.rust-lang.org/rust-by-example/scope/lifetime/static_lifetime.html) |
| **Hexagonal architecture**: Poisoning prevents all future access to a standard mutex. | Poisoning is advisory. Access is possible; repair or validity still needs evidence. | [Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning) |
| **Hexagonal architecture**: Shared references are transferable because they are immutable. | `&T` is `Send` if and only if `T: Sync`. | [Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html) |
| **Hexagonal architecture**: A future is `Send` because its output is `Send`. | Inspect the future's captured state separately. | [Tokio spawn](https://docs.rs/tokio/latest/tokio/task/fn.spawn.html) |
| **Microsoft**: A resolver field is unnecessary when using a new edition. | A virtual workspace needs an explicit resolver. | [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html#virtual-workspace) |
| **Microsoft**: A test feature safely isolates a certificate-check bypass. | Features unify. Use an isolated test design; inspect the release feature graph. | [Feature unification](https://doc.rust-lang.org/cargo/reference/features.html#feature-unification) |
| **Microsoft**: Vec grows by a fixed factor and shrinking guarantees exact capacity. | Neither is guaranteed. Measure retained memory and later growth. | [Vec guarantees](https://doc.rust-lang.org/std/vec/struct.Vec.html#guarantees) |
| **Microsoft**: Fixed-length boxed storage is immutable. | Fixed length and mutation are separate properties. | [Box](https://doc.rust-lang.org/std/boxed/struct.Box.html) |
| **Microsoft**: A logging format message necessarily allocates. | `format_args!` avoids heap allocation; inspect the macro and subscriber. | [format_args](https://doc.rust-lang.org/std/macro.format_args.html), [tracing event](https://docs.rs/tracing/latest/tracing/macro.event.html) |
| **Google**: `format!` or `write!` necessarily uses fewer allocations than string `+`. | Keep the readability advice, but measure allocations. `String + &str` reuses the left buffer and grows it only as needed. | [String addition](https://doc.rust-lang.org/std/string/struct.String.html#impl-Add%3C%26str%3E-for-String) |
| **Microsoft**: Every `.await` gives other tasks a turn. | A ready future can continue immediately. Use a runtime-aware scheduling plan. | [Tokio task](https://docs.rs/tokio/latest/tokio/task/) |
| **Microsoft**: Miri passing proves soundness. | It checks executed paths. A soundness argument remains required. | [Miri](https://github.com/rust-lang/miri) |
| **Microsoft**: The linked Unsafe Code Guidelines reference is the current complete base. | Its own page describes it as largely abandoned. Use current owning contracts. | [UCG status](https://rust-lang.github.io/unsafe-code-guidelines/) |
| **Newtypes**: A business-only invariant needs an unsafe constructor. | Use a checked or restricted safe API unless memory safety depends on caller duties. | [Safe and unsafe meaning](https://doc.rust-lang.org/nomicon/safe-unsafe-meaning.html) |
| **Newtypes**: `Borrow` is unofficially unsafe. | It is a safe trait with equivalence requirements. Broken laws are logic errors. | [Borrow](https://doc.rust-lang.org/std/borrow/trait.Borrow.html) |
| **Newtypes**: Whole email addresses are case insensitive. | Do not adopt whole-address lowercasing as a generic validation rule. SMTP preserves local-part case. | [RFC 5321 section 2.4](https://www.rfc-editor.org/rfc/rfc5321#section-2.4) |
| **Newtypes**: `nutype` cannot expose a custom validation error. | Current documentation supports one. Check the selected version. | [nutype custom error](https://docs.rs/nutype/latest/nutype/#custom-validation-with-a-custom-error-type) |
| **Production macro_rules**: An `@` macro arm is private. | It is an internal convention that callers can still invoke. | [Macro syntax and hygiene](https://doc.rust-lang.org/reference/macros-by-example.html) |
| **Production macro_rules**: `format_args!` accepts any expression that returns a format string. | It requires a literal format string, including supported macro-produced literals. | [format_args](https://doc.rust-lang.org/std/macro.format_args.html) |
| **Rust in Space**: All f64 values in `[0, 1)` are subnormal. | False. For example, `0.5` is normal. | [f64 classification](https://doc.rust-lang.org/std/primitive.f64.html#method.is_subnormal) |
| **Rust in Space**: Fraction storage resolution proves full time-conversion accuracy. | Require an error budget and independent reference results. | [Pinned Lox Time](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/crates/lox-time/src/time.rs) |
| **Rust in Space**: The talk describes current Lox storage. | Current reviewed source uses `Subsecond([u32; 6])`. Use the talk for design reasoning. | [Pinned Subsecond](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/crates/lox-time/src/subsecond.rs) |
| **Ownership and linked lists**: An iterative merge guarantees bounded stack use for the type. | Review recursive destruction separately. | [Drop Reference](https://doc.rust-lang.org/reference/destructors.html), [linked teaching discussion](https://rust-unofficial.github.io/too-many-lists/first-drop.html) |
| **Rust Style Guide**: Rust 2024 style is still nightly-only before release. | This sentence is stale. Check the installed formatter and current style-edition documentation. | [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/rustfmt-style-edition.html), [rustfmt configuration](https://raw.githubusercontent.com/rust-lang/rustfmt/main/Configurations.md) |
| **Style and API guides**: Add authors and author email as normal required metadata. | Current Cargo deprecates `authors`; email is optional. Preserve current project metadata policy. | [Cargo authors](https://doc.rust-lang.org/cargo/reference/manifest.html#the-authors-field) |
| **Google/style application risk**: Import grouping settings can be copied into any stable formatter configuration. | The checked formatter source marks `imports_granularity` and `group_imports` unstable. Verify the selected version. | [Formatter option definitions](https://raw.githubusercontent.com/rust-lang/rustfmt/main/Configurations.md) |
| **Beginner rules**: Derive Copy or Clone whenever fields permit it. | Check semantic duplication, resource ownership, size, and compatibility. A fixed array can be large without many fields. | [Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html), [Clone](https://doc.rust-lang.org/std/clone/trait.Clone.html) |
| **Beginner rules**: Copy removes lifetime concerns. | A copied reference still has its lifetime. Borrowed storage can be valid and useful. | [Lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) |
| **Beginner rules**: Explicitly slice String to satisfy an ordinary str-reference parameter. | A direct `&str` parameter can accept `&String` through deref coercion. Generic inference needs a separate check. | [Coercion sites](https://doc.rust-lang.org/reference/type-coercions.html) |
| **API guide**: Old optional Serde feature forwarding preserves optionality. | `serde/std` activates an optional dependency; `serde?/std` forwards conditionally on supported Cargo versions. | [Dependency features](https://doc.rust-lang.org/cargo/reference/features.html#dependency-features) |
| **API guide**: Error guidance from a std example applies unchanged to no_std. | Suitable no_std libraries can use `core::error::Error` from Rust 1.81. Apply target-specific errors where required. | [Core Error](https://doc.rust-lang.org/core/error/trait.Error.html) |
| **API guide**: Documentation hiding restricts access. | `#[doc(hidden)]` controls rendered docs, not Rust visibility. | [Visibility](https://doc.rust-lang.org/reference/visibility-and-privacy.html) |
| **Kernel supporting test docs**: The introduction's test-group list is complete. | The reviewed body also includes host `rusttest`. Select from the full body and target-tree version. | [Rust kernel tests](https://docs.kernel.org/rust/testing.html) |

## Policy decisions

These decisions define this set. They are not changes to Rust itself.

| Decision | Reason and trade-off | Blast radius |
| --- | --- | --- |
| Use a small core with conditional topic files. | The future skill needs only the rules for its task. The skill entry point must route every topic. | Reference loading. |
| Prefer official contracts over tutorial explanations. | Tutorials contain useful designs and verified errors. Their examples remain useful within limits. | Claim selection and citations. |
| Preserve project policy within safety constraints. | A generic guide cannot decide the host runtime, ABI, MSRV, or release model. | Future code changes. |
| Select typed errors from caller needs. | Enum matching and opaque evolution serve different requirements. | Public error APIs. |
| Keep hexagonal architecture optional. | A useful boundary can fit in modules; a template can add needless layers. | Dependency structure. |
| Make allocator, hasher, CPU, shrinking, and boxing choices conditional. | Gains depend on load, threat model, target, and lifetime. | Performance and deployment. |
| Keep company-specific rules opt-in. | Chromium layout and scheduling, Fuchsia locks, short-name limits, exact builder thresholds, and mandatory error shapes are local choices. | Style and platform integration. |
| Add verification scenarios before skill installation. | A readable reference set does not prove reliable model routing. | Future skill acceptance. |
| Add a separate Linux kernel profile. | Kbuild, Kconfig, kernel errors, C aliases, and wrapper policy differ from userspace Cargo practice. | Kernel code tasks only. |
| Compile full style and API sources without duplicating their manuals. | A short task route selects operational rules; detailed coverage records preserve the full review. | Reference loading and maintenance. |

## Coverage boundary

The review followed relevant in-page sections, same-site guide links, category pages, linked code examples, and owning technical references. The [link ledger](link-ledger.md) records access and exclusions. This was not an unlimited crawl of every repository and manual. No source application, architecture template, or historical macro expansion was build-verified.

The set does not provide a complete embedded, no_std, hard real-time, cryptographic, kernel, or safety-critical Rust policy. Such work needs target-specific rules and evidence. The tutorials' missing parts do not fill these gaps.

## Maintenance

For a source update, review changed rules and their owning contracts. Record the review date and version. Preserve rule IDs when meaning is stable. Record an incompatible policy change before changing an ID's meaning. Re-run document checks and future skill acceptance tests after integration. Links to `latest`, `main`, or unversioned manuals can change; use the project's pinned versions during implementation.
