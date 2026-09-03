---
name: idea-refinery-implement
description: Execute an implementation-ready Spec Kit feature with dependency-safe parallel subagents, recorded test-driven development, independent review, bounded convergence, and fresh completion evidence. Use only when explicitly invoked as $idea-refinery-implement.
---
<!-- Generated from idea-refinery-implement/SKILL.md; do not edit this copy. -->

# Idea Refinery Implement

Implement the active feature produced by `$idea-refinery-full`. Preserve the refinement skill's handoff boundary: this skill may change application code, tests, `tasks.md`, and its own implementation state, but it does not change approved product scope or architecture.

Read [the orchestration contract](references/orchestration-contract.md) before dispatching any worker. Create or resume `implementation-state.md` from [the state template](references/implementation-state-template.md) in the active feature directory.

## Authorization boundary

Invoking this skill authorizes the controller to finish every approved, routine gate required by the active `tasks.md` and its approved convergence tasks: scheduling, implementation, objective in-scope review remediation, task promotion, state recording, convergence, hooks, and final verification. Do not ask the user again merely because the next routine gate is ready. It does not authorize dependency upgrades outside the plan, destructive cleanup, commits, pushes, pull requests, merges, deployments, or edits that resolve a material product or architecture decision.

Preserve unrelated user changes. Never assign a worker an uncommitted path unless the change is part of the active feature and the controller has inspected it. Ask before creating worktrees or changing repository/branch structure. If a protected output path or validator prerequisite needs authority that this invocation does not grant, ask once per normalized path or prerequisite category during preflight, record the request, and do not repeat it on resume.

## Component routing

At invocation, inspect the skills actually available in the current session. When available, load each selected skill's complete `SKILL.md` before using it.

Prefer these Superpowers components for their narrow stages:

- `$subagent-driven-development` for bounded worker dispatch.
- `$test-driven-development` for each behavior-changing task.
- `$systematic-debugging` when a failure's cause is not demonstrated.
- `$requesting-code-review` for read-only implementation review.
- `$verification-before-completion` immediately before the final claim.
- `$freeze` and `$unfreeze`, or `$using-git-worktrees`, when they provide an enforceable worker write boundary.

Use `$speckit-implement` for Spec Kit prerequisites, checklist and extension-hook semantics, artifact loading, and task completion conventions. Use `$speckit-converge` after the initial pass. Treat `[P]` as a hint; this skill's dependency and write-set checks decide whether work can actually run concurrently.

If a preferred Superpowers component is unavailable, apply the equivalent contract in the orchestration reference and record `composition: local-fallback` for that stage. Do not weaken evidence, review, or stop gates. Never claim that the missing component was invoked.

gstack `$review` is optional and belongs only after implementation verification when the user wants a pre-landing branch review. It is not the task executor or per-wave reviewer.

## Host capability contract

Before each stage, inspect the current host for skill discovery, component skills, delegation, command support, and enforceable isolated write boundaries. Use native capabilities only when they satisfy the stated gate. When a preferred component is unavailable, apply the equivalent contract and record `composition: local-fallback`; never claim it ran. If a host cannot enforce worker isolation, use controller-applied patches or sequential execution. Block rather than promote a result that lacks equivalent evidence.

## Entry gate and preflight

