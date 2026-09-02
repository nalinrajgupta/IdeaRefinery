# Refinery state

This file is the controller state for one Idea Refinery Full feature. Update it before changing `spec.md`, `plan.md`, or `tasks.md` after a material question, decision, or review finding.

## Feature status

| Field | Value |
| --- | --- |
| Feature | |
| Active Spec Kit directory | |
| Current stage | discovery \| spec-v1 \| review \| synthesis \| clarify \| plan-and-tasks \| analysis-authorization \| analyzing \| repairing \| handoff |
| Handoff verdict | draft \| ready-for-implementation \| ready-for-implementation-degraded \| blocked-on-decision |

## Decision queue

Only use this table for user-owned product, strategic, or risk decisions.

| ID | Canonical decision | Options and trade-offs | Recommendation | Owner | Status | Source | Evidence to reopen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | | | | user | open \| decided \| deferred | | |

## Question registry

Record every material question, including questions a component skill proposes but the controller suppresses as duplicates. Two questions are duplicates when they seek the same decision, behavior, actor, constraint, or acceptance criterion, even if the wording differs.

| ID | Canonical topic | Question | Answer or linked decision | Status | First raised by | Used by | Reopen rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | | | | proposed \| answered \| suppressed-duplicate \| reopened | | | |

## Review ledger

Every material review finding must have one entry.

| ID | Reviewer | Severity | Artifact / section | Evidence | Smallest proposed change | Human decision? | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | CEO \| Product \| Architect \| Spec Kit | blocker \| critical \| high \| medium \| low | | | | yes \| no | accepted \| rejected — rationale \| deferred — trigger \| decision-needed |

## Run and repair ledger

The state file summarizes the active run; detailed worker envelopes, immutable briefs, hashes, trace events, and stage markers live under the feature-local `runs/<run-id>/` directory.

| Run ID | Resolved config hash | Active stage | Status | Repair authorization | Repair cycles | Waiver |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | none \| bounded (max 2) | 0/2 | |

## Stage log

Use one line per completed stage. State which decisions and questions were supplied to the component skill in its stage brief.

| Stage | Inputs supplied | New IDs | Artifact changes | Outcome |
| --- | --- | --- | --- | --- |
| | | | | |
