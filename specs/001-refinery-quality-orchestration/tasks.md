# Tasks: Refinery Quality Orchestration

**Input**: Design documents from `specs/001-refinery-quality-orchestration/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required by FR-031–FR-036 and SC-001–SC-012. Story test tasks precede their implementation tasks.

**Organization**: Tasks are grouped by user story. Requirement IDs in task descriptions provide direct implementation traceability.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with adjacent marked tasks because it owns different files and has no unmet dependency
- **[Story]**: Maps to a user story in `spec.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the embedded package, schema source of truth, and test entry points.

- [X] T001 Create the Python 3.11 package metadata and runtime/dev dependency groups in `idea-refinery-full/pyproject.toml`
- [X] T002 [P] Create package exports and version constants in `idea-refinery-full/src/idea_refinery/__init__.py`
- [X] T003 [P] Mirror the six approved v1 contracts from `specs/001-refinery-quality-orchestration/contracts/` into `idea-refinery-full/schemas/`
- [X] T004 [P] Add pytest configuration and shared temporary feature/run-store fixtures in `idea-refinery-full/tests/conftest.py`
- [X] T005 Add a package command entry point and subcommand placeholders in `idea-refinery-full/src/idea_refinery/cli.py`

**Checkpoint**: Package installs locally, schemas are distributable with it, and pytest discovers the suite.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared types, validation, identity, and durable storage used by all stories.

**Critical**: Complete this phase before story work begins.

- [X] T006 [P] Define enums, immutable dataclasses, and canonical serialization helpers for roles, statuses, hashes, and schema versions in `idea-refinery-full/src/idea_refinery/types.py` (FR-006, FR-012, FR-017)
- [X] T007 [P] Implement stable coded errors and human/actionable rendering in `idea-refinery-full/src/idea_refinery/errors.py` (FR-004, FR-014)
- [X] T008 [P] Implement schema loading, Draft 2020-12 validation, and semantic-validator registration in `idea-refinery-full/src/idea_refinery/schemas.py` (FR-012, FR-023, FR-029)
- [X] T009 Implement content hashing, canonical JSON, atomic file replacement, and directory fsync helpers in `idea-refinery-full/src/idea_refinery/io.py` (FR-011, FR-024, FR-029)
- [X] T010 Implement versioned run creation, manifest mutation, immutable object storage, JSONL event append, and stage commit markers in `idea-refinery-full/src/idea_refinery/run_store.py` (FR-029, FR-030)
- [X] T011 [P] Add contract tests that validate every bundled schema and enforce canonical equality with feature contracts in `idea-refinery-full/tests/contract/test_schemas.py` (FR-012, FR-023, FR-029, FR-031)
- [X] T012 [P] Add property tests for canonical serialization, stable hashes, atomic replacement, and monotonic trace sequencing in `idea-refinery-full/tests/property/test_persistence_invariants.py` (FR-029, FR-030)
- [X] T013 Add CLI plumbing for structured input/output, stable exit codes, and `--run-dir` handling in `idea-refinery-full/src/idea_refinery/cli.py` (FR-029, FR-031)

**Checkpoint**: All stories can rely on versioned contracts, canonical identities, atomic writes, and append-only trace events.

---

## Phase 3: User Story 1 — Run Independent Multi-Model Reviews (Priority: P1) — MVP

**Goal**: Resolve session-native role assignments and accept three isolated, attributable review envelopes while preserving the existing invocation.

**Independent Test**: Resolve bundled and overridden configurations against full/reduced rosters, then validate three frozen-input result envelopes and reject unavailable explicit models, incomplete attestations, or artifact drift.

### Tests for User Story 1

- [X] T014 [P] [US1] Add `overrides.roles` invocation-schema, bundled/repository/invocation precedence, fallback, effort-clamping, and unavailable-explicit-model cases in `idea-refinery-full/tests/unit/test_config.py` (FR-001–FR-006)
- [X] T015 [P] [US1] Add completed, failed, incomplete-attestation, mismatched-dispatch, and protected-drift contract cases in `idea-refinery-full/tests/contract/test_review_envelopes.py` (FR-009–FR-014)
- [X] T016 [P] [US1] Add full and reduced session roster fixtures in `idea-refinery-full/tests/fixtures/rosters/full.json` and `idea-refinery-full/tests/fixtures/rosters/reduced.json` (FR-001, FR-004, FR-005)
- [X] T017 [P] [US1] Add an end-to-end frozen three-role dispatch/result acceptance test in `idea-refinery-full/tests/integration/test_review_dispatch.py` (FR-007–FR-014)

