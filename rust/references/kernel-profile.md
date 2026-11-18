# Linux kernel Rust profile

Load for work inside a Linux kernel tree or on a Rust kernel module. This profile selects project-specific rules. It does not apply to an ordinary userspace crate. Read the target tree's documentation before using a live website's API examples.

Identify the compilation target. Runtime restrictions below apply to code compiled into the kernel or its modules. Host tools, build tools, and procedural macros can use `std` and host error types under their own target contracts. They still use the owning tree's build and contribution workflow.

## R-KERN-01 — Establish the target tree

**MUST.** Record the kernel revision, subsystem, architecture, build directory, configuration, and toolchain. Use that tree's Kbuild, Kconfig, and `Documentation/rust/` instructions. Keep required `ARCH`, `O=`, and tool overrides consistent between configuration, build, and checks.

**Check:** Rust is available for the selected configuration and target. `rustavailable` checks tools; it does not itself enable `CONFIG_RUST`. Cargo checks do not replace the kernel build. [Quick Start](https://docs.kernel.org/rust/quick-start.html), [architecture support](https://docs.kernel.org/rust/arch-support.html), [LLVM build](https://docs.kernel.org/kbuild/llvm.html)

## R-KERN-02 — Follow the kernel source conventions

**SHOULD.** Use the tree's default formatter and vertical import convention. Preserve the documented trailing `//` import marker where needed. Keep C concepts recognizable while using Rust names and avoiding repeated prefixes.

**MUST.** Review Markdown comments and rustdoc separately. Use a summary sentence and the relevant safety, panic, example, and item links. Keep implementation notes separate from API documentation, including for private items.

**Check:** Run `rustfmtcheck` and inspect manual conventions. [Kernel coding guidelines](https://docs.kernel.org/rust/coding-guidelines.html)

## R-KERN-03 — Explain each unsafe use

**MUST.** Put a `// SAFETY:` explanation before each unsafe block. State caller or implementor duties in the API's `# Safety` section. Verify initialization, ownership, lifetime, aliasing, concurrency, and destruction duties that the selected API requires. General Rust soundness still applies across the C boundary.

**Check:** Each use meets its actual target-tree contract. A debug-only precondition assertion does not replace the proof; the reviewed helper can be a no-op without `CONFIG_RUST_DEBUG_ASSERTIONS`. [Kernel comments](https://docs.kernel.org/rust/coding-guidelines.html#comments), [safety helper source](https://rust.docs.kernel.org/src/kernel/safety.rs.html), [Rust soundness](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)

## R-KERN-04 — Use the kernel abstraction boundary

**MUST.** For code compiled into the kernel or its modules, use the kernel's `no_std` environment, `core`, and reviewed kernel APIs. Leaf drivers use the kernel abstractions rather than bypass them through raw C bindings. Extend the abstraction when needed. Use kernel-prelude C aliases such as `c_int` and `c_char` under the kernel convention.

**Check:** Read the chosen lock, allocation, pinning, callback, or workqueue API in the target tree. A similar `std` name does not establish its contract. Kernel-prelude C aliases are a kernel rule; userspace APIs can use `core::ffi` as appropriate. [General information](https://docs.kernel.org/rust/general-information.html), [C FFI types](https://docs.kernel.org/rust/coding-guidelines.html#c-ffi-types), [kernel prelude](https://rust.docs.kernel.org/kernel/prelude/index.html)

## R-KERN-05 — Use kernel failure and lint policy

**MUST.** For kernel runtime code, use the target tree's kernel error types and propagation conventions. Avoid panicking operations for reachable failures. The kernel's panic consequences require a stricter policy than a normal application. Do not add an application reporting crate by default. Host tools and procedural macros use their documented error contracts.

**SHOULD.** Keep lint exceptions local. Use `expect` where the warning is expected in all relevant builds; use a justified `allow` when configuration, architecture, or macro use makes that expectation unsuitable.

**Check:** Failure paths return the intended kernel error. Check relevant configurations before requiring a lint expectation. [Kernel Result](https://rust.docs.kernel.org/kernel/error/type.Result.html#error-codes-in-c-and-rust), [kernel lints](https://docs.kernel.org/rust/coding-guidelines.html#lints)

## R-KERN-06 — Use kernel checks and report their scope

**MUST.** Select checks from the target tree and changed behavior. These are command templates, not results from this review. Keep the selected build context and overrides.

| Purpose | Documented command | Limit |
| --- | --- | --- |
| Tool availability | `make LLVM=1 rustavailable` | Target support and configuration still need checks. |
| Build | `make LLVM=1` | Needs valid configuration, Rust support, and required tools. |
| Format check | `make LLVM=1 rustfmtcheck` | Does not need a kernel configuration. |
| Clippy analysis | `make LLVM=1 CLIPPY=1` | Analysis build; do not deliver it as the production kernel. |
| API documentation | `make LLVM=1 rustdoc` | Documentation follows the build configuration. |
| Host Rust tests | `make LLVM=1 rusttest` | Needs configuration; does not execute a driver in its target kernel. |

**SHOULD.** Use the target tree's KUnit, doctest, and Rust selftest instructions where applicable. Test configuration and runtime context are part of the result. Preserve existing configuration before a test setup changes it.

**Check:** Report revision, target, configuration, command, and outcome. Clippy can change code generation. Host tests, KUnit tests, and selftests establish different evidence. Do not run a kernel installation, boot, or device test merely because this reference lists it. [General information](https://docs.kernel.org/rust/general-information.html), [Rust testing](https://docs.kernel.org/rust/testing.html)

## Version limit

The live documentation can differ from the target kernel. Reviewed generated API pages reported v7.4-rc2; the main documentation site had no version label. This identifies the read, not a supported minimum. No kernel build, boot, or runtime test was run for this set.
