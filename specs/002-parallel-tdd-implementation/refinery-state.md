# Refinery State: Parallel TDD Implementation Skill

## Status

| Field | Value |
| --- | --- |
| Current stage | Complete |
| Design approval | approved by user on 2026-09-02 |
| Handoff verdict | ready-for-implementation |
| Repair cycles authorized | 0 of 2 used |

## Decisions

| ID | Topic | Decision | Owner | Status | Reopen trigger |
| --- | --- | --- | --- | --- | --- |
| D-001 | Skill boundary | Create a sibling `idea-refinery-implement` skill | user | decided | Evidence that a unified skill preserves a clearer authorization boundary |
| D-002 | Composition | Superpowers-first hybrid with Spec Kit traceability and gstack final review | user | decided | Required component unavailable with no equivalent safe fallback |
| D-003 | Parallelism | Parallel bounded subagents only for dependency-safe, disjoint write sets | user | decided | Evidence that stronger isolation permits safe overlap |
| D-004 | Development discipline | Recorded TDD plus independent review | user | decided | None without explicit user reversal |
| D-005 | Missing Superpowers components | Use equivalent local contracts and disclose degraded composition | controller | decided | User selects strict dependency failure instead |
| D-006 | Invocation | Explicit-only `$idea-refinery-implement` | user | decided | User requests automatic discovery |
| D-007 | Eligibility | Only Idea Refinery handoffs with `refinery-state.md` and a ready verdict | user via approved sibling-handoff design | decided | User explicitly requests generic Spec Kit compatibility |

## Questions

| ID | Question | Answer | Status |
| --- | --- | --- | --- |
| Q-001 | Proceed with the recommended hybrid in the current repository? | Yes | answered |

## Review Findings

| ID | Reviewer | Severity | Artifact / section | Evidence | Smallest proposed change | Human decision | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Product | high | TDD baseline | Baseline failures or already-passing tests could be misrepresented as red/green evidence | Require controller-owned baseline evidence and block promotion until intended causality is shown | no | accepted in spec and orchestration contract |
| R-002 | Product | medium | Reviewer independence | The implementer could otherwise review itself and missing review had no recovery state | Require a different agent and resumable `review-blocked` replacement flow | no | accepted in skill and orchestration contract |
| R-003 | CEO | high | Handoff eligibility | Optional refinery state made the intended market/safety boundary ambiguous | Require Idea Refinery state and recognized ready verdict | yes | accepted using D-001/D-002/D-007 |
| R-004 | CEO | high | Pre-dispatch traceability | Missing tasks would be detected only after implementation during convergence | Block dispatch until every buildable requirement maps to tasks and acceptance targets | no | accepted |
| R-005 | Architect | high | Convergence authority | Direct append could conflict with controller-only coordination writes | Invoke under controller identity and validate/record exact append-only patch | no | accepted |
| R-006 | Architect | high | Worker isolation | Instructions alone cannot enforce a parallel worker's write boundary | Require scoped sandbox/freeze or worktree; otherwise controller-applied patches/sequential execution | no | accepted |
| R-007 | Architect | high | Snapshot and lease | Path claims and resume hashes lacked canonicalization/drift rules | Add versioned envelopes, canonical paths, protected hashes, lease, and quarantine | no | accepted |
| R-008 | Architect | medium | TDD causality | Red/green logs were not bound to ordered diffs and the new assertion | Add timestamps, hashes, baseline, test diff, assertion, and implementation diff evidence | no | accepted |
| R-009 | Architect | medium | Hook lifecycle | Per-run versus per-wave hooks and mutation invalidation were ambiguous | Run pre/post hooks once at defined boundaries and invalidate affected evidence | no | accepted |
| R-010 | Forward test | high | Readiness gate | A stale ready verdict could coexist with an open material decision | Scan decision/question registries independently and stop on open, decision-needed, or reopened material decisions | no | accepted |
| R-011 | Forward test | medium | Resume audit | State omitted worker identity and immutable assignment/lease linkage | Add assignment identity, envelope hash, path sets, lease, timestamps, and status | no | accepted |

## Stage Log

| Stage | Inputs | Outputs | Result |
| --- | --- | --- | --- |
| Discovery | User request, repository, installed skill catalog | Approved hybrid design | complete |
| Spec v1 | Approved design | `spec.md`, checklist, state | complete |
| Product review | Frozen Spec v1 | R-001, R-002 | complete; both accepted |
| CEO review | Frozen Spec v1 | R-003, R-004 | completed through approved fallback; accepted |
| Architect review | Frozen Spec v1 | R-005–R-009 | completed through approved fallback; accepted |
| Planning | Spec v1 and accepted findings | `plan.md`, research, data model, contract, quickstart, tasks | complete |
| Forward evaluation | Completed skill and fixture scenarios | R-010, R-011 | complete; both accepted |
| Validation | Completed skill and all design artifacts | Skill validation, traceability, repository tests | complete |

## Validation Evidence

| Gate | Evidence | Result |
| --- | --- | --- |
| Skill structure | Skill Creator `quick_validate.py idea-refinery-implement` | valid |
| Requirement traceability | FR-001 through FR-030 mapped explicitly in `tasks.md` | complete |
| Forward behavior | Independent module/lockfile/decision/fallback/reviewer fixture review | passed after R-010 and R-011 fixes |
| Repository regression | `uv run --project idea-refinery-full --extra dev pytest -q` | 77 passed, 3 pre-existing warnings |
| Formatting | `git diff --check` | passed |
