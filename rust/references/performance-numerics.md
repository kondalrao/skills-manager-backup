# Performance and numeric models

Load for speed, memory, allocation, numeric, unit, or time work.

## R-PERF-01 — Measure the required workload

**MUST.** Define the relevant target, input size, throughput, latency, memory, and correctness limits before an optimization claim. Compare before and after under the same conditions. Keep enough build information to repeat the result.

**SHOULD.** Profile the costly path. Use a release-like build and an appropriate benchmark. Include tail latency or peak memory when the service contract depends on it.

**Check:** The result meets the stated budget without a behavior regression. An allocator, CPU setting, or dispatch preference is a candidate for measurement, not a guaranteed improvement. [rustc code generation](https://doc.rust-lang.org/rustc/codegen-options/index.html), [Criterion](https://bheisler.github.io/criterion.rs/book/)

## R-PERF-02 — Match allocation to the lifetime

**SHOULD.** Reserve capacity when a useful bound is known. Reuse buffers when ownership and isolation permit it. Consider `Box<[T]>` or `Box<str>` for fixed-length owned data. Consider shrinking a long-lived overallocated collection after construction when saved memory exceeds the cost.

**MUST.** Do not assume a fixed `Vec` growth factor. `shrink_to_fit` does not promise exact capacity. A boxed slice has a fixed length, but its elements can still be mutable. Do not reserve untrusted sizes without a resource limit.

**Check:** Measure allocation count, retained capacity, peak memory, and reuse behavior when they decide the change. Shrinking a buffer just before it grows again can add work. String concatenation can reuse an existing buffer; formatting syntax alone does not establish fewer allocations. [Vec guarantees](https://doc.rust-lang.org/std/vec/struct.Vec.html#guarantees), [Vec shrink_to_fit](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.shrink_to_fit), [String addition](https://doc.rust-lang.org/std/string/struct.String.html#impl-Add%3C%26str%3E-for-String)

## R-PERF-03 — Keep deployment choices explicit

**MUST.** Preserve collision-attack resistance when keys can be attacker-controlled. Verify every deployment CPU supports selected code generation. Choose a global allocator only at a suitable application boundary with platform, correctness, and performance checks.

**MAY.** Use another hasher, allocator, batching design, or indirection layout when the workload supports it. For large async state machines, measure future size and stack pressure before boxing.

**Check:** Include hostile-key behavior, supported CPUs, allocation ownership across FFI, and deployment configuration where relevant. Do not set `target-cpu=native` for portable distributed binaries without a fleet contract. [HashMap hasher policy](https://doc.rust-lang.org/std/collections/struct.HashMap.html), [target-cpu](https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu), [global allocator](https://doc.rust-lang.org/std/alloc/index.html)

## R-PERF-04 — Account for telemetry cost

**SHOULD.** Use stable event names and structured fields. Defer expensive field construction when the level is disabled. Redact private data and bound payload size. Use the backend's actual formatting and export contract.

**Check:** Inspect disabled-level overhead on costly paths. `format!` creates a `String`; `format_args!` does not require a heap allocation. Formatting inside a logging macro is not automatically an allocation. [tracing events](https://docs.rs/tracing/latest/tracing/#recording-events), [format_args](https://doc.rust-lang.org/std/macro.format_args.html)

## R-NUM-01 — Define the representation and valid range

**MUST.** State units, scale, range, rounding, overflow, and invalid-value policy. A floating wrapper must handle NaN and infinities when they are outside the domain. For equality or total order, include signed zero and trait-law checks as needed.

**SHOULD.** Use distinct types or marker parameters for values that must not mix. Use a runtime enum when the scale is selected at runtime. A zero-sized marker does not establish the layout of every enclosing type.

For a public bit-oriented numeric type, offer binary, octal, or hexadecimal formatting when callers need those views. Keep the representation and formatting contract clear.

**Check:** Test endpoints, normalization, overflow, and conversion round trips with stated tolerance. In floating-point terminology, `[0, 1)` is not the subnormal range; `0.5` is normal. [f64](https://doc.rust-lang.org/std/primitive.f64.html), [PhantomData layout](https://doc.rust-lang.org/std/marker/struct.PhantomData.html#layout), [Eq](https://doc.rust-lang.org/std/cmp/trait.Eq.html), [Ord](https://doc.rust-lang.org/std/cmp/trait.Ord.html)

## R-NUM-02 — Separate time meaning from storage precision

**MUST.** For domain time conversions, define epoch, unit, time scale, leap-second policy, range, and required external data. Pass providers explicitly when conversion needs observations. Return a failure for unavailable or out-of-range data unless an approximation is part of the contract.

**MUST.** State representation resolution separately from numerical and physical-model accuracy. Verify claimed accuracy against reference values across the required range. A count of stored fractional digits is insufficient.

**SHOULD.** Use `Instant` for ordinary elapsed time and the project's wall-clock type for timestamps. Add astronomical time types only when the domain needs them. Keep generic Rust models separate from a concrete Python interface when PyO3 restrictions require it.

**Check:** Cover provider gaps, stale data, boundaries, and documented tolerances. The Lox talk is a design case; current Lox uses a different subsecond representation. [Instant](https://doc.rust-lang.org/std/time/struct.Instant.html), [pinned Lox Time](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/crates/lox-time/src/time.rs), [pinned Lox Subsecond](https://github.com/lox-space/lox/blob/aba22ff7b6e7bd82f5c1088c7da45b74ca0362b0/crates/lox-time/src/subsecond.rs), [PyO3 restrictions](https://pyo3.rs/main/class.html#restrictions)