### Implementation for User Story 1

- [X] T018 [P] [US1] Add the approved five-role defaults, reasoning efforts, fallbacks, concurrency, retry, and timeout limits in `idea-refinery-full/defaults/config.yaml` (FR-002, FR-005, FR-006)
- [X] T019 [US1] Implement source precedence, roster-snapshot validation, explicit-override semantics, ordered fallback, and effort clamping in `idea-refinery-full/src/idea_refinery/config.py` (FR-001–FR-006)
- [X] T020 [P] [US1] Implement immutable stage-brief creation and cross-review information exclusion in `idea-refinery-full/src/idea_refinery/briefs.py` (FR-009, FR-010)
- [X] T021 [US1] Implement review-envelope structural and semantic validation, dispatch matching, and protected-hash checks in `idea-refinery-full/src/idea_refinery/envelopes.py` (FR-011, FR-012, FR-014)
- [X] T022 [US1] Add `resolve-config`, `prepare-review`, and `validate-envelope` commands in `idea-refinery-full/src/idea_refinery/cli.py` (FR-001, FR-004, FR-006, FR-014)
- [X] T023 [US1] Update model-roster capture, resolved-config preview, immutable review briefs, per-role override syntax, and session-native dispatch instructions in `idea-refinery-full/SKILL.md` (FR-001–FR-014)

**Checkpoint**: Existing invocation uses the approved defaults; valid overrides work; independent results are attributable and contract-complete.

---

## Phase 4: User Story 2 — Synthesize by Coverage, Not Volume (Priority: P1)

**Goal**: Prove systematic review coverage, canonicalize duplicate findings, and target no more than one follow-up at uncovered high-risk areas.

**Independent Test**: Replay known omissions and duplicate findings; verify all applicable items terminate with evidence or a blind-spot disposition and only the deterministic owner receives a focused follow-up.

### Tests for User Story 2

- [X] T024 [P] [US2] Add coverage derivation, state transition, applicability, and evidence-completeness tests in `idea-refinery-full/tests/unit/test_coverage.py` (FR-015, FR-018, FR-019)
- [X] T025 [P] [US2] Add semantic duplicate, alias, causal-lineage, and completion-criterion identity tests in `idea-refinery-full/tests/unit/test_findings.py` (FR-016, FR-017)
- [X] T026 [P] [US2] Add ownership fallback, degraded-role tie-break, and one-follow-up ceiling tests in `idea-refinery-full/tests/unit/test_followup_selection.py` (FR-020)
- [X] T027 [P] [US2] Add a seeded coverage-gap replay fixture and expected matrix in `idea-refinery-full/tests/fixtures/replay/coverage-gap/` (SC-001, SC-002)

### Implementation for User Story 2

- [X] T028 [P] [US2] Implement stable coverage taxonomy derivation, ownership assignment, evidence aggregation, and matrix transitions in `idea-refinery-full/src/idea_refinery/coverage.py` (FR-015, FR-018, FR-019)
- [X] T029 [P] [US2] Implement root-finding canonicalization, aliases, attribution retention, and acyclic caused-by/supersedes lineage in `idea-refinery-full/src/idea_refinery/findings.py` (FR-016, FR-017)
- [X] T030 [US2] Implement deterministic blind-spot ranking, primary/secondary selection, and one-follow-up enforcement in `idea-refinery-full/src/idea_refinery/coverage.py` (FR-020)
- [X] T031 [US2] Implement finding/blind-spot dispositions and readiness coverage gates in `idea-refinery-full/src/idea_refinery/synthesis.py` (FR-021, FR-037, FR-040)
- [X] T032 [US2] Add `build-coverage` and `synthesize` commands in `idea-refinery-full/src/idea_refinery/cli.py` (FR-015–FR-021)
- [X] T033 [US2] Update reviewer attestation, coverage-driven synthesis, targeted follow-up, and single-writer ledger instructions in `idea-refinery-full/SKILL.md` (FR-012–FR-021, especially FR-013)

