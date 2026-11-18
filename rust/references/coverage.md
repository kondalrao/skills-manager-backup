# Source coverage

This map records source treatment. It is not another checklist to load on every task. A means adopt the principle, Q means apply with conditions, and N means no automatic default. The topic files define the actual rule strength and checks.

## Tutorial mapping

| Requested guide | Destination |
| --- | --- |
| Rust in Space | Types; numeric models |
| Production macro_rules | Macros |
| Error handling | Errors; public API evolution |
| Hexagonal architecture | Architecture and async; boundary tests |
| Ownership and linked lists | Ownership; collection and stack checks |
| Newtypes | Types; trait laws; safe validation |

## Google topic treatment

All sections were read.

| Topics | Treatment |
| --- | --- |
| Layout, imports, formatting | Preserve project conventions. |
| Ownership, parameters, results | Apply by ownership need. |
| Types, traits, naming | Apply by domain contract. |
| Documentation, API evolution | Apply with caller checks. |
| Unsafe code | Require safety evidence. |
| Panics, poison | Use explicit failure policy. |
| Macros, iteration, inference | Prefer clear code. |
| Chromium, Fuchsia, test frameworks | Local rules only. |

## Microsoft inventory


Each category link owns all IDs in that category. Use its `#M-...` fragment for a direct rule citation. Empty `Library Guidelines` and `Safety` headings in the aggregate add no rule.


## AI Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/ai/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-DESIGN-FOR-AI` | A | Use documented, idiomatic APIs and tests of observable behaviour. |
| `M-NO-META-DESIGN-DOCUMENTATION` | A | Keep user API docs about current behaviour; put decision history in its own record. |
| `M-RUST-SHAPED` | A | Preserve domain behaviour when porting; redesign ownership and error flow for Rust. |
| `M-SINGLE-ITEM-PATH` | Q | Prefer one canonical path; retain required deprecated compatibility paths. |
| `M-TAUTOLOGICAL-TESTS` | A | Test a requirement or invariant with an independent expectation. |

## Application Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/apps/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-APP-ERROR` | Q | Use the existing application reporter; preserve typed errors where recovery needs them. |
| `M-MIMALLOC-APPS` | N | Change the allocator only after target checks and representative comparison. |
| `M-TARGET-CPU` | Q | Require a proven fleet instruction baseline and test the oldest supported CPU. |

## Correctness Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/correctness/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-PANIC-CONTINUATION` | Q | Review unwind safety and isolation; a restart policy belongs to the application. |
| `M-PANIC-IS-STOP` | Q | Use Result for expected failure; never rely on a panic being catchable. |
| `M-PANIC-MESSAGE` | A | Explain the broken invariant with useful, non-secret context. |
| `M-PANIC-ON-BUG` | Q | Use types to prevent misuse; return errors for fallible boundary validation. |
| `M-UNSAFE-IMPLIES-UB` | A | Use unsafe for memory-safety obligations, not ordinary business danger. |
| `M-UNSAFE` | A | Require a narrow safety argument and suitable tests; benchmark a performance claim. |
| `M-UNSOUND` | A | Safe clients must not trigger UB; tests do not replace a soundness argument. |

## Documentation

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/docs/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-CANONICAL-DOCS` | A | Document examples, errors, panics, safety and aborts when applicable. |
| `M-DOC-INLINE` | Q | Use for owned re-exports when it improves rustdoc; inspect rendered output. |
| `M-FIRST-DOC-SENTENCE` | Q | Use a short summary; 15 words is a style target, not a hard technical limit. |
| `M-MODULE-DOCS` | A | Document each public module purpose and interaction rules. |

## FFI Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/ffi/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-FFI-NAMING` | Q | Use -sys/-ffi roles when compatible with the project naming scheme. |
| `M-FFI-TRANSLATES` | A | Keep boundary conversion separate from safe domain logic. |
| `M-ISOLATE-DLL-STATE` | A | Use explicit ABI and ownership; do not assume shared Rust runtime state. |


