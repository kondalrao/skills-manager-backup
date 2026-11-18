# Subagent coordination

Read before delegating a Rust task. Use the available subagent tools within the current task's scope. The main agent remains responsible for the completed result.

## Select the split

Use the smallest useful team. Split by an independent question, component, or check. Establish shared interfaces before dependent implementation. Parallel execution is useful only when the work can proceed without competing edits or unresolved input from another task.

| Work | Useful assignment | Boundary |
| --- | --- | --- |
| Unclear code path or version-specific contract | Read-only researcher | Answer named questions from the owning source and report evidence and limits. |
| Separate components with agreed interfaces | Implementation workers | Give each worker exclusive write ownership of named files or modules. |
| Unsafe abstraction, FFI contract, macro export, or public async/trait change | Independent reviewer | Review the relevant diff, callers, safety argument, and matching Rust rules. Keep review read-only. |
| Integrated behavior or build checks | Verification worker | Run agreed checks on the integrated state; report commands, configuration, and results. |

For a local borrow fix or a question with one clear source, work directly. Avoid dividing a short sequential task merely to create a team. For a multi-component change, use independent workers when their interfaces and file ownership are clear.

## Keep shared contracts with the main agent

The main agent owns scope, dependency order, and integration. Coordinate changes to public signatures, trait bounds, error categories, feature names, MSRV, edition, shared manifests, and lockfiles through one owner. Workers can propose these changes; dependent work waits until the updated contract is known.

Use shared-workspace editing only with clear, non-overlapping ownership. If edits must overlap, sequence them or use isolated worktrees and integrate deliberately. Tests and generated files also need owners. Never resolve a collision by discarding another worker's changes.

An independent reviewer should use a fresh context when available. Give it the requirement, relevant artifacts, and review scope. Keep the intended answer or suspected defect out of the brief unless needed for the actual review. The author remains available to explain context after the initial review.

## Send a complete brief

Each assignment needs:

- The required result and its acceptance criteria.
- Repository and working paths, relevant base revision or file state, and applicable instructions or continuity.
- Read-only or write scope; exact owned files or modules for an implementation task.
- Shared interfaces, dependencies, and work that must finish first.
- Only the matching Rust references, toolchain, target, feature, and runtime information needed for that task.
- Required checks and the permitted side effects. State that other workers are present, unrelated edits must be preserved, and a shared-contract change must return to the main agent.
- A return contract: findings or changed paths, evidence, commands and results, unresolved issues, and the next dependency to release.

Keep dispatch and integration with the main agent unless it explicitly assigns a worker to manage a further split. If a worker needs more context or cannot finish, narrow or reassign the work. Treat partial output as partial work, not completion.

## Coordinate Rust checks

Workers can run targeted checks for their owned changes. Assign one owner for a combined Cargo feature/MSRV matrix or kernel build. Avoid concurrent commands that can rewrite the same lockfile, generate the same files, or mutate shared build configuration. Use an isolated build area when it is needed and supported by the project.

Retain the build profile: a host fixture is not a kernel test, an installed compiler is not an MSRV pass, and a compile check is not a runtime result. Use [Verification](verification.md) and the matching [kernel profile](kernel-profile.md). A delegated check has the same evidence requirements as a local check.

## Integrate and close

Review each returned result against its assigned scope. Inspect changes and decisive evidence before accepting a completion claim. Resolve conflicting findings against the owning code or contract. Recheck a review or test result when later edits affect what it covered.

Integrate dependent work in order. Run the relevant final checks on the combined state; individual worker passes do not establish that the combined change works. Resolve actionable findings or report the exact remaining limit. The main agent gives the final behavior, verification, exceptions, and open-risk report. Do not end with only a list of delegated tasks.
