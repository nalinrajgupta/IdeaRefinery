# Refinery state

This file is the controller state for the Refinery Quality Orchestration feature. Update it before changing `spec.md`, `plan.md`, or `tasks.md` after a material question, decision, or review finding.

## Feature status

| Field | Value |
| --- | --- |
| Feature | Refinery Quality Orchestration |
| Active Spec Kit directory | `specs/001-refinery-quality-orchestration` |
| Current stage | handoff |
| Handoff verdict | ready-for-implementation |

## Decision queue

| ID | Canonical decision | Options and trade-offs | Recommendation | Owner | Status | Source | Evidence to reopen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | Product boundary | Prompt-only; standalone runtime; hybrid skill-native orchestration plus deterministic tooling | Hybrid | user | decided | Discovery | Session-native delegation becomes unavailable or a supported in-process model API is introduced |
| D-002 | Model execution surface | External CLIs/APIs; models exposed by current session | Current-session models | user | decided | Discovery | Current-session model selection cannot satisfy required independent roles |
| D-003 | Default review profile | Single model; opt-in multi-model; default multi-model | Default multi-model for full mode | user | decided | Discovery | Ablation evals show no material quality benefit or unacceptable cost |
| D-004 | Model configurability | Fixed role assignments; per-role overrides | Defaults plus validated per-role model and reasoning overrides | user | decided | Discovery | Session roster cannot be validated before dispatch |
| D-005 | Review concurrency | Sequential; parallel with fallback | Parallel by default with automatic sequential fallback | user | decided | Discovery | Independence, consistency, or failure recovery cannot be maintained |
| D-006 | Eval gating | All scores block; deterministic and golden gates only; report-only | Deterministic and approved golden regressions block; judge scores remain non-blocking until calibrated | user | decided | Discovery | Judge rubric reaches stable human agreement and blocking is explicitly approved |
| D-007 | Primary workflow improvements | Broad equal-weight improvements; coverage-driven synthesis and bounded repair loops | Prioritize coverage-driven synthesis and bounded repair loops | user | decided | Research-informed design | Eval evidence shows another failure class dominates quality |
| D-008 | Repair authorization boundary | One up-front consent for at most two scoped repair cycles; separate approval for every repair packet | One up-front bounded consent, excluding constitution changes and material product/risk decisions | user | decided | R-006 / Architect review | New evidence that bounded consent permits unsafe or materially broader edits |
| D-009 | Failed required reviewer readiness | Permit a user waiver to reach ready with a missing perspective; require every role or approved fallback to complete before readiness | Require every required role or approved fallback to complete | user | decided: permit waiver | Spec Kit clarification / FR-037 | Evidence that ready-but-degraded is routinely mistaken for complete review or causes material downstream decisions |
| D-010 | Current-run repair authorization | Decline and keep analysis read-only; authorize at most two narrow repair cycles within D-008 boundaries | Authorize bounded repair | user | decided: authorized | Pre-analysis gate | Authorization is revoked or a proposed correction crosses an excluded boundary |

## Question registry

