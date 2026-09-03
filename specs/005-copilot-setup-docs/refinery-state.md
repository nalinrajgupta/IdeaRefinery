# Refinery state

## Feature status

| Field | Value |
| --- | --- |
| Feature | First-Class GitHub Copilot Setup Documentation |
| Active Spec Kit directory | `specs/005-copilot-setup-docs` |
| Current stage | handoff |
| Handoff verdict | ready-for-implementation |

## Decision queue

| ID | Canonical decision | Options and trade-offs | Recommendation | Owner | Status | Source | Evidence to reopen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | Copilot documentation depth | Minimal links; first-class quick start plus complete setup guide; duplicate all compatibility details | Add a concise README quick start and a complete setup guide while keeping compatibility rationale centralized | user | decided | User selected `first_class` on 2026-09-03 | Evidence that users cannot complete setup without duplicated compatibility content |
| D-002 | Existing cross-host architecture | Reopen distribution design; preserve the generated `.agents/skills` distribution | Preserve the settled portable distribution and document its Copilot installation paths | controller | decided | `specs/003-copilot-hermes-skills/refinery-state.md` D-001 and D-002 | Evidence that current Copilot no longer discovers standard agent skills from the documented locations |
| D-003 | Personal Copilot skill path | Remove personal setup; document `~/.copilot/skills` as an observed supported path | Keep personal setup because the current host loaded both copied skills successfully | user | decided | Successful install and `/idea-refinery-full` invocation on 2026-09-03 | Copilot stops discovering personal skills from this location |
| D-004 | Invocation syntax consistency | Documentation-only limitation note; widen scope to make skill descriptions host-neutral | Make canonical descriptions host-neutral and regenerate distributions so Copilot and Codex instructions do not conflict | user | decided | User selected documentation limitation on 2026-09-03 | Evidence that the limitation note still causes incorrect invocation or support burden |
| D-005 | Native Windows implementation prerequisites | Require Bash-backed Spec Kit setup; widen scope to select an available platform script | Prefer platform-aware prerequisite selection so documented Windows support covers both workflows | user | decided | User selected platform-aware preflight on 2026-09-03 | Evidence that Spec Kit exposes no reliable platform-neutral prerequisite selection |

## Question registry

| ID | Canonical topic | Question | Answer or linked decision | Status | First raised by | Used by | Reopen rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | Invocation intent | Is `test skill` only a smoke test or a request to refine a feature? | Refine documentation so `setup.md` and `README.md` explain GitHub Copilot usage | answered | controller | discovery, spec-v1 | User changes the requested outcome |
| Q-002 | Documentation structure | How much Copilot guidance belongs in the two top-level documents? | First-class README quick start plus complete setup guide; D-001 | answered | controller | discovery, spec-v1 | Usability testing shows the split is insufficient |
| Q-003 | Platform script support | Which prerequisite script families must implementation preflight support? | Bash and PowerShell | answered | Spec Kit clarification | clarify, plan, tasks | A supported Spec Kit release removes or renames one of these script families |

## Review ledger

