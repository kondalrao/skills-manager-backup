# Link review record

Reviewed: 2026-11-15. “Read” means the relevant text or code was available. It does not mean that a whole manual or repository was audited. In-page sections were read with each guide. This is a bounded technical review, not a recursive crawl.

## Microsoft


Status: opened/read unless noted. The aggregate supplied the complete rule content; category pages checked canonical paths and anchor targets. The ledger records selected relevant links, not every link in an unbounded web graph.

| Group | URLs checked | Use |
| --- | --- | --- |
| Supplied source | [https://microsoft.github.io/rust-guidelines/agents/all.txt](https://microsoft.github.io/rust-guidelines/agents/all.txt) | Full 90-rule inventory; local extraction read in six ranges. |
| Scope | [https://microsoft.github.io/rust-guidelines/](https://microsoft.github.io/rust-guidelines/) | Version, licence context, applicability. |
| Category pages | [https://microsoft.github.io/rust-guidelines/guidelines/ai/index.html](https://microsoft.github.io/rust-guidelines/guidelines/ai/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/apps/index.html](https://microsoft.github.io/rust-guidelines/guidelines/apps/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/correctness/index.html](https://microsoft.github.io/rust-guidelines/guidelines/correctness/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/docs/index.html](https://microsoft.github.io/rust-guidelines/guidelines/docs/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/ffi/index.html](https://microsoft.github.io/rust-guidelines/guidelines/ffi/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/macros/index.html](https://microsoft.github.io/rust-guidelines/guidelines/macros/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/performance/index.html](https://microsoft.github.io/rust-guidelines/guidelines/performance/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/project/index.html](https://microsoft.github.io/rust-guidelines/guidelines/project/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/universal/index.html](https://microsoft.github.io/rust-guidelines/guidelines/universal/index.html) | Canonical topic references. |
| Library category pages | [https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/index.html](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/libs/building/index.html](https://microsoft.github.io/rust-guidelines/guidelines/libs/building/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/index.html](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/index.html) ; [https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/index.html](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/index.html) | Public API, build, ownership and testing rules. |
| Owning Rust safety docs | [https://doc.rust-lang.org/reference/behavior-considered-undefined.html](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) ; [https://doc.rust-lang.org/nomicon/ffi.html](https://doc.rust-lang.org/nomicon/ffi.html) ; [https://doc.rust-lang.org/std/panic/fn.catch_unwind.html](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html) | Soundness and unwind limits. |
| Linked safety tools | [https://github.com/rust-lang/miri](https://github.com/rust-lang/miri) ; [https://rust-lang.github.io/unsafe-code-guidelines/](https://rust-lang.github.io/unsafe-code-guidelines/) | Test limits and current UCG status. |
| Cargo | [https://doc.rust-lang.org/cargo/reference/features.html](https://doc.rust-lang.org/cargo/reference/features.html) ; [https://doc.rust-lang.org/cargo/reference/workspaces.html](https://doc.rust-lang.org/cargo/reference/workspaces.html) ; [https://doc.rust-lang.org/cargo/reference/semver.html](https://doc.rust-lang.org/cargo/reference/semver.html) | Feature unification, resolver and compatibility. |
| Standard library | [https://doc.rust-lang.org/std/error/trait.Error.html](https://doc.rust-lang.org/std/error/trait.Error.html) ; [https://doc.rust-lang.org/std/backtrace/struct.Backtrace.html](https://doc.rust-lang.org/std/backtrace/struct.Backtrace.html) ; [https://doc.rust-lang.org/std/vec/struct.Vec.html](https://doc.rust-lang.org/std/vec/struct.Vec.html) ; [https://doc.rust-lang.org/std/collections/struct.HashMap.html](https://doc.rust-lang.org/std/collections/struct.HashMap.html) ; [https://doc.rust-lang.org/std/marker/trait.Send.html](https://doc.rust-lang.org/std/marker/trait.Send.html) ; [https://doc.rust-lang.org/std/sync/struct.Arc.html](https://doc.rust-lang.org/std/sync/struct.Arc.html) ; [https://doc.rust-lang.org/std/boxed/struct.Box.html](https://doc.rust-lang.org/std/boxed/struct.Box.html) ; [https://doc.rust-lang.org/std/any/struct.TypeId.html](https://doc.rust-lang.org/std/any/struct.TypeId.html) ; [https://doc.rust-lang.org/std/macro.format_args.html](https://doc.rust-lang.org/std/macro.format_args.html) | Error, allocation, thread and representation contracts. |
| Compiler and traits | [https://doc.rust-lang.org/rustc/codegen-options/index.html](https://doc.rust-lang.org/rustc/codegen-options/index.html) ; [https://doc.rust-lang.org/reference/items/traits.html](https://doc.rust-lang.org/reference/items/traits.html) | CPU baseline and dyn compatibility. |
| Telemetry API | [https://docs.rs/tracing/latest/tracing/macro.event.html](https://docs.rs/tracing/latest/tracing/macro.event.html) | Structured fields and formatted message support. |

Excluded: navigation duplicates; screenshot images that only compare visual doc layout; social quotations; generic design essays; benchmark-tool marketing; third-party package choices not selected for this neutral guideline set; platform-specific installation guides. These exclusions do not support a claim that the entire link graph was reviewed.


## Google

The complete [Rust guide](https://google.github.io/styleguide/rustguide.html) and its in-page topics were read. Followed technical references included the [Rust Style Guide](https://doc.rust-lang.org/style-guide/), [API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html), [Cargo layout](https://doc.rust-lang.org/cargo/guide/project-layout.html), [coherence rules](https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence), [dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility), [non_exhaustive](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute), and [must_use](https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-must_use-attribute).

The owning standard-library pages for `Arc`, `Mutex`, and `catch_unwind` were read to check the guide's scoped policies. API naming, interoperability, flexibility, documentation, predictability, type safety, macros, and future-proofing chapters were also opened.

The [String addition contract](https://doc.rust-lang.org/std/string/struct.String.html#impl-Add%3C%26str%3E-for-String) was read to check the guide's allocation comparison. It confirms reuse of the left-hand buffer.

Excluded: Google product glossaries, C++ naming essays, platform import/build installation instructions, compiler-internal type catalogs, and local test-framework setup. No neutral rule depends on those excluded platform instructions. Their local status is preserved in the coverage map.

## Errors and architecture


All internal section links in both requested tutorials were covered through the complete article text. Links that point to code references were read in article context. Jina Reader omitted most code blocks; the web reader exposed code blocks for specific passages. No claim in this note depends on an unobserved code block.

| Linked destination | Result and relevance |
| --- | --- |
| [Error tutorial release](https://github.com/howtocodeit/article-md/releases/tag/error-handling@v1.1.2) | Opened; version record. |
| [Architecture tutorial release](https://github.com/howtocodeit/article-md/releases/tag/master-hexagonal-architecture-in-rust@v1.1.7) | Opened; version record. |
| [anyhow](https://docs.rs/anyhow/latest/anyhow/) | Read API overview, context, downcast, backtrace, and `no_std` sections. |
| [thiserror](https://docs.rs/thiserror/latest/thiserror/) | Read derive, source, conversion, and public API sections. |
| [Actix](https://actix.rs/) → [ResponseError](https://docs.rs/actix-web/latest/actix_web/error/trait.ResponseError.html) | Read the owning API contract; supports conversion and downcasts. |
| [tracing](https://tracing.rs/tracing/) → [crate docs](https://docs.rs/tracing/latest/tracing/) | Original host failed in the web reader; crate-owner documentation was available. Names in the article include an unstable-era collector vocabulary; use the selected crate version. |
| [wgpu ray-tracing source](https://github.com/gfx-rs/wgpu/blob/1ea5498038b2fd0392bd6cbd81ec71b2438e5c95/wgpu-core/src/ray_tracing.rs) | Opened pinned code example; not adopted as a mandatory error layout. |
| [Error member-access issue](https://github.com/rust-lang/rust/issues/99301) | Opened; use current `Error` API docs for stable status. |
| [I/O error issue](https://github.com/rust-lang/rust/issues/86442) | Opened; current `ErrorKind` docs are the operative contract. |
| [Read](https://doc.rust-lang.org/std/io/trait.Read.html), [Write](https://doc.rust-lang.org/std/io/trait.Write.html) | Read signatures; the standard I/O error contract is explicit. |
| [Axum](https://docs.rs/axum/latest/axum/) | Read overview, runtime dependency, state, and example API. |
| [Newtypes old route](https://www.howtocodeit.com/articles/ultimate-guide-rust-newtypes) | Followed redirect to requested newtypes guide; inspected constructor section. Full review belongs to the sibling research task. |
| [Original hexagonal architecture paper](https://alistair.cockburn.us/hexagonal-architecture/) | Read the original intent, ports, adapters, and isolation requirements. |
| [hexarch template](https://github.com/howtocodeit/hexarch) | Opened project page. Template was not cloned, built, or approved as a default. |
| [zerocopy](https://docs.rs/zerocopy/latest/zerocopy/) | Read overview and conversion guarantees. It does not establish that logical architecture boundaries are unsuitable for all fast programs. |

Additional primary sources used to correct claims are linked in the rule and correction tables.

## Exclusions and limits

- Excluded newsletter, privacy, social sharing, comments, images, and book sales links. They do not define Rust behavior.
- Excluded the Go examples and Grafana search from Rust rule evidence. They illustrate a general risk but do not own a Rust contract.
- Excluded the Stack Overflow discussion as technical authority. Used Rust `Arc` and `Sync` documentation instead.
- Excluded historical third-party Rust forks and the nightly `stdrs.dev` mirror as current API evidence. Used current Rust documentation instead.
- Some linked `/articles/` routes are historical aliases. The requested `/guides/` routes are the current readable pages.
- No example application was compiled. Do not describe the tutorials or their template as build-verified.
- Documentation versions observed were mixed current site versions. A consumer must use the project's Rust version, dependency versions, target, and feature set. These notes do not set an MSRV or approve dependency updates.


## Macros and newtypes


Visited successfully:

- Both requested article URLs, with all relevant in-page sections and numbered code references covered as part of the page review.
- Both article version links: [macro release](https://github.com/howtocodeit/article-md/releases/tag/macro-rules%40v1.0.7) and [newtype release](https://github.com/howtocodeit/article-md/releases/tag/ultimate-guide-rust-newtypes%40v1.0.15).
- The macro guide's Book link redirects; reviewed [current macro chapter](https://doc.rust-lang.org/book/ch20-05-macros.html).
- The macro guide's [assert_eq docs](https://doc.rust-lang.org/std/macro.assert_eq.html), [axum repository](https://github.com/tokio-rs/axum), [historical Tokio join source](https://github.com/tokio-rs/tokio/blob/39cf6bba0035bbb32fe89bf8ad0189e96fa2d926/tokio/src/macros/join.rs#L58), and [Little Book internal rules](https://danielkeep.github.io/tlborm/book/pat-internal-rules.html). Added current Tokio docs to avoid treating the historical code as the current API.
- The newtype guide's [Deref docs](https://doc.rust-lang.org/std/ops/trait.Deref.html#deref-coercion), [method-call reference](https://doc.rust-lang.org/reference/expressions/method-call-expr.html), [num repository](https://github.com/rust-num/num), both derive crate docs, and both Clippy lint links. The Clippy URLs redirect to `clippy.rust-lang.org`; checked `derive_ord_xor_partial_ord` and `inherent_to_string_shadow_display` there.
- Added primary Rust Reference, Edition Guide, standard trait docs, rustdoc book, and RFC links listed beside rules above.

Excluded: images, newsletter, share and discussion UI, privacy links, generic home-page navigation, and paid book storefronts. These do not establish a Rust rule. No claim depends on an unread paid book. The newtype guide's Book home link was followed through the relevant official trait and Reference pages rather than by reviewing the whole Book.

Access limitation: Jina Reader fetched both article bodies but omitted code blocks. Web extraction supplied the article code and official documentation. No claim of a full recursive site crawl is made. Only relevant rule-bearing links were followed. No dependency-specific examples were compiled. Check selected versions when a real project adopts these rules.

## Time models and ownership


All entries below were opened. A successful read means relevant text was available. It does not mean that the whole repository or manual was audited.

| Link | Result and use |
| --- | --- |
| [Space article](https://www.howtocodeit.com/guides/rust-in-space) | Full speaker notes read through Jina Reader and web reader. |
| [Space article release](https://github.com/howtocodeit/article-md/releases/tag/rust-in-space@v1.0.7) | Opened to record the linked version. |
| [Talk slides](https://docs.google.com/presentation/d/1nAUbbKHDrMSGnDsKFn3sBYLgkv9KPc0K2lYiyEE83iw/edit?usp=sharing) | Opened. The extracted page has presentation controls and metadata, not the full slide text. The article includes slide images and speaker notes; those notes are the research basis. |
| [Lox repository](https://github.com/lox-space/lox) | Read project description. Followed its documentation and source tree. |
| [Lox documentation](https://docs.lox.rs/) | Opened; landing page has little technical content. Used pinned code instead. |
| [Lox source tree](https://api.github.com/repos/lox-space/lox/git/trees/main?recursive=1) | Read through the GitHub connector. Snapshot SHA recorded above. Direct shell fetch returned HTTP 403; connector succeeded. |
| [Lox subsecond source](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/crates/lox-time/src/subsecond.rs) | Full file read; verifies representation drift. Not a full correctness audit. |
| [Lox time source](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/crates/lox-time/src/time.rs) | Read lines 1–220; verifies typed scale, constructors, and accuracy limit. |
| [Lox README](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/README.md) | Read; current library scope and pre-1.0 API status. |
| [Libre Space Foundation](https://libre.space/) | Article link redirects to its main site. The page read does not verify a current funding or certification claim for Ephemerista. No such claim is adopted. |
| [Ownership article](https://www.howtocodeit.com/guides/rust-ownership-explained-merging-linked-lists) | Full prose and all code variants read. Jina omits some code; web reader supplied code. Internal code anchors were inspected in their surrounding sections. |
| [Ownership article release](https://github.com/howtocodeit/article-md/releases/tag/merging-linked-lists@v1.1.2) | Opened to record the linked version. |
| [Ownership discussion](https://github.com/howtocodeit/comments/discussions/6#discussioncomment-9930479) | Read the suggested iterative solution, simplifications, and author acceptance. |
| [Too Many Linked Lists](https://rust-unofficial.github.io/too-many-lists/) | Read introduction and collection guidance; followed the relevant Drop chapter. |
| [Drop chapter](https://rust-unofficial.github.io/too-many-lists/first-drop.html) | Read recursive-destruction analysis and iterative approach. |
| [Rust `Option`](https://doc.rust-lang.org/std/option/enum.Option.html) | Read `as_ref`, `as_mut`, `unwrap`, `take`, `insert`, and `get_or_insert` contracts. |
| [Rust `swap`](https://doc.rust-lang.org/std/mem/fn.swap.html), [Rust `replace`](https://doc.rust-lang.org/std/mem/fn.replace.html) | Read signatures, state effects, and examples. |
| [Rust `rc`](https://doc.rust-lang.org/std/rc/), [Rust `cell`](https://doc.rust-lang.org/std/cell/) | Read ownership, thread, cycle, and runtime-borrow limits. |
| [Rust `LinkedList`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html) | Read collection selection guidance. |
| [Rust `f64`](https://doc.rust-lang.org/std/primitive.f64.html) | Read binary64 description, finite/normal/subnormal contracts, and precision-related examples. |
| [Rust layout](https://doc.rust-lang.org/reference/type-layout.html), [Rust `PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html) | Read size/alignment and marker layout sections. |
| [Rust `TryFrom`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html) | Read fallible-conversion contract. |
| [Rust `Instant`](https://doc.rust-lang.org/std/time/struct.Instant.html) | Read clock guarantees, platform limits, and checked operations. |
| [PyO3 classes](https://pyo3.rs/main/class.html) | Read restrictions and concrete-wrapper example. |

Excluded: site navigation, newsletters, privacy pages, image assets, share controls, general coding-challenge home pages, and unrelated chapters. The YouTube recording duplicates the supplied speaker notes and was not watched. No relevant same-site article links exist in these two article bodies beyond the current-page anchors and home-page navigation.

An extra attempt to open `[https://libre.space/projects/ephemerista/`](https://libre.space/projects/ephemerista/`) did not return content. That path was a discovery attempt, not a link supplied by the article. An extra attempt to open the historical-looking `std::convert::Infallible` enum URL returned 404; no rule depends on it.


## Additional primary checks

Read the relevant contract sections of [Serde container conversion](https://serde.rs/container-attrs.html#try_from), [Clippy usage](https://doc.rust-lang.org/clippy/usage.html), [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html), [Cargo package](https://doc.rust-lang.org/cargo/commands/cargo-package.html), [MSRV](https://doc.rust-lang.org/cargo/reference/rust-version.html), [workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html), [async functions](https://doc.rust-lang.org/reference/items/functions.html#async-functions), [procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html), [destructors](https://doc.rust-lang.org/reference/destructors.html), [Tokio blocking work](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html), [Tokio task scheduling](https://docs.rs/tokio/latest/tokio/task/), [Tokio mutex selection](https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html#which-kind-of-mutex-should-you-use), [Anyhow context](https://docs.rs/anyhow/latest/anyhow/trait.Context.html), [allocation](https://doc.rust-lang.org/std/alloc/index.html), and [Criterion](https://bheisler.github.io/criterion.rs/book/).

The official Book chapters on ownership, panic selection, and testing were used for baseline principles. Specific standard-library or Reference pages beside each rule define the detailed contract. No whole-book audit is claimed.

## Access limits

Jina Reader omitted code blocks on some tutorial pages. Web extraction supplied code for the relevant passages. The slide deck did not expose all slide text, and the duplicate video was not watched. Pinned Lox source and article speaker notes supplied the checked claims. Failed historical paths were replaced with the owning current documentation where available. A failed or partial read is not evidence for an unobserved claim.

## Added sources in version 1.1

### Nightly Rust Style Guide


Opened: the requested nightly root; `print.html`; `items.html`; `statements.html`; `expressions.html`; `types.html`; `advice.html`; `cargo.html`; `principles.html`; `editions.html`; `nightly.html`, all under `https://doc.rust-lang.org/nightly/style-guide/`.

Followed: [stable style-edition page](https://doc.rust-lang.org/style-guide/editions.html), [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/rustfmt-style-edition.html), [style RFC](https://rust-lang.github.io/rfcs/3338-style-evolution.html), [rustfmt repository and README](https://github.com/rust-lang/rustfmt), [configuration source](https://github.com/rust-lang/rustfmt/blob/main/Configurations.md), [configuration viewer](https://rust-lang.github.io/rustfmt/), [Cargo manifest](https://doc.rust-lang.org/cargo/reference/manifest.html), [TOML keys](https://toml.io/en/v1.0.0#keys), and [SPDX identifiers](https://spdx.org/licenses/).

The dynamic rustfmt configuration viewer returned only its controls. A version-filtered URL failed. The raw first-party `Configurations.md` supplied the relevant option definitions. Its selected sections were read for `edition`, `style_edition`, `reorder_imports`, `imports_granularity`, and `group_imports`. The source's `main` branch can change; check the installed version before use.

Excluded: editor installation instructions, formatter development workflow, historical issue discussion about small-item heuristics, the old style archive source tree, and the frontmatter tracking issue. These do not change the proposed neutral defaults. The current archive link and frontmatter section were read, but this review does not claim to audit the archive or implement unstable syntax.

No supplied Rust repository exists for a formatter test. No toolchain was installed or changed. This research verifies source coverage and rule scope; it does not certify formatter support in a future target project.

### Full Rust API Guidelines


Status **read**: landing page, checklist, and all chapter URLs linked in the inventory above. Each chapter's complete body was fetched through Jina Reader and read. Browser extraction also confirmed every chapter. No chapter was sampled in place of reading it.

Status **read**: [External links](https://rust-lang.github.io/api-guidelines/external-links.html). Its six RFC links were opened: [199](https://github.com/rust-lang/rfcs/blob/master/text/0199-ownership-variants.md), [344](https://github.com/rust-lang/rfcs/blob/master/text/0344-conventions-galore.md), [430](https://github.com/rust-lang/rfcs/blob/master/text/0430-finalizing-naming-conventions.md), [505](https://github.com/rust-lang/rfcs/blob/master/text/0505-api-comment-conventions.md), [1574](https://github.com/rust-lang/rfcs/blob/master/text/1574-more-api-documentation-conventions.md), and [1687](https://github.com/rust-lang/rfcs/pull/1687). RFC 1687 timed out twice in browser extraction; Jina Reader fetched its first-party PR discussion. These historical RFCs provide background; current Reference, Cargo, and rustdoc documentation govern current behavior. The other two external links are secondary design essays/catalogs. They are not needed as authorities and were excluded from technical rule evidence.

Status **read**: all current-source pages in the correction list. Also visited official [Read](https://doc.rust-lang.org/std/io/trait.Read.html), [Write](https://doc.rust-lang.org/std/io/trait.Write.html), and [From](https://doc.rust-lang.org/std/convert/trait.From.html) pages to check interface claims. Initial `serde.rs/trait-bound.html` failed; the correct linked topic is [attr-bound.html](https://serde.rs/attr-bound.html), which succeeded.

Exclusions: repetitive example links for already verified standard-library behavior; historical pinned third-party API examples; nontechnical navigation; issue trackers used only to mark unresolved naming choices; unrelated book and site navigation. This is full chapter coverage, not an unlimited recursive crawl of every example or its dependencies.


### Linux kernel profile


| Source | Read result |
| --- | --- |
| [Coding Guidelines](https://docs.kernel.org/rust/coding-guidelines.html) and [page source](https://docs.kernel.org/_sources/rust/coding-guidelines.rst.txt) | Full guide read; headings and policy map checked. |
| [Rust index](https://docs.kernel.org/rust/index.html) | Read entry points and generated-doc location. |
| [General Information](https://docs.kernel.org/rust/general-information.html) | Full page read: no_std, docs, Clippy, bindings, abstractions, Kconfig. |
| [Quick Start](https://docs.kernel.org/rust/quick-start.html) | Full page read: tool requirements, developing tools, configuration, build. Package-install examples were not executed or imported as fixed requirements. |
| [Arch Support](https://docs.kernel.org/rust/arch-support.html) | Read supported targets and constraints. Future work must recheck its target. |
| [Rust testing](https://docs.kernel.org/rust/testing.html) | Full page read, including host tests and selftests. |
| [kernel crate](https://rust.docs.kernel.org/kernel/index.html), [source](https://rust.docs.kernel.org/src/kernel/lib.rs.html), [prelude](https://rust.docs.kernel.org/kernel/prelude/index.html) | Checked no_std, abstraction boundary, C alias exports, and representative macro safety contract. Direct generated pages report v7.4-rc2. |
| [kernel Result](https://rust.docs.kernel.org/kernel/error/type.Result.html#error-codes-in-c-and-rust) | Full guidance read, including propagation and panic limit. |
| [kunit_tests](https://rust.docs.kernel.org/macros/attr.kunit_tests.html) | Read module registration and CONFIG_KUNIT behavior. Direct recheck reports v7.4-rc2. |
| [safety source](https://rust.docs.kernel.org/src/kernel/safety.rs.html) | Read debug-only unsafe precondition assertion. |
| [Rust documentation guide](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html), [CommonMark](https://commonmark.org/help/) | Read linked documentation format guidance. |
| [Rust naming](https://rust-lang.github.io/api-guidelines/naming.html), [diagnostics](https://doc.rust-lang.org/stable/reference/attributes/diagnostics.html) | Read naming/conversion guidance and lint expectation semantics. |
| [Rust undefined behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) | Read soundness obligations and FFI scope. |
| [Kernel deprecated interfaces](https://docs.kernel.org/process/deprecated.html#bug-and-bug-on) | Followed the kernel Result link to BUG guidance. Read that section; did not import unrelated C migration rules. |
| [LLVM build guide](https://docs.kernel.org/kbuild/llvm.html) | Read target selection and consistent tool invocation rules. |
| [KUnit index](https://docs.kernel.org/dev-tools/kunit/index.html), [start](https://docs.kernel.org/dev-tools/kunit/start.html), [wrapper](https://docs.kernel.org/dev-tools/kunit/run_wrapper.html) | Read configuration, build directory, QEMU, and command prerequisites. |

Excluded: unrelated global site navigation, translations, styling tools, distro-specific installation work, and unrelated subsystem manuals. The requested coding guide does not link to a KLINT or a general invariants manual. No KLINT requirement is claimed. Concrete API invariants must be read when the code task selects those APIs.


### Beginner rules of thumb

Read the full [article](https://joshua-laughner.io/posts/rust-beginning-rules-of-thumb/), all three in-page rule sections, exceptions, and the graph-ID example. There were no rule-bearing external links in the body. Unrelated navigation and ORCID were excluded as Rust evidence.

Added owning checks: [Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html), [Clone](https://doc.rust-lang.org/std/clone/trait.Clone.html), [Drop](https://doc.rust-lang.org/std/ops/trait.Drop.html), [coercions](https://doc.rust-lang.org/reference/type-coercions.html), and [struct lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html). Read the relevant sections. Jina and web reads succeeded. The article examples are schematic and were not compiled.
