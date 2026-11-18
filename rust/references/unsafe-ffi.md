# Unsafe code and FFI

Load for unsafe blocks, unsafe APIs, raw pointers, native libraries, or an FFI boundary.

## R-SAFE-01 — State the soundness argument

**MUST.** Use safe Rust when it meets the contract. For required unsafe code, state the operation that needs it and the proof obligations. Review validity, initialization, bounds, alignment, provenance, aliasing, lifetimes, ownership, and concurrency as applicable. Unsafe code must remain correct for every permitted safe caller.

**SHOULD.** Keep the unsafe region small. Put a local `SAFETY:` comment next to each operation to explain how that operation's preconditions hold. Put caller obligations in a `# Safety` section on an unsafe public API. A comment that only says the operation is safe is insufficient.

**Check:** Review against the Rust Reference and the owning API. For a performance reason, provide a safe baseline and target measurements. The Unsafe Code Guidelines reference says it is largely abandoned; do not treat it as the sole current authority. [Undefined behavior and soundness](https://doc.rust-lang.org/reference/behavior-considered-undefined.html), [safe and unsafe](https://doc.rust-lang.org/nomicon/safe-unsafe-meaning.html), [UCG status](https://rust-lang.github.io/unsafe-code-guidelines/)

## R-SAFE-02 — Keep logic invariants separate from safety preconditions

**MUST.** Use `unsafe` only when the caller must uphold a condition needed to prevent undefined behavior. A malformed email address, an ordinary out-of-range domain number, or a broken safe comparison trait does not by itself make an unsafe API appropriate.

**Check:** Name the undefined behavior that a violated precondition can cause. If the issue is only a business error, use checked construction or a restricted safe internal path. If unsafe internals depend on a domain invariant for memory safety, all safe construction and mutation must enforce that invariant. [Rust soundness](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)

## R-FFI-01 — Define the complete boundary

**MUST.** Specify ABI, representation, string encoding, buffer length, null handling, lifetime, ownership transfer, release function, thread use, and error behavior. Use a supported FFI representation. A one-field Rust struct alone does not guarantee the inner ABI. Use `#[repr(transparent)]` or `#[repr(C)]` only when its documented rules meet the need.

**SHOULD.** Keep native declarations and translation separate from domain rules. A `-sys` crate can contain raw bindings and a safe wrapper can enforce contracts. Document required native tools and libraries rather than promise dependency-free builds.

**Check:** Test layout where useful and test a real foreign caller. A size assertion on one target does not replace a representation guarantee. Test invalid inputs that the public foreign contract requires the wrapper to reject. [Rust layout](https://doc.rust-lang.org/reference/type-layout.html), [Nomicon FFI](https://doc.rust-lang.org/nomicon/ffi.html)

## R-FFI-02 — Control unwinding and library state

**MUST.** Specify what happens when Rust panics or foreign code throws. Use the correct unwind or non-unwind ABI. Do not assume `catch_unwind` catches aborts or foreign exceptions. Define which library allocates and frees each resource. Do not transfer Rust runtime objects between separately linked libraries without an explicit supported contract.

**Check:** Test error and shutdown paths. Review allocator pairing, callback lifetime, library unload, duplicated global state, and version skew. For separate DLLs, process identity alone does not establish shared Rust state. [FFI and unwinding](https://doc.rust-lang.org/nomicon/ffi.html#ffi-and-unwinding), [catch_unwind](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html)

## R-SAFE-03 — Test adversarial safe use

**MUST.** Review zero-sized types, empty and maximum lengths, panic during partial work, repeated calls, destructor behavior, and permitted concurrent use when they apply. Include unusual safe trait implementations when the abstraction depends on client traits.

An `unsafe impl Send` or `Sync` needs a valid thread-safety argument for the type. Do not add one only to make a spawn call compile.

**SHOULD.** Run Miri on relevant supported tests and use sanitizers or native integration checks where they add coverage.

**Check:** State which configurations and paths were tested. Passing dynamic checks does not prove soundness. Unsupported FFI or platform paths need separate evidence. [Miri limits](https://github.com/rust-lang/miri)
