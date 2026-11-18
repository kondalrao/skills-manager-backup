# Rust API Guidelines coverage

Reviewed: 2026-11-15. All 54 unique checklist IDs are mapped below. All 11 topic chapters were read. Adopt means a default for its applicable API; qualify preserves the intent with conditions; not default needs a project choice. These are recommendations, not language requirements.

[Source landing page](https://rust-lang.github.io/api-guidelines/), [checklist](https://rust-lang.github.io/api-guidelines/checklist.html). Use [Library API](library-api.md) as the normal task entry point.

## Naming — 7 rules

Source: [Naming](https://rust-lang.github.io/api-guidelines/naming.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-CASE` | Adopt: use Rust case conventions, including acronym case. | [core.md](core.md): R-CORE-02 |
| `C-CONV` | Adopt: name views `as_`, work/conversions `to_`, ownership transfer `into_`; state real cost. | [library-api.md](library-api.md): R-API-02 |
| `C-GETTER` | Qualify: use `field` and `field_mut`; preserve meaningful established `get` APIs. | [library-api.md](library-api.md): R-API-02 |
| `C-ITER` | Adopt: homogeneous collections use `iter`, `iter_mut`, and `into_iter` for their ownership forms. | [library-api.md](library-api.md): R-API-02 |
| `C-ITER-TY` | Adopt: name public iterator types after producing methods, in their owning module. | [library-api.md](library-api.md): R-API-02 |
| `C-FEATURE` | Adopt: name capabilities directly, without filler or negative feature names. | [library-api.md](library-api.md): R-API-02 |
| `C-WORD-ORDER` | Adopt: keep word order consistent across related APIs. | [library-api.md](library-api.md): R-API-02 |

## Interoperability — 8 rules

Source: [Interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-COMMON-TRAITS` | Qualify: review useful standard traits; implement only when their meaning fits. | [types-ownership.md](types-ownership.md): R-TYPE-03, R-OWN-04 |
| `C-CONV-TRAITS` | Adopt: prefer standard conversion traits; implement `From`/`TryFrom` rather than their blanket reciprocals. | [types-ownership.md](types-ownership.md): R-TYPE-02 |
| `C-COLLECT` | Qualify: collections support `FromIterator` and `Extend` when their invariants permit these infallible operations. | [library-api.md](library-api.md): R-API-03 |
| `C-SERDE` | Qualify: add Serde for intended data exchange; optional feature where appropriate; preserve validation. | [library-api.md](library-api.md): R-API-05 |
| `C-SEND-SYNC` | Qualify: preserve intended thread behavior; never add unsafe auto-trait implementations merely for convenience. | [unsafe-ffi.md](unsafe-ffi.md): R-SAFE-03 |
| `C-GOOD-ERR` | Qualify: provide meaningful diagnostic errors and source chains; add thread bounds when callers need them. | [errors.md](errors.md): R-ERR-02 |
| `C-NUM-FMT` | Qualify: bit-oriented numbers support binary/octal/hex formatting where useful. | [performance-numerics.md](performance-numerics.md): R-NUM-01 |
| `C-RW-VALUE` | Adopt: generic synchronous readers/writers normally accept `R: Read`/`W: Write` by value; callers can pass `&mut`. | [library-api.md](library-api.md): R-API-03 |

## Macros — 5 rules

Source: [Macros](https://rust-lang.github.io/api-guidelines/macros.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-EVOCATIVE` | Adopt: input syntax should make generated Rust structure clear. | [macros.md](macros.md): R-MAC-02 |
| `C-MACRO-ATTR` | Adopt: item macros accept and forward relevant attributes, including per-item `cfg` and derives. | [macros.md](macros.md): R-MAC-02 |
| `C-ANYWHERE` | Qualify: item macros work in intended item contexts; test module and function scope where supported. | [macros.md](macros.md): R-MAC-02 |
| `C-MACRO-VIS` | Adopt: use normal Rust visibility syntax and private defaults for generated items. | [macros.md](macros.md): R-MAC-02 |
| `C-MACRO-TY` | Adopt: type inputs support relevant primitive, reference, relative, absolute, parent, and generic forms. | [macros.md](macros.md): R-MAC-02 |

## Documentation — 8 rules

Source: [Documentation](https://rust-lang.github.io/api-guidelines/documentation.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-CRATE-DOC` | Adopt: explain crate purpose, use, and main workflows. | [core.md](core.md): R-CORE-04 |
| `C-EXAMPLE` | Qualify: public APIs need useful examples or links to shared examples; avoid mechanical repetition. | [core.md](core.md): R-CORE-04 |
| `C-QUESTION-MARK` | Qualify: fallible examples normally use `?`; intentional panic demonstrations can differ. | [core.md](core.md): R-CORE-04 |
| `C-FAILURE` | Adopt: document relevant errors, panics, and caller safety duties, including trait methods. | [core.md](core.md): R-CORE-04 |
| `C-LINK` | Adopt: link related concepts and items; prefer current intra-doc item links. | [core.md](core.md): R-CORE-04 |
| `C-METADATA` | Qualify: use current Cargo publishing metadata; do not require deprecated fields. | [library-api.md](library-api.md): R-API-07 |
| `C-RELNOTES` | Adopt: document significant changes and migrations; identify the released source revision. | [library-api.md](library-api.md): R-API-07 |
| `C-HIDDEN` | Qualify: hide irrelevant rustdoc details; use visibility for real access limits. | [core.md](core.md): R-CORE-04 |

## Predictability — 7 rules

Source: [Predictability](https://rust-lang.github.io/api-guidelines/predictability.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-SMART-PTR` | Qualify: generic smart pointers use associated functions to reduce target-method collisions. | [library-api.md](library-api.md): R-API-02 |
| `C-CONV-SPECIFIC` | Adopt: place ad-hoc conversions on the type with the more specific meaning. | [library-api.md](library-api.md): R-API-06 |
| `C-METHOD` | Adopt: use a method when the operation has a clear receiver. | [library-api.md](library-api.md): R-API-02 |
| `C-NO-OUT` | Qualify: return results directly; allow deliberate in-place mutation and buffer reuse. | [types-ownership.md](types-ownership.md): R-OWN-02 |
| `C-OVERLOAD` | Adopt: operators retain expected domain meaning and laws. | [library-api.md](library-api.md): R-API-02 |
| `C-DEREF` | Qualify: reserve deref coercion for intended transparent pointer-like behavior. | [types-ownership.md](types-ownership.md): R-TYPE-03 |
| `C-CTOR` | Adopt: constructors are inherent associated functions with conventional or domain-specific names. | [library-api.md](library-api.md): R-API-02 |

## Flexibility — 4 rules

Source: [Flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-INTERMEDIATE` | Qualify: return useful computed information when it avoids repeated work without exposing unstable details. | [library-api.md](library-api.md): R-API-03 |
| `C-CALLER-CONTROL` | Adopt: take ownership only when needed; let callers choose copying. | [types-ownership.md](types-ownership.md): R-OWN-01 |
| `C-GENERIC` | Qualify: use the least restrictive useful input contract; weigh inference, code size, and clarity. | [types-ownership.md](types-ownership.md): R-OWN-02 |
| `C-OBJECT` | Qualify: design dyn compatibility when trait-object use is intended; verify current Reference rules. | [architecture-async.md](architecture-async.md): R-ARCH-02 |

## Type safety — 4 rules

Source: [Type safety](https://rust-lang.github.io/api-guidelines/type-safety.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-NEWTYPE` | Adopt: distinct types prevent meaningful unit or domain mix-ups. | [types-ownership.md](types-ownership.md): R-TYPE-01 |
| `C-CUSTOM-TYPE` | Qualify: replace unclear primitive arguments with meaningful types; keep obvious Boolean or optional meanings simple. | [types-ownership.md](types-ownership.md): R-TYPE-01 |
| `C-BITFLAG` | Qualify: independently combinable flags use a flags type; one-of choices use enums. | [library-api.md](library-api.md): R-API-04 |
| `C-BUILDER` | Qualify: use a builder for complex construction; ownership decides consuming versus borrowed methods. | [library-api.md](library-api.md): R-API-04 |

## Dependability — 3 rules

Source: [Dependability](https://rust-lang.github.io/api-guidelines/dependability.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-VALIDATE` | Qualify: enforce validity with types or runtime checks. Debug-only checks cannot enforce release safety or external-input validity. | [types-ownership.md](types-ownership.md): R-TYPE-02 |
| `C-DTOR-FAIL` | Adopt: avoid panics in `Drop`; provide fallible explicit close/finish operations where needed. | [library-api.md](library-api.md): R-LIFE-01 |
| `C-DTOR-BLOCK` | Qualify: provide explicit shutdown for blocking teardown; keep destructor work bounded and documented. | [library-api.md](library-api.md): R-LIFE-01 |

## Debuggability — 2 rules

Source: [Debuggability](https://rust-lang.github.io/api-guidelines/debuggability.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-DEBUG` | Qualify: public types normally implement useful `Debug`; redact secrets and respect justified type limits. | [library-api.md](library-api.md): R-API-05 |
| `C-DEBUG-NONEMPTY` | Adopt: represent empty and redacted values explicitly; return useful nonempty diagnostics. | [library-api.md](library-api.md): R-API-05 |

## Future proofing — 4 rules

Source: [Future proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-SEALED` | Qualify: seal only traits that exclude downstream implementations by design. | [types-ownership.md](types-ownership.md): R-API-01 |
| `C-STRUCT-PRIVATE` | Qualify: keep invariant or implementation fields private; public passive records are deliberate API commitments. | [types-ownership.md](types-ownership.md): R-API-01 |
| `C-NEWTYPE-HIDE` | Qualify: expose a wrapper or suitable `impl Trait` contract instead of incidental concrete representation. | [library-api.md](library-api.md): R-API-06 |
| `C-STRUCT-BOUNDS` | Qualify: put bounds on relevant implementations; keep bounds required by fields, associated types, or `Drop`. | [library-api.md](library-api.md): R-API-06 |

## Necessities — 2 rules

Source: [Necessities](https://rust-lang.github.io/api-guidelines/necessities.html).

| ID | Treatment and original synthesis | Target |
| --- | --- | --- |
| `C-STABLE` | Qualify: review dependency types and implementations exposed in public APIs; assess compatibility and release policy explicitly. | [library-api.md](library-api.md): R-API-07 |
| `C-PERMISSIVE` | Not default: follow the owner's license and dependency policy. A license change requires an explicit project decision. | [library-api.md](library-api.md): R-API-07 |