## Macros Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/macros/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-EXAMPLE-OVER-PROC` | Q | Choose macro_rules when it can express the required grammar clearly. |
| `M-MACRO-HELPERS` | A | Give generated code stable helper paths; hidden public helpers remain a contract. |
| `M-MACRO-LAST-RESORT` | A | First test whether functions, traits or generics solve the repetition. |
| `M-MACRO-MAIN-CRATE` | Q | Document the facade path; test renamed dependencies if they are supported. |
| `M-MACRO-VERSION-PIN` | Q | Pin tightly coupled companion crates when generated code needs that lockstep. |
| `M-MACROS-DONT-LIE` | A | Keep signatures and generated behaviour clear; document necessary transformation. |
| `M-PROC-IMPL` | Q | Keep token logic testable; a third crate is optional if existing tests suffice. |
| `M-PROC-IMPLIED-ITEMS` | A | Make generated public names explicit and test collisions. |

## Performance Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/performance/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-ASYNC-STACK-SIZE` | Q | Measure hot future sizes; preserve setup and polling semantics during changes. |
| `M-AVOID-INDIRECTION` | Q | Remove needless indirection after ownership and hot-path evidence. |
| `M-BOX-DST` | Q | Consider fixed-length storage when memory data supports it; it is not immutable. |
| `M-FAST-HASHER` | Q | Require trusted key origin and a measured gain; retain DoS protection otherwise. |
| `M-HOTPATH` | A | Profile and compare representative work against an explicit performance goal. |
| `M-INITIAL-CAPACITY` | Q | Reserve a credible bounded size; avoid attacker-controlled excessive reservation. |
| `M-LOG-OVERHEAD` | A | Measure enabled and disabled telemetry cost on a hot path. |
| `M-MEM-REUSE` | Q | Reuse buffers where lifecycle and retained-memory cost permit it. |
| `M-SHRINK-TO-FIT` | Q | Use for costly long-lived spare capacity; shrinking can reallocate or be partial. |
| `M-THROUGHPUT` | Q | Batch within latency, fairness and cancellation budgets; throughput is one metric. |
| `M-YIELD-POINTS` | Q | Use runtime-aware fairness; offload CPU work as needed; await need not suspend. |

## Project Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/project/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-CARGO-WORKSPACE` | Q | Share settings for related crates; keep feature and MSRV effects explicit. |
| `M-CRATES-FLAT-FOLDER` | Q | Use a simple layout for new work; preserve valid existing structures. |
| `M-CRATES-IN-WORKSPACE` | Q | Centralise related dependency versions when useful; Cargo also allows path deps. |
| `M-LATEST-EDITION` | Q | Select a stable edition compatible with MSRV; virtual workspaces need resolver. |
| `M-MSRV` | Q | Declare and test MSRV; select its release policy from user needs. |


## Universal Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/universal/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-DOCUMENTED-MAGIC` | A | Name significant constants and record their source and change consequence. |
| `M-LINT-OVERRIDE-EXPECT` | Q | Use reasoned expect when supported by MSRV; allow can suit generated code. |
| `M-LOG-STRUCTURED` | Q | Use fields and redaction; do not claim all format arguments allocate. |
| `M-PUBLIC-DEBUG` | A | Provide useful Debug with tested secret redaction. |
| `M-PUBLIC-DISPLAY` | Q | Provide Display for meaningful human text; keep secret values protected. |
| `M-REGULAR-FN` | A | Use free functions when no type or receiver owns the operation. |
| `M-SHORT-NAMES` | Q | Use clear domain names; no universal two-word or abbreviation rule. |
| `M-SMALLER-CRATES` | Q | Split for a real boundary; compare build graph and maintenance cost. |
| `M-STATIC-VERIFICATION` | A | Run project checks; use extra tools where risk warrants them; record limits. |
| `M-UPSTREAM-GUIDELINES` | Q | Use owning current docs; separate community patterns from language rules. |
| `M-WEASEL-WORDS` | Q | Name the role precisely; retain meaningful domain terms such as Service. |

## Libraries / Building Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/libs/building/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-FEATURES-ADDITIVE` | A | Keep library features additive; test the supported feature combinations. |
| `M-OOBE` | Q | Declare supported targets and prerequisites; do not promise untested portability. |
| `M-SYS-CRATES` | Q | Prefer reproducible native builds; respect upstream build, licence and system policy. |

## Libraries / Interoperability Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-DONT-LEAK-TYPES` | Q | Treat external public types as version contracts; interoperability can justify them. |
| `M-ESCAPE-HATCHES` | Q | Expose native handles only for a use case; mark unsafe only for safety obligations. |
| `M-FOREIGN-REEXPORTS` | Q | Use explicit public dependency policy; facade re-exports can improve compatibility. |
| `M-IMPL-ASREF` | Q | Choose borrowed or generic inputs from ownership and ergonomics, not universally. |
| `M-IMPL-IO` | Q | Separate protocol logic from effects; pick I/O traits that match supported runtimes. |
| `M-IMPL-RANGEBOUNDS` | Q | Use RangeBounds only when all its bound forms have a clear supported meaning. |
| `M-TYPES-SEND` | Q | Assert Send for promised cross-thread use; support local-only types when required. |

