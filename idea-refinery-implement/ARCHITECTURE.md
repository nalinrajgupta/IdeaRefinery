# Idea Refinery Implement Architecture

How `$idea-refinery-implement` turns a ready Idea Refinery handoff into reviewed, test-driven application changes without silently expanding its authority or pausing between authorized routine gates.

## Purpose and boundary

This explicit-only skill consumes an active feature produced by `$idea-refinery-full`. It may edit application code, tests, `tasks.md`, and feature-local `implementation-state.md`. It may not change approved product scope or architecture, perform destructive cleanup, create worktrees without approval, or commit, push, open a pull request, merge, or deploy.

It does not implement arbitrary Spec Kit features. The active feature must contain `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md` with a recognized ready verdict.

## Architecture at a glance

```text
Ready Idea Refinery handoff
  -> entry, readiness, and preflight authority/validator gate
  -> explicit completion checklist
  -> requirement/task inventory
  -> conservative dependency and write-set scheduling
  -> deterministic execution waves (maximum 3 workers)
  -> isolated red-green-refactor workers
  -> controller evidence and path inspection
  -> independent read-only wave review
  -> automatic objective finding correction, task promotion, integrated verification
  -> Spec Kit convergence (0..2 implementation cycles)
  -> after hooks and fresh final verification
  -> terminal-verdict drive loop: advance or explicitly block every item
  -> optional gstack pre-landing review
```

Parallelism is an optimization. When isolation, path ownership, or agent capacity is insufficient, the same evidence gates run sequentially.

The drive loop is foreground control flow in the active invocation, not a background monitor or scheduler. It reports milestones but does not yield because routine implementation work remains.

## Component responsibilities

| Component | Responsibility | Write authority |
| --- | --- | --- |
| Controller | User communication, preflight, completion checklist, task graph, scheduling, leases, shared state, review disposition, objective remediation, hooks, convergence, and final claims | Sole writer of `tasks.md`, `refinery-state.md`, and `implementation-state.md`; applies approved application changes |
| `$speckit-implement` | Prerequisite, checklist, extension-hook, artifact-loading, and task-completion conventions | Only through the controller's execution of the stage |
| Implementation worker | One immutable task slice and its test-first implementation | Only declared source/test paths behind an enforceable boundary |
| Superpowers components | Bounded dispatch, TDD, debugging, review, and completion verification when present | Limited to the stage contract and worker boundary |
| Reviewer | Independent requirements-first and code-quality review of one frozen wave | Read-only |
| `$speckit-converge` | Detects remaining spec-to-code gaps after the initial pass | Controller validates its single append-only `tasks.md` change |
| gstack `$review` | Optional holistic branch review after verification and before landing | Outside the mandatory inner loop |

The preferred Superpowers components are `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, and `verification-before-completion`. Availability is resolved from the current session. If a component is absent, the controller applies the equivalent local contract and records `composition: local-fallback`; the safety and evidence gates do not weaken.

## What each step does

| Step | Question answered | Output | Difference from the next step |
| --- | --- | --- | --- |
| Entry gate | Is this the right repository, active feature, and authorized handoff? | Validated ready state, hook results, baseline context | Establishes permission and readiness; inventory proves coverage |
| Inventory and traceability | Is every buildable requirement represented by work and an acceptance target? | Requirement/task map, dependencies, paths, commands | Describes all work; scheduling decides what is safe now |
| Slicing and scheduling | Which coherent TDD slices can execute, and which may run together? | Deterministic waves and conservative write sets | Proves logical independence; isolation enforces it technically |
| Dispatch and isolation | Can a worker change only its assigned paths? | Immutable envelope, scoped boundary, and wave lease | Constrains mutations; TDD proves the behavior change |
| Recorded TDD | Did the new test fail for the intended reason and pass after the smallest implementation? | Baseline, red, green, refactor, and scope evidence | Demonstrates causal behavior; review independently challenges correctness and scope |
| Review and promotion | Does a different agent find the slice compliant, complete, and safe? | Findings, dispositions, promoted task state | Checks planned work; convergence checks the whole feature for omitted work |
| Convergence | Did the completed task list still miss any approved requirement? | Zero gaps or append-only remediation tasks | May add bounded work; completion validates the final state without adding scope |
| Completion | Does fresh evidence support the final claim? | One terminal verdict and evidence report | Ends implementation; optional gstack review is a separate landing concern |

TDD and review are complementary. TDD proves that a particular assertion changes from failing to passing because of the implementation. Review checks whether the assertion is sufficient, the requirement is actually met, failure paths are covered, and the change stayed inside scope.

Wave verification and convergence are also different. Wave verification integrates already planned slices. Convergence compares the finished codebase with the entire spec, plan, and task set to find omissions.

## Entry, readiness, and preflight

The controller inspects both supported Spec Kit prerequisite scripts and prefers the host-native executable when both exist:

```bash
.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