| ID | Canonical topic | Question | Answer or linked decision | Status | First raised by | Used by | Reopen rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | Product boundary | Should the feature remain declarative or add an executable controller? | D-001: hybrid | answered | Brainstorming | Spec v1 | |
| Q-002 | Model surface | Should v1 use external provider CLIs/APIs or current-session models? | D-002: current-session models | answered | Brainstorming | Spec v1 | |
| Q-003 | Default profile | Should three-model review be default or opt-in? | D-003: default | answered | Brainstorming | Spec v1 | |
| Q-004 | Model overrides | Should role models be fixed or overridable? | D-004: overridable | answered | Brainstorming | Spec v1 | |
| Q-005 | Parallel execution | Should review run concurrently with sequential fallback? | D-005: yes | answered | Brainstorming | Spec v1 | |
| Q-006 | Eval enforcement | Which eval classes should block CI initially? | D-006 | answered | Brainstorming | Spec v1 | |
| Q-007 | Workflow emphasis | Which research-informed improvements deserve primary focus? | D-007 | answered | Brainstorming | Spec v1 | |
| Q-008 | Repair authorization | How should the workflow obtain permission before analysis-driven artifact repairs? | D-008: one up-front bounded authorization | answered | Architect review | Spec v2 | |
| Q-009 | Missing-perspective waiver | Can a user waiver permit `READY FOR IMPLEMENTATION` after a required review role exhausts all fallbacks? | D-009: yes, with ready-but-degraded labeling and audit trail | answered | Spec Kit clarification | Spec v2 | |
| Q-010 | Current-run repair consent | May analysis trigger up to two narrow repair cycles under the settled D-008 safety boundary? | D-010: yes | answered | Pre-analysis gate | Analysis and bounded repair | |

## Review ledger

| ID | Reviewer | Severity | Artifact / section | Evidence | Smallest proposed change | Human decision? | Resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | CEO | medium | Success Criteria | Current criteria measure process proxies but not whether implementation agents need new material decisions | Add downstream material-decision escalation rate to the eval and success criteria | no | accepted |
| R-002 | Product | high | FR-003–FR-006; User Story 1 | Override capability has no invocation/configuration surface, precedence, or backward-compatibility contract | Define invocation and repository configuration surfaces, precedence, validation timing, default compatibility, and resolved-config preview | no | accepted |
| R-003 | Product | high | FR-005, FR-014, FR-019–FR-021, FR-029 | Failed required perspectives and degraded synthesis have no user-visible handoff policy | Define degraded status, notice, coverage impact, continuation rule, and handoff blocking conditions | no | accepted |
| R-004 | Product | medium | FR-020; User Story 2 | “Best-suited role” for targeted coverage follow-up is not deterministic | Add coverage-area ownership map, tie-breaker, and recorded selection rationale | no | accepted |
| R-005 | Product | medium | FR-006, FR-018, FR-021, FR-029; state template | Required configuration, coverage, and repair history have no canonical persisted locations | Extend the state contract and canonical artifacts; resolved together with R-011 | no | accepted |
| R-006 | Architect | critical | FR-022; safety boundary | Automatic repair conflicts with the existing explicit-approval requirement for analysis-driven edits | Choose bounded up-front consent or per-packet approval; never include constitution or material product/risk decisions | yes | accepted (D-008: up-front bounded authorization) |
| R-007 | Architect | high | FR-022; clarification interface | Clarification has no blocker/critical/high finding envelope, so it cannot deterministically trigger severity-based repair | Limit repair findings to analysis; accepted clarifications invalidate downstream artifacts and unanswered high-impact questions become decisions | no | accepted |
| R-008 | Architect | high | FR-009, FR-012, FR-018–FR-019 | Finding-only reviewer envelopes cannot prove reviewed-with-no-finding coverage | Assign stable coverage IDs before fan-out and require per-item coverage attestations with evidence and linked findings | no | accepted |
| R-009 | Architect | high | FR-024, FR-026, FR-028 | Selective regeneration lacks a complete Spec Kit artifact dependency graph, checkpoint, validation, and rollback behavior | Define artifact DAG/invalidation, pre-repair checkpoint, staged regeneration, atomic promotion, and rollback | no | accepted |
| R-010 | Architect | high | FR-017, FR-025–FR-026 | Rephrased findings can reset repair counters because canonical identity has no cross-run lineage rule | Persist root-finding identity plus aliases and caused-by/supersedes lineage across analysis runs | no | accepted |
| R-011 | Architect | high | FR-029–FR-030, SC-007, SC-011 | Conversation-only results and Markdown summaries cannot guarantee crash-consistent resume or exact reuse | Define a versioned feature-local run store, immutable inputs/results/events, hashes, atomic writes, and stage commit markers | no | accepted |
| R-012 | Architect | high | FR-031–FR-036 | Ordinary CI cannot execute session-native live multi-model evals | Split deterministic replay CI from session-native live benchmarks and promote approved bundles into replay fixtures | no | accepted |
| R-013 | Architect | medium | FR-005; fallback behavior | Fallback candidates, effort clamping, dispatch-time validation, and exhaustion are underspecified | Define ordered role fallbacks, effort rules, revalidation, and terminal disposition | no | accepted |
| R-014 | Architect | medium | FR-011, FR-013; worker boundary | Instruction-only read-only workers do not prevent accidental shared artifact mutation | Require immutable snapshots plus isolation or protected-artifact pre/post hashes and abort-on-drift | no | accepted |
| R-015 | Spec Kit | high | `spec.md` configuration contract; `contracts/config.schema.json`; `quickstart.md` | The approved invocation surface is `overrides.roles`, but the only machine contract and validation example expose top-level `roles` | Add a dedicated invocation wrapper schema and make deterministic test input explicitly serialize that block | no | accepted — resolved by RP-001 cycle 1 |
| R-016 | Spec Kit | high | `plan.md` source tree and component ownership; `tasks.md` | Existing authoritative `references/orchestration-contract.md` and `references/refinery-state-template.md` would retain legacy sequential/state semantics because no task owns their update | Add both reference artifacts to the planned structure and one integration task that synchronizes them after story work | no | accepted — resolved by RP-002 cycle 1 |
| R-017 | Spec Kit | high | `plan.md` performance goal; `tasks.md` | The measurable 250 ms validation target has no executable regression task, violating the buildable-requirement coverage gate | Add a deterministic performance regression task with representative artifacts and a stable CI threshold | no | accepted — resolved by RP-003 cycle 1 |
| R-018 | Spec Kit | medium | `tasks.md` T066; FR-005 | The live benchmark task says to run one comparison but does not encode the approved `skipped-unavailable` baseline outcome | State the skip outcome directly in T066 | no | deferred — non-blocking cleanup before implementation |
| R-019 | Spec Kit | low | `.specify/memory/constitution.md`; `plan.md` | The constitution is still a placeholder, so no project-wide normative principles can be checked | Ratify governance separately if desired; do not change it through this feature repair | yes | deferred — separate governance decision |