1. Confirm the target repository and resolve the active feature with one supported Spec Kit prerequisite script. Inspect both `.specify/scripts/bash/check-prerequisites.sh` and `.specify/scripts/powershell/check-prerequisites.ps1`, and Prefer the host-native executable when both exist. Invoke Bash with `--json --require-tasks --include-tasks` or PowerShell with `-Json -RequireTasks -IncludeTasks`; both invocations must return the same required feature and artifact paths. If the host-native script is unavailable, use the other executable supported script. If neither supported prerequisite script can be executed, stop instead of skipping validation: report both expected paths, state that Bash and PowerShell are the supported prerequisite script families, and direct the user to repair the repository's Spec Kit initialization or script distribution.
2. Require `.specify/`, `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`. Load the constitution, research, data model, contracts, and quickstart when present. This skill does not implement generic Spec Kit features that lack an Idea Refinery handoff.
3. Build or resume one explicit completion checklist in `implementation-state.md` before any mutable application work. It must cover preflight authorization and validator resolution, tasks, reviews, objective corrections, task promotion, state recording, convergence, hooks, and final evidence. Give each item an owner, acceptance command or evidence target, status, and blocker category when blocked.
4. Identify every protected output path that a planned command, hook, generator, formatter, test, or validator can mutate. Identify every validator prerequisite and whether the exact validator, equivalent evidence, or neither is available. Record the path/prerequisite category, required authority, remediation, and evidence. Do this before hooks, baselines, snapshots, leases, worker dispatch, or any other mutable work.
5. If new authority is needed, issue at most one precise request for each normalized protected-path category or validator-prerequisite category. A request states the target/category, why it is needed, the smallest authority, and the affected checklist item. Persist the request token so a resume never re-asks. A refused or unavailable authority is a `missing-authority` blocker; it is not an ordinary pause.
6. Process enabled unconditional `before_implement` hooks exactly once per implementation run using `$speckit-implement` semantics: present optional hooks for user invocation and execute mandatory hooks only after their protected paths and prerequisites have passed preflight. Do not evaluate conditional hooks locally. Record output and changed paths for hooks that run; any later hook-driven mutation invalidates affected evidence.
7. Report all feature checklists. If any item is unchecked, obtain the same explicit proceed decision required by `$speckit-implement`; record it as a scoped authorization in the completion checklist rather than repeatedly pausing at later routine gates.
8. Require the refinery handoff verdict to be `ready-for-implementation` or `ready-for-implementation-degraded`. Independently scan the decision and question registries and stop when any material decision is open, `decision-needed`, or reopened, even if the summary verdict says ready. For a degraded handoff, surface the waiver and missing coverage before proceeding. Stop on `blocked-on-decision`, unresolved blocker/critical/high findings, or an absent/unrecognized readiness record.
9. Capture the initial git status, artifact hashes, relevant baseline test result, available agent capacity, resolved component routing, and completed preflight evidence in `implementation-state.md`.

## Terminal-verdict drive loop

After preflight, repeatedly advance the earliest incomplete checklist item until every item is complete or a genuine blocker is recorded. The controller owns this loop; it is not a background monitor or scheduler and it never waits for a new user message while actionable authorized work remains.

1. Order checklist items deterministically: preflight authorization, validator prerequisites, review correction, task promotion, state recording, convergence, and final verification. Tasks and review evidence feed those gates; a correction always precedes promotion.
2. For every incomplete routine item, take the smallest authorized action, update its evidence and status, invalidate dependent evidence when required, and continue to the next actionable item in the same invocation.
3. Treat an objective, in-scope review finding as a new correction slice. Implement, review, and verify that correction without asking the user; then resume promotion. Reject incorrect review feedback with recorded evidence. Escalate only a finding that requires a material product or architecture decision.
4. Send progress updates for material milestones, but do not yield control or end the turn because a routine task, remediation, promotion, convergence, state write, or verification step remains actionable. A progress update must name completed and next checklist items.
5. A blocked outcome is valid only for `missing-authority`, `material-decision`, or `external-state`. Classify a failed exact validator as `external-state` only after checking for equivalent evidence; otherwise record that equivalent validation and continue. Scheduling conflicts, stale evidence, missing review envelopes, path drift, and unexplained failures are recovery work, not terminal pauses: isolate, repair, redispatch, or debug them within the loop.
6. Emit a terminal verdict only after the loop has either completed every checklist item or explicitly attached one of those blocker categories to every non-completable item. Do not return an interim result with actionable internal work.

## Plan execution

