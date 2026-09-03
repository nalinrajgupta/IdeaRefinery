# Tasks: Parallel TDD Implementation Skill

**Input**: Design documents from `specs/002-parallel-tdd-implementation/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: Skill validation and behavioral forward evaluation are required. Application-code TDD is not applicable because this feature's deliverable is an instruction skill, but its runtime TDD contract is reviewed as a required behavior.

## Phase 1: Setup

- [x] T001 Create the sibling skill scaffold in `idea-refinery-implement/`
- [x] T002 Configure explicit-only UI metadata in `idea-refinery-implement/agents/openai.yaml`

## Phase 2: Foundational contracts

- [x] T003 [P] Define worker scheduling, ownership, TDD, review, and recovery rules in `idea-refinery-implement/references/orchestration-contract.md`
- [x] T004 [P] Define resumable controller state in `idea-refinery-implement/references/implementation-state-template.md`

## Phase 3: User Story 1 - Execute an approved handoff safely (Priority: P1)

**Independent Test**: Validate that the entrypoint requires a ready Spec Kit handoff, preserves hook/checklist semantics, and records baseline/red/green/refactor evidence before task promotion.

- [x] T005 [US1] Implement authorization, component routing, and entry gates for FR-001, FR-002, FR-003, FR-004, FR-005, FR-014, FR-015, FR-022, FR-023, and FR-028 in `idea-refinery-implement/SKILL.md`
- [x] T006 [US1] Implement controller-only task promotion and recorded TDD execution for FR-010, FR-011, FR-012, FR-013, FR-018, FR-021, FR-025, and FR-029 in `idea-refinery-implement/SKILL.md`

## Phase 4: User Story 2 - Run independent work concurrently (Priority: P2)

**Independent Test**: Confirm the contract permits tasks in disjoint subfolders to share a wave while serializing shared resources and dirty paths.

- [x] T007 [US2] Implement dependency and conservative write-set wave formation for FR-006, FR-007, FR-008, FR-009, FR-024, FR-026, and FR-030 in `idea-refinery-implement/SKILL.md`
- [x] T008 [US2] Specify immutable worker envelopes, enforceable isolation, and a maximum capacity of three for FR-007, FR-008, FR-009, and FR-026 in `idea-refinery-implement/references/orchestration-contract.md`

## Phase 5: User Story 3 - Review and converge before completion (Priority: P3)

**Independent Test**: Confirm missing review evidence blocks promotion and convergence is capped at two implementation cycles.

- [x] T009 [US3] Implement independent read-only wave review and finding disposition for FR-016, FR-017, and FR-018 in `idea-refinery-implement/SKILL.md`
- [x] T010 [US3] Implement bounded Spec Kit convergence, hook lifecycle, and fresh completion verification for FR-019, FR-020, FR-021, FR-023, and FR-027 in `idea-refinery-implement/SKILL.md`

## Phase 6: Integration and validation

- [x] T011 [P] Document the separate implementation handoff in `idea-refinery-full/SKILL.md`
- [x] T012 [P] Document both skill workflows in `README.md`
- [x] T013 Validate SC-008 with Skill Creator in `idea-refinery-implement/`
- [x] T014 Review SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, and SC-007 plus every FR against the delivered skill and references in `specs/002-parallel-tdd-implementation/`
- [x] T015 Run an isolated forward evaluation of SC-001, SC-002, SC-003, SC-004, SC-006, and SC-007 using `specs/002-parallel-tdd-implementation/quickstart.md`

## Dependencies & Execution Order

- T001-T002 precede all skill content.
- T003-T004 may proceed in parallel, then T005-T010 consume those contracts.
- T005-T006 establish the safe execution path before T007-T010 add concurrency and completion.
- T011-T012 are independent documentation integrations.
- T013-T015 run after all content changes.

## Parallel Opportunities

- T003 and T004 modify different reference files.
- T011 and T012 modify different integration documents.
- Runtime implementations may parallelize only after applying the stronger write-set contract defined by this feature.