| ID | Reviewer | Severity | Artifact / section | Evidence | Smallest proposed change | Human decision? | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | CEO | high | Spec v1 assumptions and personal install requirements | Existing compatibility guide did not explicitly name the personal path | Verify or remove the personal path | yes | accepted — D-003 records successful host discovery |
| R-002 | CEO | medium | Spec v1 success criteria | Expected refinement artifacts and verdict are not part of a success criterion | Add an outcome-recognition criterion | no | accepted |
| R-003 | Architect | high | Invocation requirements and generated descriptions | Copilot uses slash invocation while generated descriptions advertise dollar-prefixed invocation | Correct documentation and decide whether skill descriptions become host-neutral | yes | accepted — document the limitation per D-004 |
| R-004 | Architect | high | Windows setup and implementation preflight | Implementation calls a Bash prerequisite script directly | Require Bash or add platform-aware preflight selection | yes | accepted — add platform-aware selection per D-005 |
| R-005 | Architect | high | Personal install lifecycle | Repeat runs, preflight, atomic replacement, and missing-safe removal are unspecified | Add failure-safe and idempotent lifecycle acceptance criteria | no | accepted |
| R-006 | Architect | medium | Project versus personal precedence | Active copy and precedence are unspecified | Add precedence and active-location troubleshooting | no | accepted |
| R-007 | Architect | high | Workflow path filters | README and setup changes do not trigger documentation validation | Add both files to relevant workflow path filters | no | accepted |
| R-008 | Architect | high | Documentation validation | Current tests do not validate required Copilot content | Add requirement-focused automated and manual validation mapping | no | accepted |
| R-009 | Architect | medium | Shell labeling | Compatibility guide contains unlabeled POSIX examples | Apply shell labels or redirects across all three documents | no | accepted |
| R-010 | Product | critical | Current README Copilot journey | Actionable setup remains Codex-specific | Add a concise Copilot quick start | no | accepted |
| R-011 | Product | critical | Current setup guide | No executable Copilot install and lifecycle journey | Add a contiguous complete Copilot section | no | accepted |
| R-012 | Product | high | Copilot reload guidance | Current docs omit refresh or restart after skill changes | Add refresh guidance beside lifecycle steps | no | accepted |
| R-013 | Product | medium | Documentation regression checks | Existing tests omit first-class Copilot guidance | Add focused assertions | no | accepted |
| R-014 | Spec Kit | high | SC-008, quickstart platform preflight, tasks T018-T021 | Content assertions alone do not require execution of Bash-only, PowerShell-only, both-present, and neither-present acceptance layouts | Add an explicit controlled four-layout walkthrough task and evidence record | no | accepted in repair cycle 1 |
| R-015 | Spec Kit | medium | Plan documentation layering and task T016 | T016 asks the compatibility guide to repeat update/removal lifecycle guidance owned by setup.md | Limit the compatibility guide to host summary, initialization preservation, capability, and synchronization; link to setup lifecycle | no | accepted in repair cycle 1 |
| R-016 | Spec Kit | low | Task T022 | The task says to add requirement traceability even though tasks.md already contains it | Change the task to verify and update traceability after repairs | no | accepted in repair cycle 1 |
| R-017 | Spec Kit | high | Foundational task order T004-T005 | The workflow filter implementation is ordered before its required failing contract assertion | Put the failing workflow-filter test before the YAML implementation task | no | accepted in repair cycle 2 |

## Run and repair ledger

| Run ID | Resolved config hash | Active stage | Status | Repair authorization | Repair cycles | Waiver |
| --- | --- | --- | --- | --- | --- | --- |
| local-005 | `1dde0c33337a8f12b1ab19264bc1dc9ea629db3c53c60d72ca4b557a2800ed96` | handoff | complete | bounded (max 2) | 2/2 | User authorized on 2026-09-03 |

## Resolved role roster

| Role | Model | Reasoning effort | Resolution |
| --- | --- | --- | --- |
| CEO | `gpt-5.5` | high | configured primary available |
| Product | `gpt-5.6-terra` | high | configured primary available |
| Architect | `gpt-5.6-sol` | high | configured primary available |
| Eval | `gpt-5.6-luna` | medium | configured primary available |
| Baseline | `gpt-5.4` | medium | configured primary available |

The deterministic sidecar bootstrap was attempted on 2026-09-03 but dependency retrieval failed during a package-index TLS handshake. Review and synthesis therefore use the skill's documented local contracts; no sidecar success is claimed.

## Stage log