The controller is the only writer of `tasks.md`, `refinery-state.md`, and `implementation-state.md`.

1. Build an inventory of unchecked tasks, requirement/story links, explicit dependencies, affected paths, verification commands, and material-decision boundaries. Before any dispatch, map every buildable requirement to one or more task IDs and an acceptance target; block on gaps rather than spending convergence on a preventable omission.
2. Convert the inventory into task slices that can complete one coherent red-green-refactor cycle. Combine tasks only when separating them would make either slice unverifiable.
3. Derive conservative read and write sets. Treat repository-wide configuration, dependency manifests and lockfiles, generated outputs, migrations, shared schemas, snapshots, and shared test fixtures as exclusive resources.
4. Form deterministic waves. A slice is eligible only when dependencies are complete, its write set is disjoint from every other slice in the wave, and none of its paths overlaps unrelated uncommitted work. Acquire the protected-path lease and dispatch at most three implementation workers.
5. Give every worker an immutable assignment envelope from the orchestration contract. Parallel edits require a host-enforced path boundary such as a scoped sandbox/freeze or an approved isolated worktree. If no boundary exists, have workers return proposed patches for controller application or execute sequentially. A worker may never update shared coordination artifacts and must stop when it discovers missing authority or an unexpected required path.
6. After workers return, independently inspect changed paths and evidence. Do not trust completion claims without command output.
7. Dispatch a different, read-only reviewer with the frozen before/after diff, applicable requirements, task IDs, and worker evidence. The reviewer does not edit files or talk to the user. A missing or invalid review envelope leaves the wave in `review-blocked` until a replacement independent review succeeds.
8. Resolve every material finding through the terminal-verdict drive loop. Apply objective in-scope corrections through a new TDD slice without a new user prompt; reject incorrect feedback with evidence; stop only for a material decision. Do not promote the slice yet.
9. Run the relevant integrated verification command. Mark task checkboxes complete only after review disposition and integrated verification pass, record task promotion in the completion checklist, then continue the drive loop into the next dependent wave.

When agent capacity is unavailable or only one safe slice exists, execute the same contract sequentially. Parallelism is an optimization, not a completeness requirement.

## Convergence and completion

After the initial task list is complete, the drive loop invokes `$speckit-converge` under the controller identity. Validate that its only write is the expected append-only `tasks.md` patch, record the before/after hashes, and reject any other mutation. If it appends tasks, execute them through the same scheduler, TDD, review, and correction gates without asking the user again. Permit at most two convergence implementation cycles. Stop only when the same root gap needs a material decision, a new high-severity contradiction is unresolved, or an external-state failure prevents verification.

Before completion:

1. Run all enabled unconditional `after_implement` hooks required by `$speckit-implement` exactly once, after convergence and before final verification. Record their mutations and invalidate/re-run any affected evidence.
2. Re-run the narrow tests, relevant integration suites, and the project-level verification command from a clean command invocation.
3. Confirm every buildable requirement maps to completed tasks, reviewed changes, and verification evidence.
4. Confirm no assignment wrote outside its declared set and no unrelated user change was incorporated.
5. If available, use `$verification-before-completion`; otherwise apply its evidence-before-claims rule locally.

Return exactly one verdict. `BLOCKED ON DECISION` is only for missing authority or a material decision; `BLOCKED ON VERIFICATION` is only for an external-state failure after available equivalent evidence has been evaluated:

- `IMPLEMENTATION COMPLETE` when all gates pass.
- `BLOCKED ON DECISION` with the decision, owner, options, recommendation, and affected tasks.
- `BLOCKED ON VERIFICATION` with failing commands, demonstrated cause if known, and remaining work.

Include completed task IDs, changed paths, test commands/results, review dispositions, convergence cycles, degraded composition or handoff waivers, and deferred pre-landing actions. Do not imply that optional gstack review, commit, PR, or deployment occurred.