```powershell
.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
```

If the host-native script is unavailable, it uses the other executable supported script. If neither script can be executed, it stops, reports both expected paths and supported script families, and directs the user to repair the repository's Spec Kit initialization or script distribution instead of skipping validation.

It then, before any mutable work (including hooks, baselines that can write, snapshots, leases, worker dispatch, test generators, or validators):

1. Requires `.specify/`, `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`.
2. Loads the constitution and optional research, data model, contracts, and quickstart.
3. Creates or resumes one completion checklist covering preflight, tasks, reviews, corrections, promotion, state, convergence, hooks, and final evidence.
4. Identifies protected output paths and validator prerequisites, records exact-validator availability or equivalent evidence, and requests any ungranted authority once per normalized path/prerequisite category.
5. Runs each enabled unconditional `before_implement` hook exactly once after its protected paths and prerequisites have passed preflight.
6. Reports every feature checklist and records any required explicit proceed decision as scoped authority rather than re-asking at later routine gates.
7. Accepts only `ready-for-implementation` or `ready-for-implementation-degraded`.
8. Independently scans the decision/question registry for open, decision-needed, or reopened material decisions and scans findings for unresolved blocker, critical, or high items.
9. Records git status, artifact hashes, baseline results, capacity, component routing, preflight, and checklist evidence in `implementation-state.md`.

A stale ready summary cannot override an open material decision.

The deterministic validation sidecar that validates continuation transitions is provider- and credential-independent. It cannot authorize paths, call a model provider, or run a background process; the controller remains responsible for the foreground workflow and is the sole shared-artifact writer.

## Completion checklist and continuity

An invocation is authority to finish approved routine gates. The controller repeatedly advances the earliest incomplete checklist item: preflight authorization, validator prerequisite, review correction, task promotion, state recording, convergence, and final verification. It records the owner, dependency, acceptance evidence, status, and any blocker category for every item.

An objective in-scope review finding becomes a correction slice automatically. The controller performs its TDD, independent review, and verification, then resumes task promotion without a new user prompt. It asks the user only when the smallest correction requires a material product/architecture decision or authority outside the invocation boundary.

Progress messages name the completed item and the next actionable one, but do not yield while a routine item remains. Only three blocker categories can terminate a run: `missing-authority`, `material-decision`, and `external-state`. The first two map to `BLOCKED ON DECISION`; the latter maps to `BLOCKED ON VERIFICATION` after exact validation and equivalent evidence have both been evaluated.

## Inventory, slicing, and scheduling

Before dispatch, every buildable requirement must map to one or more task IDs and a concrete acceptance target. An unmapped requirement blocks execution instead of consuming convergence budget later.

Tasks become slices sized for one coherent red-green-refactor cycle. The scheduler derives conservative read and write sets and treats these as exclusive shared resources:

- repository-wide configuration;
- dependency manifests and lockfiles;
- generated outputs;
- ordered migrations;
- shared schemas;
- snapshots and shared test fixtures;
- controller state files.

`[P]` in `tasks.md` is only a hint. A slice may join a wave only when predecessors are verified, exact and ancestor/descendant path claims do not overlap, tests do not rewrite another slice's resources, no unrelated dirty path overlaps, and failure can be reviewed independently. Eligible slices are sorted by task ID, and a wave contains at most three workers.

Paths are normalized repository-relative claims. Symlink targets are resolved, traversal outside the repository is rejected, and tracked content, relevant untracked content, file type/mode, and protected state hashes are captured. The controller holds an exclusive wave lease until post-return drift verification finishes.

## Dispatch and isolation

Each worker receives an immutable versioned envelope containing the run, wave, slice, tasks, requirements, constraints, satisfied dependencies, allowed read/write paths, forbidden shared paths, test commands, baseline, selected component, stop conditions, timestamp, protected hashes, and lease.

Parallel edits require a host-enforced boundary such as a scoped sandbox/freeze or a user-approved isolated worktree. Directory names alone are not enforcement. When no boundary is available, workers return proposed patches for controller application or execution becomes sequential.

Workers never update `tasks.md`, `refinery-state.md`, `implementation-state.md`, `.specify/feature.json`, or another worker's paths. Discovering a required undeclared path or material product/architecture decision stops the slice.

