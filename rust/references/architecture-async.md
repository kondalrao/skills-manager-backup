# Architecture, concurrency, and async

Load for service boundaries, adapters, tasks, traits, locks, or async APIs.

## R-ARCH-01 — Keep policy separate from external mechanisms

**SHOULD.** Keep domain rules independent of HTTP handlers, database rows, and transport status codes when these mechanisms change independently. Put translation in adapters. A port is a contract required by a use case. It is not a reason to wrap every function.

**MAY.** Use a hexagonal design when replaceable I/O, several entry points, or isolated domain tests justify it. Start with modules. Split crates when a dependency or release boundary needs enforcement.

**Check:** Domain tests run without a network service. Adapters map errors and values explicitly. For a small tool, one package can meet the same need. [Original ports and adapters model](https://alistair.cockburn.us/hexagonal-architecture), [API flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html)

## R-ARCH-02 — Choose dispatch from the boundary

**SHOULD.** Use a concrete type for a fixed dependency. Use a generic bound for static substitution. Use `dyn Trait` for runtime selection, heterogeneous values, or a useful reduction in generic code. A trait needs a real contract; tests alone do not require dynamic dispatch.

**MUST.** Check dyn compatibility before promising a trait object. An associated function or generic method with `where Self: Sized` can be excluded from dispatch; simplified blanket bans are inaccurate.

**Check:** A small consumer compiles with the selected dispatch and lifetime bounds. Measure code size or speed when that decides the choice. [Trait dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility)

## R-ASYNC-01 — State runtime and future contracts

**MUST.** Identify the executor, runtime I/O types, task lifetime, and cancellation behavior. Add `Send` and `'static` only where a boundary needs them. A future's `Send` property depends on its captured state, including state held across suspension; its output type alone does not decide it. A shared reference `&T` is `Send` when `T: Sync`.

**SHOULD.** Use `async fn` for a simple async operation. Use a returned future or another explicit form when the API needs bounds or work before the future is created. For public traits, check how callers can require a `Send` future on the supported compiler.

**Check:** Compile representative spawn and local-executor callers. Include non-`Send` state where supported. Choose runtime abstraction only when the library needs more than one runtime. [Async functions](https://doc.rust-lang.org/reference/items/functions.html#async-functions), [Send](https://doc.rust-lang.org/std/marker/trait.Send.html), [Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html), [async in public traits](https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/)

## R-ASYNC-02 — Keep executor work bounded

**SHOULD.** Keep blocking I/O and long CPU work outside an executor worker when they can delay unrelated tasks. Use the runtime's supported blocking facility or a bounded worker design. Bound task counts and queues. Define shutdown, timeout, and partial-completion behavior.

**Check:** Test queue limits, cancellation, and shutdown under load. Check whether a timeout cancels only the wait or also the underlying operation. CPU loops need a scheduling plan; an `.await` is not proof of a yield. [Tokio blocking work](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html), [Tokio task behavior](https://docs.rs/tokio/latest/tokio/task/)

## R-SYNC-01 — Protect state with a clear lock contract

**MUST.** Define the protected invariant and lock order. Keep critical sections limited. Check every guard held across `.await`; use a suitable async lock only when the operation requires it. Atomic reference counting does not protect mutation of the value.

**SHOULD.** Inject mutable process state when independent instances or isolated tests need it. Immutable constants and justified process-wide state can remain global.

**Check:** Test concurrent operations and error paths. A poisoned standard mutex signals possible invalid state. Recovery needs a documented repair or validity argument; `into_inner()` alone is not repair. Poisoning is advisory and cannot establish memory safety. [Mutex poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning), [Tokio mutex selection](https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html#which-kind-of-mutex-should-you-use)

## R-ARCH-03 — Test the boundary as well as the domain

**MUST.** Pair domain tests with adapter tests for the contract that an external service actually provides. A fake repository is not evidence for a SQL query, transaction, network protocol, or runtime behavior.

**Check:** Cover not-found, conflict, outage, timeout, retry safety, and partial writes when they apply. Verify that error translation preserves caller action. This is the selected verification policy; the tutorial alone does not establish it.