## Libraries / Resilience Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-AVOID-STATICS` | A | Make consistency-critical state explicit; account for duplicate crate versions. |
| `M-BUILD-RESULT` | A | Validate cross-field rules in build; strong field types can validate earlier. |
| `M-INTEGRATION-TESTS` | Q | Use tests/ for external API tests; unit tests can still verify public behaviour. |
| `M-LOG-NOT-PRINT` | A | Use project diagnostics; reserve stdout for an intended CLI/data interface. |
| `M-MOCKABLE-SYSCALLS` | Q | Provide controllable effects; use the simplest suitable fake, trait or enum. |
| `M-NO-GLOB-REEXPORTS` | Q | Prefer explicit exports; review intentional platform forwarding separately. |
| `M-STRONG-TYPES-GUARD` | A | Keep invariant fields private; validate every construction and mutation path. |
| `M-STRONG-TYPES` | Q | Use Path and domain types where semantics require them; numeric types can encode invariants. |
| `M-TEST-UTIL` | Q | Isolate test support; feature gates alone cannot guarantee release exclusion. |

## Libraries / UX Guidelines

[Category source](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/index.html).

| Source ID | Treatment | Proposed skill rule |
| --- | --- | --- |
| `M-ASYNC-FN` | Q | Prefer ordinary async syntax except when the future contract or setup timing needs more. |
| `M-AVOID-WRAPPERS` | Q | Hide incidental wrappers; keep them when ownership is part of the contract. |
| `M-BALANCED-MODULES` | A | Group by domain/use case and give the main entry types clear paths. |
| `M-COLLECTION-TRAITS` | Q | Implement the meaningful iterator forms and truthful bounds for the collection. |
| `M-DI-HIERARCHY` | Q | Use concrete types first; choose generic or dynamic extension from actual needs. |
| `M-ERRORS-CANONICAL-STRUCTS` | N | Choose struct or enum from recovery and compatibility needs; no mandatory backtrace. |
| `M-ESSENTIAL-FN-INHERENT` | Q | Make core operations discoverable; avoid redundant traits or method duplication. |
| `M-FROM-ERROR` | A | Use From for canonical conversion; map_err adds operation-specific context. |
| `M-INIT-BUILDER` | Q | Use a builder for complex optional configuration; numeric thresholds are heuristics. |
| `M-INIT-CASCADED` | Q | Group related arguments by meaning; avoid extra wrapper layers with no benefit. |
| `M-NO-PRELUDE` | Q | Prefer explicit imports; retain deliberate established ecosystem preludes. |
| `M-PARAMETER-CONSISTENCY` | Q | Keep consistent order and final closures; multiple callbacks can be justified. |
| `M-SERVICES-CLONE` | Q | Use cheap shared handles where sharing is required; document Clone semantics. |
| `M-SIMPLE-ABSTRACTIONS` | A | Keep common public types easy to name; justify advanced generic structure. |



## Source reference defects

`M-RUNTIME-ABSTRACTED`, `M-ABSTRACTIONS-DONT-NEST`, and `M-DOC-FIRST-SENTENCE` are referenced by the source but absent as rule sections. The actual related IDs include `M-SIMPLE-ABSTRACTIONS` and `M-FIRST-DOC-SENTENCE`. The source also has a `.map_error()` typo; Rust uses `.map_err()`. Do not create missing rules from those names.

## Added source profiles in version 1.1

- [Full API coverage](api-coverage.md): all 54 checklist IDs and 11 topic chapters.
- [Full style coverage](style-coverage.md): introduction and all nine numbered chapters.
- [Kernel profile](kernel-profile.md): style/imports, comments, rustdoc, C FFI types, naming, lints, and error handling. Supporting kernel build and test documents were also reviewed.
- [Beginner rules](https://joshua-laughner.io/posts/rust-beginning-rules-of-thumb/): read-only inputs map to R-OWN-01/02; duplication maps to R-OWN-04; owned fields and the graph-ID example map to R-OWN-05. All three rules and their exceptions were reviewed.