## Recorded TDD cycle

Every behavior-changing slice records:

1. **Baseline**: Existing narrow and broader commands, outputs, exit codes, timestamps, and source hashes.
2. **Red**: A test-only diff hash followed by the narrow command failing at the newly added assertion for the intended missing behavior.
3. **Green**: The smallest production change and the same narrow command passing.
4. **Refactor**: Clarity improvements without new behavior, followed by narrow and broader tests.
5. **Scope check**: Ordered diff hashes, timestamps, and actual changed paths checked against the envelope.

Syntax, import, environment, unrelated, and pre-existing failures are not valid red evidence. If the new test already passes, the worker must improve the test or show that no production change is required. Documentation-only and generated-only tasks require a concrete `test-first: inapplicable` rationale plus an appropriate validation command, accepted by the controller.

## Review and promotion

The controller independently inspects worker changes and command evidence, then gives a frozen assignment, diff, applicable requirements/tasks, baseline, and evidence to a reviewer who is different from every worker in the wave.

The reviewer checks requirement compliance first, then code quality, failure paths, test strength, declared-path compliance, and regressions. Missing, malformed, timed-out, or self-authored review produces `review-blocked`; it never implies approval.

Every material finding has evidence, severity, affected requirement/task, impact, smallest correction, decision status, and disposition. Objective in-scope corrections become new TDD slices automatically. Incorrect feedback is rejected with evidence. Material product or architecture decisions return to the user. Only after all material findings are disposed and integrated verification passes does the controller mark tasks complete.

## Convergence

After the original task list completes, the controller snapshots `tasks.md` and invokes `$speckit-converge` under its own identity. The only permitted mutation is one validated append-only Convergence section. The controller records the exact patch and hashes; any other change is rejected.

Appended tasks use the same scheduler, TDD, review, correction, and promotion gates without another user prompt. There are at most two convergence implementation cycles. A repeated root cause or new high-severity contradiction is investigated and repaired when objective and in scope; the loop stops only for a material decision or external-state verification failure.

## Completion

Enabled unconditional `after_implement` hooks run once after convergence and before final verification. Any hook mutation invalidates affected assignments, tests, or review evidence.

The controller then runs fresh narrow, integration, and project-level verification; checks requirement-to-task-to-change-to-test traceability; verifies declared-path ownership; and confirms unrelated user changes were not incorporated. It uses Superpowers `verification-before-completion` when available or applies the same evidence-before-claims rule locally. It issues `IMPLEMENTATION COMPLETE` only after the terminal drive loop confirms every completion-checklist item is complete.

The skill returns exactly one verdict:

```text
IMPLEMENTATION COMPLETE
BLOCKED ON DECISION
BLOCKED ON VERIFICATION
```

The report lists completed task IDs, changed paths, commands/results, review dispositions, convergence cycles, component fallbacks, handoff waivers, and deferred landing actions.

## Failure and recovery

| Failure | Result |
| --- | --- |
| Missing, malformed, or blocked handoff | Stop before application edits |
| Unchecked checklist | Request and persist one scoped proceed authority, then continue routine gates |
| Unmapped requirement | Repair planning before dispatch |
| Unknown, overlapping, dirty, or unenforceable write set | Serialize or use controller-applied patches; do not return an interim pause |
| Worker needs an undeclared path | Stop, recompute ownership, and redispatch |
| Invalid red evidence | Prohibit production edits or promotion |
| Unexplained test failure | Use systematic debugging or reproduce, isolate, hypothesize, and test the cause before classifying external state |
| One worker fails while disjoint workers succeed | Preserve inspectable work but do not promote failed or unreviewed slices |
| Invalid reviewer result | Enter `review-blocked` and obtain a replacement reviewer |
| Protected artifact or path drifts | Quarantine, perform three-way attribution, then re-plan and re-review |
| Hook changes a protected input | Invalidate and rerun affected evidence |
| Convergence repeats a root gap | Repair an objective in-scope cause; stop only if the resolution needs a material decision or external state |
| Material decision appears | Stop and return ownership to the user |

Resume may reuse a verified wave only when artifact hashes, path hashes, commands, envelope identity, and reviewer dispositions still match.

## Related documentation

- [Skill entrypoint](SKILL.md)
- [Normative implementation contract](references/orchestration-contract.md)
- [Implementation state template](references/implementation-state-template.md)
- [Repository structure](../RepoStructure.md)
- [Refinement architecture](../idea-refinery-full/ARCHITECTURE.md)
- [Implementation feature plan](../specs/002-parallel-tdd-implementation/plan.md)
