# Implementation State: [Feature]

## Run

| Field | Value |
| --- | --- |
| Run ID | |
| Feature directory | |
| Status | preparing \| executing \| reviewing \| review-blocked \| converging \| complete \| blocked |
| Handoff verdict | |
| Artifact hashes | |
| Initial git status | |
| Worker capacity | |
| Convergence cycles | 0 / 2 |
| Terminal drive status | not-started \| advancing \| complete \| blocked |
| Terminal verdict | |

## Component routing

| Stage | Preferred skill | Resolved implementation | Availability / degradation |
| --- | --- | --- | --- |
| Worker dispatch | subagent-driven-development | | |
| TDD | test-driven-development | | |
| Debugging | systematic-debugging | | |
| Review | requesting-code-review | | |
| Completion | verification-before-completion | | |
| Task semantics | speckit-implement | | |
| Convergence | speckit-converge | | |

## Preflight: authority and validator prerequisites

Complete this section before hooks, baselines, snapshots, leases, worker dispatch, or other mutable work. Normalize each protected path/category and persist request tokens so a resume never repeats a request.

| ID | Kind | Path or prerequisite category | Command / reason | Smallest authority or evidence needed | Exact validator / equivalent evidence | Request token | Resolution | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Allowed resolutions are `already-authorized`, `granted`, `exact-validator`, `equivalent-evidence`, `missing-authority`, or `external-state`. `missing-authority` and `external-state` require a linked blocker below; all others permit the drive loop to continue.

## Completion checklist

Maintain one checklist for the whole run. A routine incomplete item is actionable and must be advanced in the same invocation; it is never a reason to yield. Use blocker categories only for `missing-authority`, `material-decision`, or `external-state`.

| Order | Item ID | Kind | Owner | Dependencies | Acceptance command / evidence | Status | Blocker category | Completed at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Required kinds: `protected-path-authorization`, `validator-prerequisite`, `task`, `review`, `review-correction`, `task-promotion`, `state-recording`, `convergence`, `after-hook`, and `final-verification`. Add one row per applicable task, review, correction, and convergence append.

## Progress log

Record material milestones without yielding while an actionable checklist item remains.

| Time | Completed item | Next actionable item | Action / evidence | Progress update sent |
| --- | --- | --- | --- | --- |

## Waves

| Wave | Slice IDs | Dependencies | Declared write sets | Status | Verification |
| --- | --- | --- | --- | --- | --- |

## Assignments

| Wave / slice | Worker identity | Envelope version / hash | Declared read set | Declared write set | Wave lease | Dispatched | Returned | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Slice evidence

| Slice | Task IDs | Baseline | Red | Green | Refactor | Changed paths | Review | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Review findings

| ID | Severity | Requirement / task | Evidence | Disposition |
| --- | --- | --- | --- | --- |

## Decisions and blockers

| ID | Owner | Decision or blocker | Category | Options / evidence | Affected checklist items | Status |
| --- | --- | --- | --- | --- | --- | --- |

## Verification log

| Time | Scope | Command | Exit status | Result |
| --- | --- | --- | --- | --- |