**Checkpoint**: Synthesis success is based on evidenced coverage and dispositions, not finding count or reviewer verbosity.

---

## Phase 5: User Story 3 — Repair Material Gaps Without Looping (Priority: P1)

**Goal**: Correct authorized material analysis findings through minimal staged regeneration while enforcing the two-cycle and safety stop conditions.

**Independent Test**: Replay repairable, persistent, rephrased, scope-changing, and regression-introducing findings; verify selective invalidation, atomic rollback/promotion, root-based limits, and decision escalation.

### Tests for User Story 3

- [X] T034 [P] [US3] Add artifact DAG and transitive invalidation tests in `idea-refinery-full/tests/unit/test_invalidation.py` (FR-024, FR-039)
- [X] T035 [P] [US3] Add bounded authorization, excluded-decision classes, cycle limit, recurring-root, and new-risk stop tests in `idea-refinery-full/tests/unit/test_repair.py` (FR-022–FR-028, FR-038)
- [X] T036 [P] [US3] Add staged validation failure, rollback, and successful atomic promotion integration tests in `idea-refinery-full/tests/integration/test_repair_transaction.py` (FR-024, FR-026, FR-028)
- [X] T037 [P] [US3] Add repair-limit, alias-reset attack, and new-contradiction replay fixtures in `idea-refinery-full/tests/fixtures/replay/repair-limit/` (SC-002, SC-003)

### Implementation for User Story 3

- [X] T038 [P] [US3] Implement the Spec Kit artifact DAG, change classification, and downstream invalidation calculator in `idea-refinery-full/src/idea_refinery/invalidation.py` (FR-024, FR-039)
- [X] T039 [US3] Implement repair-packet validation, bounded authorization classes, per-root counters, risk-delta checks, and early-stop policy in `idea-refinery-full/src/idea_refinery/repair.py` (FR-022–FR-028, especially FR-025 and FR-027, FR-038)
- [X] T040 [US3] Implement checkpoint creation, isolated staged output validation, atomic promotion, and rollback in `idea-refinery-full/src/idea_refinery/run_store.py` (FR-024, FR-029)
- [X] T041 [US3] Add `prepare-repair`, `validate-repair`, `promote-repair`, and `rollback-repair` commands in `idea-refinery-full/src/idea_refinery/cli.py` (FR-022–FR-028)
- [X] T042 [US3] Update pre-analysis consent, repair-packet scope, selective Spec Kit regeneration, and hard-stop instructions in `idea-refinery-full/SKILL.md` (FR-022–FR-028, FR-038, FR-039)

**Checkpoint**: No root finding can exceed two automatic corrections or expand beyond explicit authorization; failed corrections leave live artifacts unchanged.

---

## Phase 6: User Story 4 — Complete Reviews Efficiently and Recoverably (Priority: P2)

**Goal**: Parallelize independent review safely, queue under reduced capacity, resume exact valid work, and report degraded or waived perspectives truthfully.

**Independent Test**: Exercise capacity 3/1, timeout/fallback exhaustion, interruption, stale hashes, illegal worker writes, and a user waiver; verify deterministic outputs and correct readiness status.

### Tests for User Story 4

- [X] T043 [P] [US4] Add completion-order permutation and capacity-independent aggregation tests in `idea-refinery-full/tests/property/test_concurrency_invariants.py` (FR-007, FR-008)
- [X] T044 [P] [US4] Add exact resume reuse/invalidation, auditable provenance, and partial-stage recovery tests in `idea-refinery-full/tests/integration/test_resume.py` (FR-029, FR-030, SC-007, SC-011)
- [X] T045 [P] [US4] Add timeout, retry, fallback, exhaustion, drift-abort, and waiver journey tests in `idea-refinery-full/tests/integration/test_degraded_runs.py` (FR-005, FR-011, FR-037)
- [X] T046 [P] [US4] Add interrupted-run and exhausted-role replay fixtures in `idea-refinery-full/tests/fixtures/replay/interrupted-run/` and `idea-refinery-full/tests/fixtures/replay/failed-role/` (FR-030, FR-037)

