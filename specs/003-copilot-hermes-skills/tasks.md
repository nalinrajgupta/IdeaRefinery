# Tasks: Cross-Host Idea Refinery Skills

**Input**: [plan.md](plan.md), [spec.md](spec.md)

## Phase 1: Setup

- [x] T001 Create `tools/sync_host_skills.py` with canonical skill source and shared distribution path constants.
- [x] T002 Create `tests/unit/test_host_skill_distribution.py` fixtures for temporary canonical and generated skill trees.

## Phase 2: Foundational distribution and contract

- [x] T003 Implement deterministic synchronization of skill bodies and required relative support references, plus `--check` mode, in `tools/sync_host_skills.py`.
- [x] T004 [P] Add host-neutral capability discovery, fallback recording, and safe sequential-execution language to `idea-refinery-full/SKILL.md`.
- [x] T005 [P] Add host-neutral capability discovery, fallback recording, and safe sequential-execution language to `idea-refinery-implement/SKILL.md`.
- [x] T006 Add parity, frontmatter, generated-marker, support-reference existence, and required-reference validation in `tests/unit/test_host_skill_distribution.py`.

## Phase 3: User Story 1 - Run full refinement in any supported host (Priority: P1)

**Goal**: Make the complete refinement workflow discoverable and safe in Copilot and Hermes.

**Independent Test**: Generated full skill exactly matches the canonical body plus its permitted host preamble; its capability contract and reference paths validate.

- [x] T007 [US1] Generate `.agents/skills/idea-refinery-full/SKILL.md` and its required `references/` tree from the canonical full skill using `tools/sync_host_skills.py`.
- [x] T008 [US1] Add generated full-skill source, explicit-only, artifact, review, and readiness assertions to `tests/unit/test_host_skill_distribution.py`.
- [x] T009 [US1] Document GitHub Copilot and Hermes full-skill discovery, invocation, and fallback behavior in `docs/host-compatibility.md`.

## Phase 4: User Story 2 - Implement a ready handoff in any supported host (Priority: P1)

**Goal**: Make the separate implementation workflow discoverable and safe in Copilot and Hermes.

**Independent Test**: Generated implementation skill preserves entry gates, controller-owned artifacts, isolation rules, TDD/review evidence, convergence, and final verdict.

- [x] T010 [US2] Generate `.agents/skills/idea-refinery-implement/SKILL.md` and its required `references/` tree from the canonical implementation skill using `tools/sync_host_skills.py`.
- [x] T011 [US2] Add generated implementation-skill authority, isolation, review, convergence, and terminal-verdict assertions to `tests/unit/test_host_skill_distribution.py`.
- [x] T012 [US2] Document Copilot and Hermes implementation invocation and sequential fallback behavior in `docs/host-compatibility.md`.

## Phase 5: User Story 3 - Install and validate the correct host distribution (Priority: P2)

**Goal**: Give maintainers accurate, host-specific setup and maintenance guidance.

**Independent Test**: Each host row supplies discovery, install, invocation, Spec Kit setup/preservation, update, removal, and validation guidance.

- [x] T013 [US3] Create the host capability and setup matrix in `docs/host-compatibility.md`.
- [x] T014 [P] [US3] Update host overview, authority boundary, and documentation links in `README.md`.
- [x] T015 [P] [US3] Update host-specific install, update, removal, troubleshooting, and validation instructions in `setup.md`.
- [x] T016 [P] [US3] Update distribution ownership and discovery paths in `RepoStructure.md`.
- [x] T017 [US3] Add documentation coverage assertions to `tests/unit/test_host_skill_distribution.py`.

## Phase 6: Polish and verification

- [x] T018 Run `python3 tools/sync_host_skills.py --check` and repair any generated-distribution drift.
- [x] T019 Run `uv run --project idea-refinery-full --extra dev pytest -q`.
- [x] T020 Run applicable structural skill validation against both canonical and generated skill folders.
- [x] T021 Run `git diff --check` and record compatibility validation evidence in `specs/003-copilot-hermes-skills/refinery-state.md`.

## Dependencies

`T001–T006` block all story work. `T007–T009` and `T010–T012` can proceed independently after Phase 2. Documentation tasks `T013–T017` can proceed after the distribution format is defined. Final verification follows all prior tasks.

## Requirement traceability

| Requirement | Task IDs | Acceptance target |
| --- | --- | --- |
| FR-001 | T003, T007, T010, T013 | Both workflows are discoverable through the shared project-skill distribution and documented host installs. |
| FR-002 | T004, T005, T006, T008, T011 | Generated skills retain required workflow gates and parity validation passes. |
| FR-003 | T004, T005, T009, T012, T013 | Capability matrix and both workflow bodies define native, local, sequential, and blocked paths. |
| FR-004 | T004, T008 | Full workflow keeps the separate implementation invocation boundary. |
| FR-005 | T005, T011 | Implementation workflow retains controller ownership and isolation/sequential rules. |
| FR-006 | T009, T012, T013, T014, T015, T016 | Documentation covers all supported hosts and maintenance actions. |
| FR-007 | T001, T003, T006, T013, T016 | Canonical-source and synchronization ownership are documented and tested. |
| FR-008 | T003, T006, T018, T020 | Drift and missing-reference checks fail before release. |
| FR-009 | T004, T005, T014, T015, T019 | Existing Codex behavior and regression validation remain intact. |
| FR-010 | T004, T005, T009, T012, T013 | Capability and fallback distinctions are visible in skill bodies and documentation. |
| FR-011 | T001, T003, T006, T007, T010, T018 | Generated skill bodies and support trees are deterministically synchronized and checked. |
| FR-012 | T004, T009, T013, T015 | Host initialization and existing-integration preservation are specified and documented. |
| SC-001–SC-005 | T006, T008, T011, T013, T017–T021 | Automated validation and host documentation prove the specified outcomes. |

## Parallel opportunities

- T004 and T005 edit separate canonical skills.
- T014, T015, and T016 edit separate top-level documentation files.
- T007–T009 and T010–T012 can be parallelized after foundational work when their write sets are isolated.

## Implementation strategy

Deliver the distribution generator and parity checks first. Then deliver the full workflow distribution, followed by the implementation distribution, then documentation. Do not claim host support until generated artifacts and all validation checks pass.
