# Refinery state

## Feature status

| Field | Value |
| --- | --- |
| Feature | Cross-Host Idea Refinery Skills |
| Active Spec Kit directory | `specs/003-copilot-hermes-skills` |
| Current stage | handoff |
| Handoff verdict | ready-for-implementation |

## Decision queue

| ID | Canonical decision | Options and trade-offs | Recommendation | Owner | Status | Source | Evidence to reopen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | Portability scope | Full workflows in Codex, GitHub Copilot, and Hermes; do not publish reduced variants | Use a portable-core design with native discovery/install entrypoints | user | decided | User approval on 2026-09-02 | Evidence that a required full-workflow gate cannot be preserved with a documented fallback |
| D-002 | Canonical source | Preserve the existing Codex skill behavior as the canonical workflow; distribute validated host entrypoints | Avoid independent, manually maintained workflow forks | controller | decided | Approved design | Evidence that a host requires material, incompatible behavior |

## Question registry

| ID | Canonical topic | Question | Answer or linked decision | Status | First raised by | Used by | Reopen rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | Host workflow scope | Should Copilot and Hermes receive the full skills or reduced compatible entrypoints? | Full skills; D-001 | answered | controller | discovery, spec-v1 | New host limitation that prevents a required gate |

## Review ledger

| ID | Reviewer | Severity | Artifact / section | Evidence | Smallest proposed change | Human decision? | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | CEO | high | Spec v1, User Story 3 and FR-006 | Per-host installation path was not explicit | Add a host setup matrix | no | accepted |
| R-002 | CEO | medium | Spec v1, FR-001 | Portability could be mistaken for syntax support | Require workflow parity and explicit exceptions | no | accepted |
| R-003 | Product | high | Spec v1, User Stories 1–3 | Discovery and helper availability were conflated | Add a capability matrix and fallback disclosure | no | accepted |
| R-004 | Product | medium | Spec v1, User Story 3 | Copied installs can become stale | Document update/version validation | no | accepted |
| R-005 | Architect | critical | Spec v1, FR-002/007/008 | Independent host copies would drift | Generate and validate distributions from canonical sources | no | accepted |
| R-006 | Architect | high | Spec v1, FR-003/005 | Fallback selection was not enforceable | Add host-neutral capability selection order | no | accepted |
| R-007 | Architect | medium | Spec v1, FR-006/009 | Existing Spec Kit integration can be host-specific | Preserve configuration and document host setup | no | accepted |
| R-008 | Spec Kit | high | Plan distribution format; Tasks T003/T007/T010 | Generated `SKILL.md` files reference supporting documents that are not included in the planned distribution | Synchronize required `references/` trees and validate them | no | accepted in repair cycle 1 |
| R-009 | Spec Kit | high | Tasks requirement coverage | Requirement-to-task mapping was implicit and could not support deterministic traceability | Add explicit mapping table | no | accepted in repair cycle 2 |

## Run and repair ledger

| Run ID | Resolved config hash | Active stage | Status | Repair authorization | Repair cycles | Waiver |
| --- | --- | --- | --- | --- | --- | --- |
| local-003 | pending | handoff | complete | bounded (max 2) | 2/2 | User authorized on 2026-09-02 |

## Stage log

| Stage | Inputs supplied | New IDs | Artifact changes | Outcome |
| --- | --- | --- | --- | --- |
| Discovery | User request, repository inspection, approved portable-core design | D-001, D-002, Q-001 | None | complete |
| Spec v1 | D-001, D-002, Q-001 and repository context | None | Created `spec.md` and requirements checklist | complete |
| CEO review | Frozen Spec v1 and D-001/D-002/Q-001 | R-001, R-002 | Added `reviews/ceo.md` | complete; findings accepted |
| Product review | Frozen Spec v1 and D-001/D-002/Q-001 | R-003, R-004 | Added `reviews/product.md` | complete; findings accepted |
| Architect review | Frozen Spec v1 and D-001/D-002/Q-001 | R-005, R-006, R-007 | Added `reviews/architect.md` | complete; findings accepted |
| Synthesis | All independent review findings | None | Updated Spec v2 requirements and success criteria | complete |
| Clarification | D-001, D-002, Q-001, and accepted R-001–R-007 | None | No material unanswered ambiguity; no spec clarification required | complete |
| Plan and tasks | Spec v2 and accepted R-001–R-007 | None | Created `plan.md` and `tasks.md` | complete |
| Analysis | Spec v2, plan, tasks, constitution | R-008 | Found missing distributed support references | high-severity gap; repair cycle 1 authorized and active |
| Repair 1 | R-008 | None | Made distributions self-contained in plan and tasks | complete |
| Analysis | Repaired plan and tasks | R-009 | Found absent deterministic requirement-to-task traceability | high-severity gap; repair cycle 2 authorized and active |
| Repair 2 | R-009 | None | Added explicit traceability mapping to `tasks.md` | complete |
| Final analysis | Repaired spec, plan, tasks, and constitution | None | Verified terminology, ordering, coverage, and required support-reference contract | complete; no unresolved blocker, critical, or high finding |
| Handoff | Approved design, decisions, reviews, clarification, analysis, and traceability | None | Set ready-for-implementation verdict | complete |
| Implementation | All T001–T021, independent review, and final verification | None | Generated portable skills, tests, and host documentation | IMPLEMENTATION COMPLETE |