### Implementation for User Story 4

- [X] T047 [US4] Implement resume eligibility comparison across spec, brief, role config, schemas, protected hashes, and stage identity in `idea-refinery-full/src/idea_refinery/run_store.py` (FR-030)
- [X] T048 [US4] Implement failed-role, degraded-fallback, waived-perspective, ready, and ready-degraded verdict construction in `idea-refinery-full/src/idea_refinery/readiness.py` (FR-037, FR-040)
- [X] T049 [US4] Add `resume-plan`, `validate-run`, and `readiness` commands in `idea-refinery-full/src/idea_refinery/cli.py` (FR-029, FR-030, FR-037, FR-040)
- [X] T050 [US4] Update parallel-slot detection, sequential queuing, retry/fallback dispatch, resume, drift abort, and waiver-reporting instructions in `idea-refinery-full/SKILL.md` (FR-005, FR-007, FR-008, FR-011, FR-030, FR-037)

**Checkpoint**: Capacity and completion order do not change semantics; interruption reuses only exact committed work; degraded readiness is explicit and auditable.

---

## Phase 7: User Story 5 — Measure Workflow Quality Continuously (Priority: P2)

**Goal**: Block deterministic regressions, report uncalibrated quality metrics without blocking, and compare the default profile against a single-model control.

**Independent Test**: Run CI replay cases offline, deliberately break an invariant, score an approved live bundle, and verify promotion is explicit and immutable.

### Tests for User Story 5

- [X] T051 [P] [US5] Add deterministic scoring tests for seeded recall, unsupported claims, coverage, diversity, questions, convergence, and traceability in `idea-refinery-full/tests/unit/test_eval_scoring.py` (FR-031–FR-035)
- [X] T052 [P] [US5] Add blocking-policy calibration and human-agreement threshold tests in `idea-refinery-full/tests/unit/test_calibration.py` (FR-032, FR-036, SC-009)
- [X] T053 [P] [US5] Add immutable, approval-required live-bundle promotion tests in `idea-refinery-full/tests/integration/test_fixture_promotion.py` (FR-034)
- [X] T054 [P] [US5] Add typical, edge, adversarial, fallback, duplicate-question, and downstream-decision golden cases in `idea-refinery-full/tests/fixtures/golden/` (FR-035, FR-041, SC-004)

### Implementation for User Story 5

- [X] T055 [P] [US5] Implement replay loading, invariant comparison, and deterministic failure evidence in `idea-refinery-full/src/idea_refinery/evals/replay.py` (FR-031, FR-035)
- [X] T056 [P] [US5] Implement quality, latency, effort, coverage, and requirement-task traceability scoring in `idea-refinery-full/src/idea_refinery/evals/scoring.py` (FR-032–FR-034, FR-041)
- [X] T057 [P] [US5] Implement human-label calibration status and blocking-policy enforcement in `idea-refinery-full/src/idea_refinery/evals/calibration.py` (FR-032, FR-036)
- [X] T058 [US5] Implement explicit live-bundle review and immutable replay-fixture promotion in `idea-refinery-full/src/idea_refinery/evals/promotion.py` (FR-034)
- [X] T059 [US5] Add `eval-replay`, `eval-score`, `calibrate`, and `promote-bundle` commands in `idea-refinery-full/src/idea_refinery/cli.py` (FR-031–FR-036)
- [X] T060 [US5] Add live default-versus-control dispatch, downstream-decision capture, and non-blocking judge instructions in `idea-refinery-full/SKILL.md` (FR-032, FR-034, FR-036, FR-041)

**Checkpoint**: CI is fully offline and deterministic; live metrics are visible, comparable, and promotion-controlled.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Complete distribution, documentation, security checks, and end-to-end validation.

