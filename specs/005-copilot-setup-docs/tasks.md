# Tasks: First-Class GitHub Copilot Setup Documentation

**Input**: Design documents from `specs/005-copilot-setup-docs/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Contract tests are required because FR-014, FR-021, and FR-022 require regression detection for documentation, generated skills, platform preflight, and workflow path filters.

**Organization**: Tasks are grouped by user story so each documentation or preflight journey can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the validation map and baseline before changing product documentation or skill contracts.

- [x] T001 Record the FR-001 through FR-022 automated/manual validation mapping in `specs/005-copilot-setup-docs/quickstart.md`
- [x] T002 Capture the current focused-test, distribution-sync, and Markdown whitespace baselines in `specs/005-copilot-setup-docs/refinery-state.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare common test helpers and CI triggers used by every story.

- [x] T003 Add shared repository-document readers and assertion helpers in `tests/unit/test_host_skill_distribution.py`
- [x] T004 Add failing workflow-filter and cross-document link assertions in `tests/unit/test_host_skill_distribution.py`
- [x] T005 [P] Add `README.md` and `setup.md` to push and pull-request path filters in `.github/workflows/refinery-evals.yml`

**Checkpoint**: Common content validation and CI triggering are ready for story-specific red-green cycles.

---

## Phase 3: User Story 1 - Start Idea Refinery with GitHub Copilot (Priority: P1) MVP

**Goal**: Make the README a complete, concise Copilot entry point with correct invocation, expected outcomes, refresh behavior, and authority boundaries.

**Independent Test**: A new reader can identify the Copilot install choices and first invocation in under three minutes, and automated assertions confirm every required quick-start fact.

### Tests for User Story 1

- [x] T006 [US1] Add failing README assertions for Copilot first-class prerequisites, `.agents/skills`, `/idea-refinery-full`, `/skills reload`, the four refinement artifacts, readiness verdict, and separate `/idea-refinery-implement` authorization in `tests/unit/test_host_skill_distribution.py`

### Implementation for User Story 1

- [x] T007 [US1] Add the concise GitHub Copilot quick start, expected outputs, invocation sequence, and setup links in `README.md`
- [x] T008 [US1] Update README troubleshooting to distinguish Copilot slash invocation from the current dollar-prefixed skill-description wording in `README.md`
- [x] T009 [US1] Run the focused README contract test and record the manual three-minute discovery result in `specs/005-copilot-setup-docs/refinery-state.md`

**Checkpoint**: The README independently provides a usable Copilot MVP while preserving the separate implementation boundary.

---

## Phase 4: User Story 2 - Manage a Personal Copilot Installation (Priority: P1)

**Goal**: Provide safe, repeatable project-local and personal install, verify, update, removal, refresh, and precedence guidance.

**Independent Test**: Temporary-target walkthroughs prove PowerShell and portable-shell procedures are exact, idempotent, failure-safe, missing-safe, and limited to the two Idea Refinery skills.

### Tests for User Story 2

- [x] T010 [US2] Add failing setup-guide assertions for repository-local and `~/.copilot/skills` paths, both skill names, PowerShell and POSIX labels, preflight, staging, exact replacement, missing-safe removal, refresh, and active-copy inspection in `tests/unit/test_host_skill_distribution.py`

### Implementation for User Story 2

- [x] T011 [US2] Add the contiguous GitHub Copilot setup modes, prerequisites, project-local discovery, and invocation sections in `setup.md`
- [x] T012 [US2] Add failure-safe Windows PowerShell personal install, verify, update, and missing-safe removal procedures in `setup.md`
- [x] T013 [US2] Add equivalent POSIX-shell lifecycle procedures plus repository-versus-personal precedence and refresh troubleshooting in `setup.md`
- [x] T014 [US2] Execute the temporary-target lifecycle walkthrough for both shells and record parity, idempotence, failed-preflight, stale-file, and missing-safe-removal evidence in `specs/005-copilot-setup-docs/refinery-state.md`

**Checkpoint**: Personal and repository-local Copilot installations are independently manageable without undocumented commands or destructive scope.

---

## Phase 5: User Story 3 - Preserve Project and Spec Kit Configuration (Priority: P2)

**Goal**: Ensure Copilot setup preserves existing integrations and directs readers to one authoritative compatibility contract.

**Independent Test**: Documentation review and automated assertions confirm existing `.specify` integrations are preserved, uninitialized projects use the Copilot route only after approval, and shell-specific commands are labeled.

### Tests for User Story 3

- [x] T015 [US3] Add failing assertions for Spec Kit preservation, Copilot initialization, no-force guidance, canonical compatibility links, and shell labels across all three setup documents in `tests/unit/test_host_skill_distribution.py`

### Implementation for User Story 3

- [x] T016 [US3] Add Copilot host summary, initialization preservation, capability fallback, synchronization guidance, and a link to the setup lifecycle in `docs/host-compatibility.md`
- [x] T017 [US3] Align README and setup cross-links and remove remaining Codex-only framing that contradicts first-class Copilot support in `README.md` and `setup.md`

**Checkpoint**: Existing project configuration is preserved and cross-host guidance has one non-contradictory source of truth.

---

## Phase 6: User Story 4 - Complete Implementation Preflight on the Active Platform (Priority: P2)

**Goal**: Let the implementation workflow resolve Bash or PowerShell Spec Kit prerequisites with equivalent semantics and actionable failure.

**Independent Test**: Canonical and generated skill contract tests cover Bash-only, PowerShell-only, both-present, and neither-present instructions without weakening any existing entry gate.

### Tests for User Story 4

- [x] T018 [US4] Add failing canonical-skill assertions for Bash and PowerShell prerequisite paths, equivalent JSON/task semantics, native preference, and explicit unsupported-layout failure in `tests/unit/test_host_skill_distribution.py`

