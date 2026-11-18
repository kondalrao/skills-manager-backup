# Types and ownership

Load for API, type, conversion, collection, or ownership work.

## R-TYPE-01 — Encode meaningful distinctions

**SHOULD.** Use a newtype when values share a representation but have different meanings, units, permissions, or invariants. A type alias gives another name to the same type; it does not prevent a mix-up. Use an enum for distinct states or an unclear Boolean parameter. Prefer named fields when positions are easy to confuse.

**Check:** A call with the wrong domain type fails to compile. State transitions cover valid and invalid cases. Use a simple type when no distinction needs enforcement. [API type safety](https://rust-lang.github.io/api-guidelines/type-safety.html), [newtypes](https://doc.rust-lang.org/rust-by-example/generics/new_types.html)

## R-TYPE-02 — Protect every construction path

**MUST.** For an invariant-bearing type, keep fields private to the module boundary that enforces the invariant. Validate public construction, parsing, conversion, deserialization, builder completion, and mutation. A database row is input unless a documented boundary guarantees the invariant.

**SHOULD.** Use `TryFrom` or a fallible constructor when validation can fail. Use `From` only when the conversion is infallible, semantically lossless, value-preserving, and has one clear meaning. Keep mutable access narrow enough to preserve validity. A business rule alone does not justify an `unsafe fn`.

Implement `From` or `TryFrom` rather than `Into` or `TryInto` when the standard blanket implementation supplies the reciprocal conversion.

**Check:** Test each path with valid, invalid, and boundary data. Derived `Deserialize` must not bypass validation. A `Default` implementation must produce a valid value. [TryFrom](https://doc.rust-lang.org/std/convert/trait.TryFrom.html), [From](https://doc.rust-lang.org/std/convert/trait.From.html), [Serde conversion attributes](https://serde.rs/container-attrs.html#try_from), [Rust soundness](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)

## R-TYPE-03 — Implement traits as contracts

**MUST.** Preserve the laws of `Eq`, `Hash`, and ordering. Implement `Borrow<T>` only when borrowed and owned values have equivalent equality, ordering, and hash behavior. Use `AsRef<T>` for a reference conversion without that equivalence. `Borrow` is a safe trait; unsafe code must not use a broken safe trait implementation as a reason for undefined behavior.

**SHOULD.** Derive traits when the derived semantics fit. For public library types, review useful standard traits before release. Add application traits when needed. Redact secrets in `Debug` and `Display`. Use `Deref` for pointer-like behavior; explicit accessors are clearer for most domain wrappers.

**Check:** Equal values hash equally. Round-trip and ordering properties hold. Exposed operations preserve the invariant. [Borrow](https://doc.rust-lang.org/std/borrow/trait.Borrow.html), [API interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html), [API predictability](https://rust-lang.github.io/api-guidelines/predictability.html)

## R-OWN-01 — Select ownership from the operation

**SHOULD.** Borrow for temporary access. Move a value when the operation transfers ownership. Clone when an independent value or simpler, acceptable lifetime is needed. State the cost when it matters. `Arc::clone` shares an allocation; it does not deep-copy its value.

**Check:** Review clone sites, lifetime constraints, and retained values. Use `Rc` for shared ownership on one thread and `Arc` when atomic shared ownership is needed. `Arc<T>` does not make an arbitrary `T` thread-safe. Break reference cycles when they would retain resources. [Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html), [ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html)

## R-OWN-02 — Accept the least restrictive useful input

**SHOULD.** Use `&str`, `&[T]`, and `&T` when the operation only needs their data. Use `&mut Vec<T>` when the operation changes vector structure. Take ownership when storage must outlive the caller's borrow. Store a borrow when its lifetime fits the type's contract. Consider `IntoIterator` for a reusable one-pass operation and slices for indexed access. Use `AsRef` or `Into` when caller benefit justifies generic code and inference cost.

**Check:** Test representative callers without extra copies. Return an iterator when deferred consumption helps. Return an owned collection when ownership, indexing, or the algorithm makes it the simpler contract. [API flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html)

For an ordinary function parameter typed `&str`, `&String` can use a deref coercion. Use `as_str()` when an explicit conversion improves clarity. Do not add a copy or change ownership only to resolve a generic inference error; first inspect the expected type and coercion site. [Type coercions](https://doc.rust-lang.org/reference/type-coercions.html#deref-coercions)

Return a result directly when that expresses the operation. Use an output parameter when intentional in-place mutation or buffer reuse is part of the contract.

## R-OWN-03 — Move values through valid states

**SHOULD.** Use pattern matching and operations such as `Option::take` or `mem::replace` to move a field while leaving a valid state. Keep exclusive borrows short. For a consuming linked-list merge, move nodes; a deep copy or shared mutable graph is not required.

**Check:** Test empty inputs, one empty input, equal keys, order, and preservation of all nodes or values. For long recursive structures, check operation and destructor stack use. Choose `Vec` or `VecDeque` for ordinary sequence storage unless linked-node behavior is required. [Option::take](https://doc.rust-lang.org/std/option/enum.Option.html#method.take), [collections](https://doc.rust-lang.org/std/collections/index.html)

## R-API-01 — Plan public API evolution

**MUST.** Review changes to public fields, variants, traits, bounds, features, `const` functions, and auto traits for compatibility. Dependency types in a signature bind users to that dependency's API. Expose them when that is intentional; wrap them when a stable domain boundary is needed.

**SHOULD.** Keep implementation fields private. Use `#[non_exhaustive]` when callers must permit future fields or variants. Use sealed traits only when downstream implementations are outside the intended contract. Use `#[must_use]` when ignoring a result is likely to be a mistake.

**Check:** Compile a downstream caller. Check migration needs and release notes. These attributes impose caller limits; do not add them mechanically. [Cargo SemVer](https://doc.rust-lang.org/cargo/reference/semver.html), [future proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html), [non_exhaustive](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute), [must_use](https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-must_use-attribute)

## R-OWN-04 — Select Copy and Clone from value semantics

**SHOULD.** Add `Copy` when implicit bitwise duplication fits the type's meaning and cost. Add `Clone` when an explicit duplicate is a supported operation. Derive them when field behavior matches the contract. A type's ability to derive a trait does not establish that the API should expose it.

**MUST.** Preserve unique-resource and exclusive-access contracts. `Copy` and `Drop` cannot be implemented on the same type. `Clone` can share an allocation or mutable state; it does not promise an independent deep copy. Copying a reference does not remove its lifetime constraints.

**Check:** Review the size and duplication meaning, including fixed arrays. Test whether a cloned handle shares or duplicates the resource. For public types, review the compatibility cost of later removing a trait. [Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html), [Clone](https://doc.rust-lang.org/std/clone/trait.Clone.html), [Drop](https://doc.rust-lang.org/std/ops/trait.Drop.html)

## R-OWN-05 — Give stored data a clear owner

**SHOULD.** Let a long-lived domain value own its independent data when that keeps the model simple. Use borrowed fields for a view, parser result, or other value whose lifetime is tied to existing storage. Select from the required lifetime, mutation, and allocation contract rather than a blanket preference.

**MAY.** Store typed IDs into a separately owned collection for a graph with independent mutation. Define identity, missing-target, deletion, and stale-ID behavior. An ID lookup adds a consistency duty; it is not a free replacement for references.

**Check:** The owner and required lifetime are explicit. Borrowed views compile for supported uses. Graph updates preserve referential rules. Avoid self-referential structures unless the design and required tools are justified. [Lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions)
