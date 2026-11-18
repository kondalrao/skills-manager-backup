# Reusable library APIs

Load when a crate exposes an API to other projects. Also read [Types and ownership](types-ownership.md). The Rust API Guidelines are design advice. Apply each rule when its operation belongs in the public contract.

## R-API-02 — Use predictable operation families

**SHOULD.** Use standard trait and method meanings. Use `as_` for a cheap conversion or view that keeps the source available, `to_` for a conversion with potential cost, and `into_` for a consuming conversion. Follow the receiver and result conventions of the operation. Use `new` for an ordinary inherent constructor. Use a method when the operation has a clear receiver.

**SHOULD.** Give iterator methods the expected ownership forms: `iter`, `iter_mut`, and `into_iter` when they apply. Give exposed iterator types names that match their methods. Use clear, consistent word order and capability-based feature names. A getter normally uses the field name without `get_`; a mutable accessor uses `field_mut`.

**Check:** A downstream caller can predict ownership, mutation, and cost. Provide expected pairs such as `len` and `is_empty`. A conversion or constructor name must retain its domain meaning. [API naming](https://rust-lang.github.io/api-guidelines/naming.html), [predictability](https://rust-lang.github.io/api-guidelines/predictability.html)

For a generic smart pointer, prefer associated functions when inherent methods could collide with methods of the target. Operator implementations must preserve the expected domain meaning and laws.

## R-API-03 — Integrate collections and I/O with standard traits

**SHOULD.** For a public collection, implement the useful `IntoIterator`, `FromIterator`, and `Extend` forms. Offer borrowed and mutable iteration when the collection supports them. Report truthful iterator bounds and properties.

**SHOULD.** For a generic synchronous I/O operation, accept `R: Read` or `W: Write` by value when that lets callers pass either an owned stream or a mutable reference. Choose runtime-compatible async traits separately. Expose a useful intermediate result when it prevents callers from repeating substantial work.

**Check:** Compile representative owned and borrowed consumers. Test collection construction and extension against independent expected values. A library need not provide an iterator form that its data model cannot support. [API interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html), [flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html)

## R-API-04 — Make configuration and flags explicit

**SHOULD.** Use a builder when several optional settings or cross-field constraints make direct construction hard to use correctly. Keep required data clear. Validate the complete configuration before returning the usable value. Add `Default` only when a meaningful valid default exists.

Choose consuming or borrowed builder methods from ownership transfer and whether callers need to reuse the configuration.

**MAY.** Use a flag-set type for independent combinable flags. Use an enum for mutually exclusive choices. Add a flag dependency only when its API and maintenance benefit justify it.

**Check:** Cover omitted required values, conflicting settings, defaults, and order-independent builder calls where promised. The compiler or final build step rejects invalid states. [API type safety](https://rust-lang.github.io/api-guidelines/type-safety.html), [validation](https://rust-lang.github.io/api-guidelines/dependability.html)

## R-API-05 — Provide useful diagnostics and serialization contracts

**SHOULD.** Give public types a useful `Debug` view. Use redacted field values for secrets; an empty debug representation gives little help. Add `Display` for meaningful user text rather than internal structure. Review common traits against the value contract in [Types and ownership](types-ownership.md).

**SHOULD.** Offer Serde support when consumers need it, with the project's feature and version policy. Preserve validated construction during deserialization. Serialization support is a compatibility promise; it is not required for every handle, secret, or runtime object.

**Check:** Test diagnostic redaction and important serialization round trips. Confirm the selected Serde version and feature behavior. Do not copy old feature syntax without checking whether it activates an optional dependency. [API debuggability](https://rust-lang.github.io/api-guidelines/debuggability.html), [interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html), [Cargo dependency features](https://doc.rust-lang.org/cargo/reference/features.html#dependency-features)

## R-API-06 — Keep extension and representation choices open

**SHOULD.** Put conversions on the most specific type that owns their meaning. Keep implementation fields private when callers do not need direct representation access. Add trait bounds to the operations that require them; add bounds to a type definition when the stored representation or invariant requires them.

**MUST.** Decide whether consumers can implement a public trait and whether they need a trait object. Check current dyn-compatibility rules for the supported compiler. Review the release effect of fields, bounds, sealing, and return types under R-API-01.

**Check:** Compile an external consumer with a supported minimal type. It must not need an unrelated trait only because one method uses it. Do not replace a useful typed API with a more complex generic API without a caller need. [API future proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html), [dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility)

A newtype or a suitable `impl Trait` return can hide an incidental representation. Choose the exposed bounds and lifetime captures deliberately; hiding the concrete name does not remove compatibility duties.

## R-LIFE-01 — Make cleanup dependable

**SHOULD.** Keep destructors free of panic and avoid blocking work in implicit cleanup. Provide an explicit `close`, `finish`, or equivalent operation when callers must observe a failure or control a costly completion step. Keep a safe fallback cleanup path for unfinished values.

**MUST.** Keep unsafe code sound even when safe code does not run a destructor. Destructors can be skipped; release behavior is not a substitute for a memory safety contract.

**Check:** Test explicit completion, early return, and partial failure. State whether failure leaves the value usable or consumes it. Avoid a second panic during unwinding. [API dependability](https://rust-lang.github.io/api-guidelines/dependability.html), [destructor limits](https://doc.rust-lang.org/reference/destructors.html#not-running-destructors)

## R-API-07 — Publish the supported contract

**MUST.** Document supported versions, features, targets, important examples, failures, and release changes. Public dependency types must have a deliberate version policy. Stable library claims need a defined compatibility policy, not just a successful build.

**SHOULD.** Check package description, repository, documentation, categories, keywords, and license metadata as appropriate to publication. Preserve the owner's license policy. Do not impose a permissive license or add personal email addresses because an older checklist recommends them. Current Cargo documentation deprecates `authors`.

**Check:** Build documentation and a downstream consumer. Check package contents and registry requirements. Use the project's license review process for dependency changes. [API documentation](https://rust-lang.github.io/api-guidelines/documentation.html), [necessities](https://rust-lang.github.io/api-guidelines/necessities.html), [Cargo metadata](https://doc.rust-lang.org/cargo/reference/manifest.html)