## Repair ledger

| Packet | Root finding | Cycle | Authorization | Affected artifacts | Smallest correction | Completion check | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RP-001 | ROOT-invocation-contract | 1 | D-010 bounded | plan, contracts, quickstart, tasks | Add and reference an `overrides.roles` invocation schema without changing precedence or model policy | Schema parses; plan/quickstart/tasks agree with FR-003 | promoted — risk decreased |
| RP-002 | ROOT-reference-sync | 1 | D-010 bounded | plan, tasks | Give both existing workflow reference files explicit implementation ownership | Planned tree and one task name both reference artifacts | promoted — risk decreased |
| RP-003 | ROOT-validation-performance | 1 | D-010 bounded | tasks | Add one deterministic test task for the existing 250 ms target | Task has ID, path, threshold, and CI linkage | promoted — risk decreased |

## Coverage matrix

Coverage items will be derived from Spec v1 before synthesis. Each applicable item will record risk, reviewing roles, evidence, canonical findings, resolution, and final task coverage. Missing review evidence is a blind spot, not a pass.

| Coverage ID | Area | Risk | Applicable | Reviewer evidence | Findings | Resolution | Task coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| COV-001 | User value and positioning | high | yes | CEO and Product examined value, positioning, and primary journey | R-001 | accepted for Spec v2 | T054, T056, T060, T066 |
| COV-002 | Invocation, configuration, and compatibility | high | yes | Product examined override UX; Architect examined fallback determinism | R-002, R-013, R-015 | accepted and repair-validated | T003, T014–T023, T062 |
| COV-003 | Review independence and concurrency | high | yes | Product found no journey gap; Architect examined isolation and failure paths | R-014 | accepted for Spec v2 | T015, T017, T020–T023, T043, T045, T050 |
| COV-004 | Coverage-driven synthesis | high | yes | All reviewers examined coverage; Product and Architect identified selection and attestation gaps | R-004, R-008 | accepted for Spec v2 | T024–T033 |
| COV-005 | Bounded repair safety and convergence | critical | yes | Product found loop scope sound; Architect identified authorization, trigger, DAG, and identity gaps | R-006, R-007, R-009, R-010 | all accepted for Spec v2 | T034–T042 |
| COV-006 | Reliability, resume, and crash consistency | high | yes | Product identified degraded experience; Architect identified run-store gap | R-003, R-005, R-011 | accepted for Spec v2 | T009, T010, T012, T040, T044–T050 |
| COV-007 | Eval strategy and CI | high | yes | CEO and Product found metric set aligned; Architect identified live-vs-replay execution gap | R-001, R-012 | accepted for Spec v2 | T051–T061, T064–T066 |
| COV-008 | Security and trust boundaries | medium | yes | Architect found no credential surface expansion and identified worker mutation boundary | R-014 | accepted for Spec v2 | T009, T015, T021, T045, T063 |
| COV-009 | Distribution and rollout | medium | yes | Architect found existing skill/symlink distribution sufficient | R-016 | accepted and repair-validated | T001–T005, T061, T062, T068 |
| COV-010 | Operations and auditability | high | yes | Product and Architect examined persisted state, traceability, and recovery | R-005, R-011 | accepted for Spec v2 | T010, T012, T031, T040, T044, T047–T049 |
| COV-011 | Test strategy and task traceability | high | yes | Product found eval coverage sound; Architect found live/replay split gap | R-012, R-017 | accepted and repair-validated | T011–T017, T024–T027, T034–T037, T043–T046, T051–T067 |

