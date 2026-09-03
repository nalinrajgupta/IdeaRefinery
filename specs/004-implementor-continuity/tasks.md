# Tasks: Implementor Continuity Controls

- [ ] T001 Add continuation-state and completion-checklist contracts in `idea-refinery-full/src/idea_refinery/`.
- [ ] T002 Add unit and contract tests for terminal-drive and blocker classification in `idea-refinery-full/tests/`.
- [ ] T003 Add replay fixtures for each pause cause in `idea-refinery-full/tests/fixtures/replay/`.
- [ ] T004 Update `idea-refinery-implement/SKILL.md` and `references/orchestration-contract.md` with preflight, automatic correction, and terminal-drive rules.
- [ ] T005 Update `references/implementation-state-template.md` with completion-checklist and progress fields.
- [ ] T006 Update README, setup, and architecture documentation for continuity semantics.
- [ ] T007 Run the deterministic suite, replay tests, skill validation, and `git diff --check`.

## Requirement traceability

| Requirement | Tasks |
| --- | --- |
| FR-001–FR-003, FR-006–FR-007, FR-009 | T004, T005, T006 |
| FR-004–FR-005, FR-008, FR-010 | T001, T002, T003, T007 |