### Implementation for User Story 4

- [x] T019 [US4] Replace the unconditional Bash prerequisite instruction with deterministic Bash-or-PowerShell selection and actionable failure in `idea-refinery-implement/SKILL.md`
- [x] T020 [US4] Regenerate `.agents/skills/idea-refinery-implement` with `tools/sync_host_skills.py`
- [x] T021 [US4] Run generated-parity and platform-preflight contract tests and record results in `specs/005-copilot-setup-docs/refinery-state.md`
- [x] T022 [US4] Execute the Bash-only, PowerShell-only, both-present, and neither-present temporary preflight walkthroughs from `specs/005-copilot-setup-docs/quickstart.md` and record selected commands or failure evidence in `specs/005-copilot-setup-docs/refinery-state.md`

**Checkpoint**: Both supported script families can enter the unchanged implementation readiness gates.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Prove traceability, consistency, and complete feature readiness.

- [x] T023 Verify and update FR-001 through FR-022 and SC-001 through SC-008 task traceability after all repairs in `specs/005-copilot-setup-docs/tasks.md`
- [x] T024 Run `python tools/sync_host_skills.py --check` and the focused host-distribution suite from `specs/005-copilot-setup-docs/quickstart.md`
- [x] T025 Run the full existing Idea Refinery test suite and record any environment-limited verification in `specs/005-copilot-setup-docs/refinery-state.md`
- [x] T026 Run `git diff --check`, review all documentation links and shell labels, and record final validation in `specs/005-copilot-setup-docs/refinery-state.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 establishes the requirement-to-validation baseline.
- Phase 2 depends on Phase 1 and blocks all user-story test work.
- User Stories 1, 2, and 3 can proceed after Phase 2, but their tests serialize because they modify `tests/unit/test_host_skill_distribution.py`.
- User Story 4 can proceed after Phase 2 independently of documentation edits, except its test-file task must serialize with other test-file edits.
- Phase 7 depends on all selected stories.

### User Story Dependencies

- **US1**: No dependency on another story after Phase 2; delivers the Copilot README MVP.
- **US2**: No dependency on US1 for implementation, but final links must agree with US1.
- **US3**: Can begin after Phase 2; final alignment depends on US1 and US2 wording.
- **US4**: Independent of documentation stories after Phase 2; generated synchronization follows the canonical skill change.

### Parallel Opportunities

- T004 can run in parallel with T003.
- T007 and T008 are sequential because both edit `README.md`.
- T011 through T013 are sequential because all edit `setup.md`.
- T016 can run in parallel with T011 through T013 because it edits a different document.
- T019 can run in parallel with documentation implementation tasks; T020 must follow T019.
- Review and validation tasks run only after their corresponding edits.

## Parallel Example: Documentation and Preflight

```text
Worker A: T011-T013 in setup.md
Worker B: T016 in docs/host-compatibility.md
Worker C: T019 in idea-refinery-implement/SKILL.md
```

Do not parallelize tasks that edit `tests/unit/test_host_skill_distribution.py`, `README.md`, `setup.md`, or `refinery-state.md` with another task touching the same file.

## Requirement Traceability

| Requirement | Task IDs | Acceptance target |
| --- | --- | --- |
| FR-001, FR-002, FR-008 | T006-T009 | README provides first-class Copilot discovery, slash invocation, outputs, refresh, and authority boundary. |
| FR-003-FR-007 | T010-T014 | Setup provides complete and safe repository-local and personal lifecycle guidance. |
| FR-009-FR-013 | T015-T017 | Existing integration is preserved and cross-host/shell guidance is consistent. |
| FR-014 | T003, T005, T006, T010, T015, T018 | Automated tests detect missing required guidance and skill contracts. |
| FR-015-FR-017 | T010, T012-T014 | Personal operations are preflighted, exact, repeatable, failure-safe, missing-safe, and diagnosable. |
| FR-018 | T006, T008, T010 | Copilot slash invocation and description limitation are explicit. |
| FR-019, FR-020 | T018-T022 | Implementation preflight supports Bash and PowerShell or fails actionably in contract and controlled walkthrough evidence. |
| FR-021 | T004, T005 | README/setup changes trigger validation on push and pull requests. |
| FR-022 | T001, T023-T026 | Automated and manual evidence covers every verifiable requirement and outcome. |
| SC-001, SC-003, SC-006 | T006-T009 | Copilot onboarding is fast, complete, and outcome-aware. |
| SC-002, SC-007 | T010-T014 | Lifecycle walkthrough is complete, exact, and idempotent. |
| SC-004 | T015-T017, T026 | All three documents use non-contradictory paths, invocations, and shell labels. |
| SC-005 | T001, T023-T026 | Validation coverage is explicit and complete. |
| SC-008 | T018-T022 | Bash, PowerShell, both-present, and unsupported-layout preflight cases are covered by assertions and controlled execution evidence. |

## Implementation Strategy

### MVP First

1. Complete Phases 1 and 2.
2. Complete User Story 1.
3. Validate the README quick start independently.
4. Stop if only a discoverable Copilot entry point is required.

### Incremental Delivery

1. Add README onboarding.
2. Add safe personal and project-local lifecycle guidance.
3. Align Spec Kit preservation and compatibility documentation.
4. Add platform-aware implementation preflight.
5. Run complete cross-document and generated-distribution validation.

## Notes

- All tasks use the required checkbox, sequential ID, story label, and explicit path format.
- Test tasks precede implementation within each story.
- Canonical skill edits must be regenerated; never edit the generated copy directly.
- No task authorizes commits, pushes, issues, deployment, or application-code changes.
