# Verification and release checks

Load when selecting tests or changing Cargo, features, or a public API.

Select the build profile first. The Cargo commands below are for Cargo projects. In a Linux kernel tree, use the [kernel profile](kernel-profile.md) and the target tree's build instructions.

## R-VER-01 — Prove the required behavior

**MUST.** Select tests from the contract and risk. Test valid behavior, boundary cases, and meaningful failures. Assert the business rule or invariant. A test that repeats a constant from the implementation gives little evidence. Use property tests for algebraic laws or a large input space when they add value.

**Check:** Explain what defect each important test can detect. Preserve an independent expected result or oracle. [Rust testing](https://doc.rust-lang.org/book/ch11-00-testing.html)

## R-VER-02 — Use the repository checks first

**MUST.** Run the documented formatter, lint, build, and test tasks that apply to the change. For a Cargo project with no stronger policy, use this starting set. Adapt it to the package and target; these commands are templates.

```sh
cargo fmt --all -- --check
cargo check --workspace --all-targets
cargo clippy --workspace --all-targets
cargo test --workspace
cargo test --workspace --doc
cargo doc --workspace --no-deps
```

`cargo test --workspace` normally includes library doctests. The explicit doc command makes their status visible. `--all-targets` is not a replacement for doctests. A cross-target check does not execute tests on that target.

**SHOULD.** Enforce warnings according to the pinned toolchain and CI policy. Use narrow lint exceptions with reasons. Prefer `#[expect(...)]` when the supported compiler and intended lint behavior permit it; it can detect an exception that is no longer needed. Do not enable every Clippy restriction lint as a bundle.

**Check:** Record command, toolchain, selected packages, features, target, and result. [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html), [Clippy usage](https://doc.rust-lang.org/clippy/usage.html), [lint attributes](https://doc.rust-lang.org/reference/attributes/diagnostics.html#lint-check-attributes)

## R-VER-03 — Test supported feature and toolchain states

**MUST.** Test the declared MSRV and supported targets with their supported feature sets. Features are unified across dependencies. Keep ordinary optional capabilities additive. A feature that disables validation or certificate checks can affect a consumer through unification; a test-only name does not make it isolated.

**SHOULD.** Check default features, minimal supported features, and important combinations. Use `--all-features` only when that combination is supported. Keep incompatible platform backends in separate checks. Share workspace settings through Cargo inheritance when it reduces drift. Set the resolver explicitly in a virtual workspace.

**Check:** Inspect actual resolved features and optional dependencies. State unsupported combinations. A latest-toolchain build is not an MSRV test. [Cargo features](https://doc.rust-lang.org/cargo/reference/features.html), [Cargo MSRV](https://doc.rust-lang.org/cargo/reference/rust-version.html), [workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)

## R-VER-04 — Match tools to the risk

**SHOULD.** Use downstream compile checks for public APIs and macros. Add compile-fail tests for type restrictions. Run Miri on relevant supported tests for unsafe code. Use fuzzing for untrusted parsers or complex state transitions when appropriate. Use integration tests under `tests/` for external Cargo consumers.

**MUST.** State tool limits. Passing Miri tests covers executed paths on supported configurations. It is not a soundness proof. A `compile_fail` doctest can pass for an unintended compiler error; inspect why it fails.

**Check:** Report the tested paths and failures. Use the repository security and dependency checks when dependencies change. Tools such as `cargo-audit` are optional additions, not compiler guarantees. [Miri](https://github.com/rust-lang/miri), [rustdoc tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html), [Cargo layout](https://doc.rust-lang.org/cargo/guide/project-layout.html)

## R-VER-05 — Review release behavior

**MUST.** For a release change, inspect public API compatibility, platform and native build requirements, dependency features, licensing policy, and package contents. Document target limits rather than claim all platforms work. Check native linking and clean-environment builds when they apply.

**Check:** Use the project's release procedure. `cargo package` and a downstream build can expose omitted files and undeclared assumptions. Preserve the established lockfile policy. [Cargo SemVer](https://doc.rust-lang.org/cargo/reference/semver.html), [cargo package](https://doc.rust-lang.org/cargo/commands/cargo-package.html)

