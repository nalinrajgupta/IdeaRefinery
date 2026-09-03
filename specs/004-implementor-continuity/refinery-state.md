# Refinery state

## Feature status

| Field | Value |
| --- | --- |
| Feature | Implementor Continuity Controls |
| Active Spec Kit directory | `specs/004-implementor-continuity` |
| Current stage | handoff |
| Handoff verdict | ready-for-implementation |

## Decision queue

| ID | Canonical decision | Options and trade-offs | Recommendation | Owner | Status | Source | Evidence to reopen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | Continuity design | Instruction-only, deterministic guardrails, or a background monitor | Deterministic guardrails with no persistent monitor | user | decided | User approval on 2026-09-03 | Evidence that non-persistent checks cannot detect a required failure mode |

## Question registry

| ID | Canonical topic | Question | Answer or linked decision | Status | First raised by | Used by | Reopen rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | Improvement scope | Should runtime automation be included? | Deterministic guardrails only; D-001 | answered | controller | discovery, spec-v1 | New evidence requiring persistent monitoring |

## Review ledger

| ID | Reviewer | Severity | Artifact / section | Evidence | Smallest proposed change | Human decision? | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | CEO | high | FR-001, FR-006 | Routine pauses break authorized implementation | Require terminal drive loop | no | accepted |
| R-002 | Product | high | FR-004–FR-007 | Environment interruptions should occur before work | Add preflight and blocker taxonomy | no | accepted |
| R-003 | Architect | high | FR-002, FR-008 | Prose cannot enforce continuity | Add sidecar validation and fixtures | no | accepted |

## Run and repair ledger

| Run ID | Resolved config hash | Active stage | Status | Repair authorization | Repair cycles | Waiver |
| --- | --- | --- | --- | --- | --- | --- |
| local-004 | pending | handoff | complete | bounded (max 2) | 0/2 | User authorized on 2026-09-03 |

## Stage log

| Stage | Inputs supplied | New IDs | Artifact changes | Outcome |
| --- | --- | --- | --- |
| Discovery | User-reported pauses and approved approach | D-001, Q-001 | None | complete |
| Spec v1 | D-001, Q-001 | None | Created `spec.md` | complete |
| Reviews and synthesis | Frozen Spec v1 | R-001–R-003 | Added reviews, Spec v2, plan, and tasks | complete |
| Analysis | Spec v2, plan, tasks, and constitution template | None | Verified coverage, terminology, ordering, and no unresolved ambiguity | complete; no repair required |
| Handoff | Approved design, reviewed artifacts, and analysis | None | Set ready-for-implementation verdict | complete |