- [X] T061 [P] Add the offline deterministic test, performance, coverage, schema, and replay gates in `.github/workflows/refinery-evals.yml` (FR-031, SC-008)
- [X] T062 [P] Document configuration shape, precedence, defaults, override examples, and degraded verdicts in `README.md` (FR-003–FR-006, FR-037, FR-040)
- [X] T063 [P] Add threat-boundary tests for YAML safe loading, path containment, oversized envelopes, lineage cycles, and artifact traversal in `idea-refinery-full/tests/contract/test_security_boundaries.py` (FR-011, FR-029)
- [X] T064 Add a requirement-to-task and task-to-requirement traceability checker in `idea-refinery-full/src/idea_refinery/evals/traceability.py` (FR-033, SC-005)
- [X] T065 Run every deterministic scenario in `specs/001-refinery-quality-orchestration/quickstart.md` and record validation evidence in `specs/001-refinery-quality-orchestration/validation.md`
- [ ] T066 Run one non-blocking session-native three-model versus single-model benchmark and store the reviewable bundle under `specs/001-refinery-quality-orchestration/evals/live/` (FR-034, SC-006, SC-010)
- [X] T067 [P] Add a deterministic regression test asserting configuration and representative-envelope validation complete within 250 ms in `idea-refinery-full/tests/performance/test_validation_latency.py` and wire it through T061
- [X] T068 Synchronize parallel review, coverage, run-store pointers, bounded repair, degraded readiness, and eval semantics in `idea-refinery-full/references/orchestration-contract.md` and `idea-refinery-full/references/refinery-state-template.md` (FR-006–FR-041)

---

## Dependencies & Execution Order

### Phase dependencies

- Setup (Phase 1) has no dependency.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- US1 depends on Foundational and is the MVP/session boundary.
- US2 and US3 depend on US1’s validated envelopes/configuration, but can run in parallel with each other after US1.
- US4 depends on US1 and the run-store foundation; its readiness integration should consume US2 before final completion.
- US5 depends on stable outputs from US1–US4 for complete replay coverage, though scoring primitives and fixtures can begin after Foundational.
- Polish depends on all selected stories.

### User story dependency graph

```text
Setup → Foundation → US1 ─┬→ US2 ─┐
                          ├→ US3 ─┼→ US5 → Polish
                          └→ US4 ─┘
```

### Parallel ownership lanes

- After schemas freeze: config/envelopes (US1), then coverage/findings (US2) and invalidation/repair (US3) may use separate files.
- Persistence/resume work owns `run_store.py`; sequence T040 and T047 rather than editing it concurrently.
- Skill integration tasks T023, T033, T042, T050, and T060 are sequential because they all own `SKILL.md`.
- Replay/scoring/calibration modules and their test files can be implemented in parallel once result shapes stabilize.

## Parallel Examples

### US1

```text
T014 config tests | T015 envelope tests | T016 roster fixtures | T017 dispatch integration test
T018 bundled defaults | T020 immutable briefs
```

### US2 and US3 after US1

```text
Lane A: T024 → T028 → T030 (coverage)
Lane B: T025 → T029 (finding identity)
Lane C: T034 → T038 (artifact invalidation)
Lane D: T035/T036/T037 → T039 → T040 (bounded repair)
```

### US5

```text
T051 → T056 (scoring)
T052 → T057 (calibration)
T053 → T058 (promotion)
T054 → T055 (fixture/replay)
```

## Implementation Strategy

### MVP first

1. Complete Setup and Foundational phases.
2. Complete US1 and demonstrate current-session roster resolution, defaults/overrides, and isolated three-role result validation.
3. Stop and validate the US1 independent test before adding synthesis or automatic repair behavior.

### Incremental delivery

1. Add US2 to make multi-model output coverage-driven and auditable.
2. Add US3 as a separately gated safety capability; keep analysis read-only until its consent and rollback tests pass.
3. Add US4 recovery/degradation behavior.
4. Add US5 deterministic gates first, then run live benchmarks as non-blocking evidence.

## Notes

- Tests listed before implementation should be written first and observed failing for the intended reason.
- `[P]` never authorizes concurrent edits to the same file.
- Do not implement provider APIs, model CLIs, credentials, application code, or automatic live-fixture promotion.
- A future constitution ratification requires a fresh plan gate check before implementation continues.