## Resolved run configuration

| Role | Default model | Reasoning effort | Override | Resolved assignment | Status |
| --- | --- | --- | --- | --- | --- |
| CEO reviewer | `gpt-5.5` | high | none | `gpt-5.5` / high | validated available |
| Product reviewer | `gpt-5.6-terra` | high | none | `gpt-5.6-terra` / high | validated available |
| Architect reviewer | `gpt-5.6-sol` | high | none | `gpt-5.6-sol` / high | validated available |
| Eval runner | `gpt-5.6-luna` | medium | none | `gpt-5.6-luna` / medium | validated available |
| Regression baseline | `gpt-5.4` | medium | none | `gpt-5.4` / medium | validated available |

- Review concurrency: 3 workers when available; automatic bounded queue otherwise.
- Shared-state policy: workers are read-only; controller is the sole writer.
- Worker retry ceiling: 1 retry per role.
- Coverage follow-up ceiling: 1 targeted follow-up per synthesis pass.
- Repair ceiling: 2 cycles per canonical finding.

## Active review dispatch

- Frozen Spec v1 SHA-256: `ec33ac05e7301638881aca8c53f5cbd34860fd1049fc56ea4af946beccfb10ef`
- Review mode: three independent read-only workers in parallel.
- Shared stage brief: D-001 through D-007 are settled; Q-001 through Q-007 are answered; there are no open user decisions or unresolved prior findings.
- Worker contract: return findings only; do not edit artifacts; do not ask the user; do not read another reviewer's output; cite repository or spec evidence; identify coverage area and human-decision need.
- Synthesized Spec v2 SHA-256: `063202baa12a5e06c7066fcc3f5dc9e9ec71ac287593d4fc035aabc7f4416ee6`.
- Clarified Spec v2 SHA-256: `582c20910c1cd7b5ab917a065823f09f17e6fe9782eba8392a07cd665265dcdd`.
- Implementation plan SHA-256: `052c1a824ced110bc696de50fe71b5401ae27c7793531e2542e4562755c3a1b0`.
- Task backlog SHA-256: `8721a19232f8f550ff35c3e055f4bd9ff8388f3641b0fd0c1eaf9f7b60d5a2b6`.