| Stage | Inputs supplied | New IDs | Artifact changes | Outcome |
| --- | --- | --- | --- | --- |
| Discovery | User request, current README/setup content, Spec 003 decisions, installed Copilot skill behavior | D-001, D-002, Q-001, Q-002 | Created `refinery-state.md` | Approved first-class documentation design |
| Spec v1 | D-001, D-002, Q-001, Q-002, current documentation, and prior cross-host requirements | None | Created `spec.md` and `checklists/requirements.md`; activated `.specify/feature.json` | Complete; specification checklist passes |
| CEO review | Frozen Spec v1 and D-001 through D-003 | R-001, R-002 | Added `reviews/ceo.md` | One high path-verification concern resolved by observed successful invocation; one medium criterion gap accepted |
| Product review | Frozen Spec v1 and D-001 through D-003 | R-010 through R-013 | Added `reviews/product.md` | Existing documentation gaps confirmed; all findings accepted |
| Architect review | Frozen Spec v1 and D-001 through D-003 | R-003 through R-009 | Added `reviews/architect.md` | Two scope decisions required; remaining lifecycle and validation findings accepted |
| Synthesis | D-001 through D-005 and R-001 through R-013 | None | Updated `spec.md` to Spec v2 | All findings resolved; scope widened only for platform-aware implementation preflight |
| Clarification | D-001 through D-005, Q-001 through Q-002, and all resolved review findings | Q-003 | Added `Clarifications` and constrained FR-019/FR-020 to Bash and PowerShell | Complete; no remaining critical ambiguity and checklist remains 16/16 passing |
| Plan | D-001 through D-005, Q-001 through Q-003, resolved R-001 through R-013, and Spec v2 | None | Created `plan.md`, `research.md`, `data-model.md`, two contracts, and `quickstart.md` | Complete; pre- and post-design gates pass |
| Tasks | Spec v2, plan, research, data model, contracts, and quickstart | None | Created `tasks.md` with 25 dependency-ordered tasks and FR/SC traceability | Complete; all tasks use required checklist format |
| Analysis authorization | Settled decisions and completed design artifacts | None | Updated repair ledger | User authorized at most two narrowly scoped repair cycles |
| Analysis | Spec v2, plan, tasks, constitution template, and requirement traceability | R-014 through R-016 | None; read-only report | One high acceptance-evidence gap, one medium layering conflict, and one low redundant task |
| Repair 1 | R-014 through R-016 | None | Updated plan, quickstart, and tasks; added controlled platform walkthrough | Complete |
| Analysis | Repaired spec, plan, and tasks | R-017 | None; read-only report | One high test-first ordering contradiction |
| Repair 2 | R-017 | None | Reordered foundational workflow-filter test before implementation | Complete |
| Final analysis | Repaired spec, plan, tasks, constitution template, and traceability | None | None; read-only report | 30/30 requirements and criteria mapped, 26/26 tasks valid, no unresolved material finding |
| Handoff | Approved design, D-001 through D-005, Q-001 through Q-003, resolved R-001 through R-017, and final analysis | None | Set ready-for-implementation verdict | READY FOR IMPLEMENTATION |
| Implementation baseline | Ready handoff, protected artifact hashes, checked requirements checklist, and local-fallback component routing | None | Created `implementation-state.md`; added validation map to `quickstart.md` | Focused 4 passed; full runtime 77 passed; sync and whitespace checks passed |
| Implementation W1 | T003-T022, FR-001 through FR-021, and SC-001 through SC-008 | None | Updated README, setup, compatibility guide, workflow filters, canonical/generated implementation skill, and contract tests | Focused red 5 failed/4 passed; green 9 passed; both lifecycle scripts and all preflight layouts passed |
| Independent implementation review | Frozen W1 diff, requirements, task IDs, and test/walkthrough evidence | None | Corrected PowerShell and POSIX backup/replacement rollback, standalone verification, section-scoped tests, preservation boundary, host-neutral overview, and actionable preflight failure | Final reviewer approved with no material findings |
| Implementation verification | Completed T001-T026 and reviewed feature diff | None | Updated task completion state | Focused 9 passed; full combined suite 86 passed with 2 existing deprecation warnings; sync, links, task format, and diff checks passed |
| Convergence | Completed implementation against spec, plan, tasks, and constitution template | None | `tasks.md` hash remained `eafd2b28f0468642ce9f545fcd49b41fec7e204cc12f6dd19fa729a828573db7` | Converged with zero appended tasks and zero implementation cycles |
| Final implementation verification | Completed tasks, reviewed changes, convergence result, and approved path scope | None | Finalized `implementation-state.md` | 86 passed; parity, links, task completion, changed-path scope, and whitespace checks passed |
| Implementation | T001-T026, independent reviews, convergence, and fresh verification | None | Completed first-class Copilot documentation and platform-aware preflight | IMPLEMENTATION COMPLETE |
