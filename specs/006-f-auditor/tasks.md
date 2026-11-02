---
description: "Dependency-ordered implementation tasks for f-auditor"
---

# Tasks: f-auditor Functional Session Auditor

**Inputs**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/audit-interface.md`, `contracts/analysis-result.schema.json`, and `quickstart.md` in `specs/006-f-auditor/`.

**Scope**: These are implementation instructions, not completed work. No implementation, commits, scheduling, external issues, or deployments are authorized by this document. Tests are required by the spec and plan: write each test, observe it fail for the intended missing behavior, implement, then verify it passes. Paths are relative to the repository root. `[P]` indicates disjoint write sets and no dependency on another task in that parallel group; do not infer that entire stories can run concurrently.

## Phase 1: Setup

- [ ] T001 Create the `f-auditor/pyproject.toml` Python 3.11+ package, `f-auditor/uv.lock`, `f-auditor/src/f_auditor/__init__.py`, and `f-auditor/tests/` layout with the existing runtime's dependency ranges and a `f-auditor` console entry point (FR-001, FR-016, FR-017).
- [ ] T002 Copy the approved analysis contract into `f-auditor/schemas/analysis-result.schema.json` and configure inclusion as a package asset; preserve the feature contract at `specs/006-f-auditor/contracts/analysis-result.schema.json` (FR-006, FR-020).

## Phase 2: Foundational contracts and safety

**Checkpoint**: Complete shared contracts before story-specific implementation.

### Tests first

- [ ] T003 [P] Add configuration and time-boundary tests in `f-auditor/tests/unit/test_config.py` for root/backlog resolution, CWD independence, explicit destinations, UTC window boundaries, limits and invalid prerequisites (FR-002, FR-004, FR-007, FR-017, SC-010).
- [ ] T004 [P] Add sanitization and injection tests in `f-auditor/tests/unit/test_evidence_safety.py` covering representative credentials, error paths, hostile transcript instructions and persistence/console/runtime boundaries (FR-013, SC-007).
- [ ] T005 [P] Add immutable run and recovery tests in `f-auditor/tests/unit/test_run_store.py` for identity hashes, exact resume, incomplete analysis, pre/post-promotion interruption and idempotent committed evidence (FR-012, FR-014, FR-015).
- [ ] T006 [P] Add schema and evidence contract tests in `f-auditor/tests/contract/test_analysis_result.py` for `f-auditor/schemas/analysis-result.schema.json`, origin IDs, exact sanitized excerpts, chunk attestations and invalid issue references (FR-006, FR-013, FR-020).

### Implementation

- [ ] T007 Implement configuration, absolute canonical paths, runtime limits, a single UTC 24-hour boundary and actionable validation in `f-auditor/src/f_auditor/config.py` (FR-002, FR-004, FR-007, FR-017).
- [ ] T008 Implement normalized run/session/message/evidence structures, pre-output redaction, provenance and prompt-injection isolation in `f-auditor/src/f_auditor/evidence.py`; omit hidden reasoning and credentials without discarding relevant visible context (FR-006, FR-013, FR-019).
- [ ] T009 Implement sanitized immutable bundles, version/hash identity, run dispositions and crash-aware commit/resume records in `f-auditor/src/f_auditor/run_store.py`; persist no raw transcripts (FR-012, FR-014, FR-015).
- [ ] T010 Implement schema, exact-citation, issue-reference and complete-chunk validation in `f-auditor/src/f_auditor/analysis.py`; reject unsupported excerpts, incomplete coverage and fabricated timestamps (FR-006, FR-013, FR-020).
- [ ] T011 Run `uv run --project f-auditor --extra dev pytest f-auditor/tests/unit/test_config.py f-auditor/tests/unit/test_evidence_safety.py f-auditor/tests/unit/test_run_store.py f-auditor/tests/contract/test_analysis_result.py` and fix failures before story implementations (FR-013, FR-015, FR-020).

## Phase 3: User Story 1 — Audit relevant recent sessions (P1)

**Goal**: Discover, select and contextually analyze whole eligible Hermes and Codex conversations without claiming coverage for uncertain histories.

**Independent test**: Prepared host fixtures verify eligibility, exclusions, whole-session context, positive/negative analysis quality and partial coverage without requiring a shared backlog implementation. Native compatibility probes are a separate required gate, not a fixture substitute.

### Tests first

- [ ] T012 [P] [US1] Create Hermes fixtures and adapter tests in `f-auditor/tests/unit/test_hermes_sources.py` and `f-auditor/tests/fixtures/hermes/` for profiles, read-only SQLite access, schema changes, lifecycle/liveness, compression, forks, inaccessible and incomplete histories (FR-003, FR-019, SC-001, SC-005).
- [ ] T013 [P] [US1] Create Codex fixtures and adapter tests in `f-auditor/tests/unit/test_codex_sources.py` and `f-auditor/tests/fixtures/codex/` for legacy/modern formats, complete pagination, missing closure proof, open/unknown states and malformed sources (FR-003, FR-019, SC-001, SC-005).
- [ ] T014 [P] [US1] Add selection tests in `f-auditor/tests/unit/test_selection.py` for fixed-window endpoints, real activity versus mtime, whole prior context, canonical path containment, late changes and exclusion/uncertainty dispositions (FR-002, FR-003, FR-004, FR-019, SC-001).
- [ ] T015 [P] [US1] Add reviewed positive and negative transcript fixtures plus expected root-problem/evidence annotations in `f-auditor/tests/fixtures/analysis/` and replay tests in `f-auditor/tests/integration/test_analysis_quality.py`; require every annotated positive, reject unrelated/disproved cases and prove an empty analyzer fails. Include a separate actual-launcher acceptance against annotated fixtures with sanitized input/output provenance, not canned responses (FR-005, FR-020, SC-008).
- [ ] T016 [P] [US1] Add runtime, chunk and source-coverage tests in `f-auditor/tests/integration/test_analysis_runtime.py` for budget enforcement, all-message coverage, distant correction/resolution reconciliation, incomplete-context partial status, attempted tool execution denied before action, blocked external reads/network/writes, event rejection, refusal, timeout, one retry, invalid schema and partial/failed reporting (FR-012, FR-013, FR-019, FR-020, SC-005).

### Implementation

- [ ] T017 [US1] Before T017 implementation, perform a read-only feasibility probe for closure, current-owner evidence and complete history for both native hosts; record versioned results in `f-auditor/references/validation-record.md` without reading secrets. If an unavailable host would defeat the approved D-007 objective, surface the evidence for a user decision rather than relaxing it; otherwise mark unsupported versions partial. Then implement the read-only Hermes inventory and visible-history adapter in `f-auditor/src/f_auditor/sources.py`, using verified lifecycle/current-owner evidence and explicit unknown dispositions; never use migration-capable host constructors (FR-003, FR-019).
- [ ] T018 [US1] Implement read-only Codex inventory, legacy/modern traversal and pagination in `f-auditor/src/f_auditor/sources.py` after T017; do not treat archived status, completed turns, mtime or a private server's empty list as closure (FR-003, FR-019).
- [ ] T019 [US1] Implement canonical workspace, provable closure, completeness and visible-activity selection in `f-auditor/src/f_auditor/selection.py`, preserving whole-session context and distinguishing unknown from ineligible (FR-002, FR-003, FR-004, FR-019).
- [ ] T020 [US1] Add bounded contextual analysis instructions, relevance/exclusion rules, priority rubric and untrusted-session boundaries in `f-auditor/SKILL.md` and `f-auditor/references/audit-contract.md` (FR-005, FR-011, FR-013, FR-016).
- [ ] T021 [US1] Implement budgeted immutable chunks, provenance-preserving cross-chunk reconciliation and the Codex native launcher in `f-auditor/src/f_auditor/analysis.py`; require the pre-execution capability gate in `specs/006-f-auditor/contracts/audit-interface.md`, fail closed if unavailable, and report refusal, timeout, retry, unreconciled context and unprocessed chunks (FR-005, FR-012, FR-013, FR-016).
- [ ] T022 [US1] Implement the optional Hermes launcher capability gate in `f-auditor/src/f_auditor/analysis.py` after T021; reject the backend unless its tools, hooks and output framing are verified non-mutating (FR-013, FR-016).
- [ ] T023 [US1] Implement coverage-aware selection-to-analysis orchestration and validated evidence attribution in `f-auditor/src/f_auditor/cli.py`, without mutating the shared backlog in this isolated story test (FR-005, FR-006, FR-012, FR-019, SC-002).
- [ ] T024 [US1] Run the US1 fixture, safety, schema and annotated replay suites in `f-auditor/tests/`; verify positive/negative acceptance and that open, outside-root, uncertain and incomplete cases are correctly distinguished (SC-001, SC-005, SC-007, SC-008).
- [ ] T025 [US1] Run version-specific read-only native compatibility probes for both hosts and record closure, liveness, source completeness and unsupported-version evidence in `f-auditor/tests/integration/test_native_compatibility.py` and `f-auditor/references/validation-record.md`; no fixture or archived/idle state proves native closure (FR-003, FR-019).

## Phase 4: User Story 2 — Maintain the shared backlog (P1)

**Goal**: Merge evidence and support contributor completion without losing human content or asserting unproved regressions.

**Independent test**: Exercise backlog and contributor commands with prepared validated findings and a fixture file, including overlapping helper writers; no native history or model backend is needed for this isolated test.

### Tests first

- [ ] T026 [P] [US2] Add Markdown round-trip, priority index, human-note/status preservation and malformed-format tests in `f-auditor/tests/unit/test_backlog_format.py` (FR-007, FR-009, FR-011, FR-014, SC-009).
- [ ] T027 [P] [US2] Add grouping, exact-origin deduplication, ambiguous similarity, completed-fix chronology and linked regression tests in `f-auditor/tests/unit/test_regressions.py` (FR-008, FR-010, FR-015, SC-003, SC-004).
- [ ] T028 [P] [US2] Add multiprocess helper-coordination, lock timeout, drift, latest-read merge, atomic promotion and interruption/recovery tests in `f-auditor/tests/integration/test_backlog_concurrency.py` (FR-009, FR-014, FR-021, SC-004).
- [ ] T029 [P] [US2] Add completion-command validation and status-only legacy completion tests in `f-auditor/tests/contract/test_completion.py` for issue IDs, UTC fix time, evidence, owner and no mutation on error (FR-010, FR-018, FR-021).

### Implementation

- [ ] T030 [US2] Implement single-authority Markdown parsing, stable `FI-` IDs, human-preserving edits, actionable priority index and conflict detection in `f-auditor/src/f_auditor/backlog.py` (FR-006, FR-007, FR-009, FR-011, FR-014).
- [ ] T031 [US2] Implement same-root grouping, per-occurrence provenance, replay deduplication and post-fix linked regression/insufficient-evidence classification in `f-auditor/src/f_auditor/backlog.py` after T030 (FR-008, FR-010, FR-015).
- [ ] T032 [US2] Implement the shared sibling OS lock, latest-file merge, observed-drift rejection, fsync/atomic replacement, backup and recoverable commit handling in `f-auditor/src/f_auditor/backlog.py` after T031; do not claim safety for uncoordinated concurrent editors (FR-009, FR-014, FR-021).
- [ ] T033 [US2] Implement explicit contributor completion with issue ID, UTC time, fix evidence and owner in `f-auditor/src/f_auditor/cli.py`, using T032's lock and preserving all unrelated issues (FR-010, FR-018, FR-021).
- [ ] T034 [US2] Connect validated US1 findings to the backlog merge in `f-auditor/src/f_auditor/cli.py`, preserving statuses and classifying partial/failed outcomes without unsafe writes (FR-006, FR-007, FR-009, FR-010, FR-012, FR-014, FR-018).
- [ ] T035 [US2] Run US2 unit, contract and multiprocess suites in `f-auditor/tests/`; verify replay, status preservation, uncertainty, lock failures and both pre/post-promotion recovery (SC-003, SC-004, SC-009).

## Phase 5: User Story 3 — Repeatable manual invocation (P2)

**Goal**: Provide a documented, non-interactive manual command with consistent destination and explicit outcome semantics, without enabling a schedule.

**Independent test**: Invoke against an isolated environment with controlled source/runtime fixtures from two working directories; verify command output, destination, exit codes and absence of scheduling. Live runtime smoke remains a separate required gate.

### Tests first

- [ ] T036 [P] [US3] Add CLI contract tests in `f-auditor/tests/contract/test_cli.py` for `audit`, `complete`, root/backlog/config precedence, JSON/human output, exit 0/1/2 including full source coverage with unresolved classification returning 2, missing prerequisites and no automatic installation or schedule (FR-001, FR-007, FR-012, FR-017, FR-018).
- [ ] T037 [P] [US3] Add cross-working-directory integration tests in `f-auditor/tests/integration/test_invocation.py` for a single destination, full/partial/failed summaries, zero findings, no competing backlog and preserved existing content (FR-007, FR-012, FR-014, SC-006, SC-010).

### Implementation

- [ ] T038 [US3] Finish the `audit` and `complete` entry points and structured/human outcome reporting in `f-auditor/src/f_auditor/cli.py`, including computed source/session/chunk dispositions, unresolved classifications, destination and update state (FR-001, FR-012, FR-017, FR-018).
- [ ] T039 [US3] Document manual invocation, prerequisites, source limitations, safe evidence handling, completion coordination, rollback and separately authorized future scheduling in `f-auditor/SKILL.md` and `f-auditor/references/audit-contract.md` (FR-001, FR-013, FR-017, FR-021).
- [ ] T040 [US3] Run CLI contract and two-directory integration suites in `f-auditor/tests/contract/test_cli.py` and `f-auditor/tests/integration/test_invocation.py`; confirm correct outcomes and that no schedule was created (SC-006, SC-010).

## Phase 6: Distribution and cross-cutting validation

- [ ] T041 Add failing distribution tests for the canonical skill, packaged schema/runtime assets and targeted generation that preserves bytes and metadata of unrelated generated copies in `tests/unit/test_host_skill_distribution.py` (FR-001, FR-016).
- [ ] T042 Extend `tools/sync_host_skills.py` for `f-auditor/` and a targeted generation mode or equivalent scoped operation; regenerate only its intended host copies without rewriting unrelated generated copies. Preserve the existing full distribution check; keep packaging, lockfile and sync-script writes exclusive (FR-001, FR-016).
- [ ] T043 Run the complete `f-auditor/tests/` suite, existing `refine-idea/tests/`, distribution tests and `python3 tools/sync_host_skills.py --check`; retain real results in the implementation validation record (FR-001–FR-021, SC-001–SC-010).
- [ ] T044 Exercise `specs/006-f-auditor/quickstart.md` with the actual implemented command, supported native runtime and actual native history sources; also execute the real analyzer on approved annotated positive/negative fixtures with input/output provenance. Record redacted outcomes, source/closure gaps and before/after history hashes; unavailable live execution leaves acceptance unverified, never fabricated (FR-001, FR-003, FR-005, FR-012, FR-020, SC-006, SC-008).
- [ ] T045 Verify every FR/SC against passing tests and native evidence, document limitations and restore/rollback procedure, and explicitly block full acceptance if either required host lacks a verified usable closure path or native runtime safety boundary in `f-auditor/references/validation-record.md` (FR-003, FR-013, FR-019, SC-001, SC-005, SC-007).

## Dependencies and execution order

- T001–T002 precede T003–T011. Tests T003–T006 are disjoint and can run in parallel; T007–T010 are ordered by shared contracts and T011 verifies the foundation.
- US1 test/fixture tasks T012–T016 are disjoint and may run in parallel after the foundation. T017 and T018 must serialize because they both modify `sources.py`; T021 and T022 serialize on `analysis.py`. T023 depends on selection and analysis; T024 depends on implementation; T025 requires actual native compatibility evidence.
- US2 tests T026–T029 are disjoint and may run in parallel. T030–T032 serialize on `backlog.py`; T033 needs coordination, and T034 integrates US1 and US2 through `cli.py`. Independent US2 fixture testing does not require native histories.
- US3 tests T036–T037 may run in parallel. T038 follows T034 and serializes with other `cli.py` work; T039 serializes with T020 because both touch skill files. T040 follows T038–T039.
- T041–T045 follow integrated behavior; T042 owns sync edits exclusively. T043–T045 are final gates, not substitutes for red/green tests. No concurrent work may share a file or bypass dependency completion merely because a task is marked `[P]`.

## Traceability

| Requirement | Primary tasks |
| --- | --- |
| FR-001 | T001, T036, T038, T039, T042, T044 |
| FR-002 | T003, T007, T014, T019 |
| FR-003 | T012, T013, T017–T019, T025, T044–T045 |
| FR-004 | T003, T007, T014, T019 |
| FR-005 | T015, T020–T021, T023–T024 |
| FR-006 | T002, T006, T008, T010, T023, T030, T034 |
| FR-007 | T003, T007, T026, T030, T034, T036–T037 |
| FR-008 | T027, T031 |
| FR-009 | T026, T028, T030, T032, T034 |
| FR-010 | T027, T029, T031, T033–T034 |
| FR-011 | T020, T026, T030 |
| FR-012 | T005, T009, T016, T021, T023, T034, T036–T038 |
| FR-013 | T004, T006, T008, T010, T016, T020–T022, T039, T045 |
| FR-014 | T005, T009, T026, T028, T030, T032, T034, T037 |
| FR-015 | T005, T009, T027, T031 |
| FR-016 | T001, T020–T022, T041–T042 |
| FR-017 | T001, T003, T007, T036, T038–T039 |
| FR-018 | T029, T033–T034, T036, T038 |
| FR-019 | T008, T012–T014, T017–T019, T023, T025, T045 |
| FR-020 | T002, T006, T010, T015–T016, T024 |
| FR-021 | T028–T029, T032–T033, T039 |

Success criteria SC-001–SC-010 map to the explicitly tagged tests and final gates above. Setup, tooling, recovery and documentation tasks also trace to operational and safety needs in the plan.

## Implementation strategy

Build the foundation, then validate US1 using isolated fixture analysis as the first functional slice. Complete US2 before an end-to-end shared-backlog audit, then US3 and distribution. The full feature is not accepted solely on fixtures: both host closure capabilities, safe native runtime execution, manual invocation and explicit coverage limitations require real evidence. If a capability cannot be proved, report it as unsupported/partial and do not claim full host acceptance. Scheduling, Windows auditing, remote histories, automatic fixes and publication are deferred.