## Stage log

| Stage | Inputs supplied | New IDs | Artifact changes | Outcome |
| --- | --- | --- | --- | --- |
| setup | Target repo, approved Spec Kit initialization, feature name | none | Initialized `.specify/` and `.agents/skills/` | Spec Kit ready; no feature branch created |
| discovery | Repository context and user request | D-001–D-007; Q-001–Q-007 | Approved architecture and research-informed design captured in Spec v1 | Hybrid session-native multi-model design approved |
| spec-v1 | All settled decisions and approved design sections | none | Created `spec.md`, quality checklist, active feature pointer, and controller state | Spec v1 ready for independent review |
| review | D-001–D-007, Q-001–Q-007, frozen Spec v1 hash, identical worker contract | R-001–R-014; D-008; Q-008 | Persisted independent CEO, Product, and Architect findings; populated coverage matrix | One critical user decision; all other findings accepted for Spec v2 |
| synthesis | D-001–D-008, Q-001–Q-008, R-001–R-014, completed coverage matrix | none | Updated `spec.md` to Spec v2; resolved every review finding; refreshed requirements checklist | All review findings accepted; no open decision remains |
| clarify | D-001–D-008 and Q-001–Q-008 supplied; FR-037 waiver semantics identified as new | D-009; Q-009 | Added one clarification to `spec.md`; checklist remained 16/16 | One question asked and answered; no other critical ambiguity found |
| plan | Clarified Spec v2, settled decisions, review ledger, coverage matrix, unratified constitution placeholder | none | Created `plan.md`, `research.md`, `data-model.md`, five JSON Schema contracts, and `quickstart.md` | Hybrid technical design complete; no unresolved technical clarification; constitution left unchanged |
| tasks | Spec v2 and all plan/supporting artifacts | none | Created 66 dependency-ordered tasks and populated coverage-to-task mappings | Every task has required format and every coverage area has implementation/test ownership |
| analysis-authorization | D-008 boundary and complete Spec Kit artifacts | D-010; Q-010 | Recorded explicit current-run bounded repair consent | Up to two narrow material repair cycles authorized; excluded decisions still require separate approval |
| analyze-0 | Constitution placeholder, Spec v2, plan/supporting artifacts, and 66-task backlog | R-015–R-019 | Read-only; no artifact mutations during analysis | 3 high gaps authorized for cycle 1; 2 lower-severity notes deferred |
| repair-1 | D-010, RP-001–RP-003, R-015–R-017 | none | Added invocation schema; aligned plan/quickstart/tasks; added reference-sync and performance tasks | All three packets promoted; unresolved material risk decreased; no new high contradiction |
| analyze-1 | Constitution placeholder, unchanged Spec v2, repaired plan/supporting artifacts, and 68-task backlog | none | Read-only; no artifact mutations during analysis | 53/53 buildable requirements covered; 68/68 tasks traceable; zero critical/high findings |
| handoff | All decisions, reviews, repair evidence, and final analysis | none | Updated controller state only | Ready; one medium cleanup and separate constitution-governance note remain deferred |

## Implementation execution

| Field | Value |
| --- | --- |
| Runtime | `idea-refinery-full` Python 3.11 package with PyYAML/jsonschema |
| TDD status | 77 deterministic tests passing; contract, property, integration, replay, security, and latency suites included |
| Parallel lanes | Coverage/findings, bounded repair/invalidation, and eval/readiness lanes completed; shared CLI/run-store integration completed by controller |
| Package verification | Source distribution and wheel built successfully; schemas/defaults present in both |
| Completed tasks | 67 of 68 |
| Remaining tasks | T066 requires a live session benchmark |
