# Errors and panics

Load when an operation can fail or a boundary reports failure.

## R-ERR-01 — Select the failure contract

**MUST.** Use `Option` for an expected absence when more detail gives no useful action. Use `Result` when the caller needs a failure reason. Reserve a panic for a documented broken program invariant or an explicit panicking API. Invalid external input is normally a `Result` case.

**Check:** Test absent, invalid, and failed I/O cases. They must not reach an incidental `unwrap`, index panic, or assertion. Use pattern matching when it proves the case directly. An `expect` message must explain why the invariant should hold. [Result](https://doc.rust-lang.org/std/result/), [Option](https://doc.rust-lang.org/std/option/), [panic](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)

## R-ERR-02 — Design for caller decisions

**SHOULD.** Expose typed errors at a reusable boundary when callers need to match failure categories. Use an enum for a useful closed set, or an opaque struct with a stable kind or accessor when evolution needs it. Application orchestration MAY use `anyhow`, `eyre`, or a similar report type.

**MUST.** For reusable error types intended for standard diagnostic tools, implement `std::error::Error` with its `Debug` and `Display` requirements. Preserve a causal error through `source()` when the cause implements `Error + 'static`. If a borrowed cause cannot meet that bound, keep useful cause data in the typed API and document the reporting limit. Keep credentials and sensitive data out of messages.

For a suitable `no_std` library, use `core::error::Error` when its MSRV supports it; it is available from Rust 1.81. For a kernel API, follow the [kernel profile](kernel-profile.md) and its native error types. Thread bounds such as `Send` and `Sync` are caller requirements, not supertraits of `Error`. [Core Error](https://doc.rust-lang.org/core/error/trait.Error.html)

**Check:** A caller can select the intended action without parsing prose. Public signatures do not force an incidental reporting crate on consumers. A struct with a backtrace is an option, not a Rust requirement. [Error](https://doc.rust-lang.org/std/error/trait.Error.html), [thiserror](https://docs.rs/thiserror/latest/thiserror/), [anyhow](https://docs.rs/anyhow/latest/anyhow/)

## R-ERR-03 — Add context without losing meaning

**SHOULD.** Propagate with `?`. Implement `From` when one context-free conversion is canonical. Use `map_err` or a context method when the operation needs local data or a different category. Keep retry, not-found, timeout, and permission cases distinct when callers act on them.

**Check:** Tests inspect variants, kinds, and sources. Do not map a storage outage to a missing record or a success default. Avoid conversions that discard the only actionable cause. [From](https://doc.rust-lang.org/std/convert/trait.From.html), [anyhow context](https://docs.rs/anyhow/latest/anyhow/trait.Context.html)

## R-ERR-04 — Put reporting at an accountable boundary

**SHOULD.** Report a failure once at the layer that owns the user response or operation result. Add structured fields at lower layers when they add distinct operational evidence. A library should use its telemetry interface, not write incidental output to stdout. A CLI can use stdout for its intended output and stderr for diagnostics.

**Check:** One failed request produces useful context without repeated full reports or secret values. Backtrace capture and visibility are verified in the deployed configuration. A backtrace is not guaranteed by choosing an error crate. [anyhow backtraces](https://docs.rs/anyhow/latest/anyhow/#details), [tracing](https://docs.rs/tracing/latest/tracing/)

## R-ERR-05 — Treat panic containment as a separate design

**MUST.** Do not use `catch_unwind` as routine error propagation. It catches unwinding panics only. For a justified containment boundary, specify panic strategy, state validity, cleanup, and restart or failure behavior. Use the ABI contract at FFI boundaries.

**Check:** Panic and abort cases have an explicit policy. A successful catch does not establish that shared state is valid. Never rely on a catch to intercept `panic=abort`. See [Unsafe and FFI](unsafe-ffi.md). [catch_unwind](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html)
