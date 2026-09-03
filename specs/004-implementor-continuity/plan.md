# Implementation Plan: Implementor Continuity Controls

## Summary

Add an explicit terminal-verdict drive loop to the implementation workflow, backed by deterministic continuation-state validation and replay fixtures. The controller progresses through correction, promotion, convergence, and final evidence automatically; it stops only for missing authority, material decisions, or external-state failures.

## Design

1. Extend `idea-refinery-implement/SKILL.md` and its orchestration contract with a preflight, drive-loop, blocker taxonomy, and non-yielding progress-update rules.
2. Add deterministic completion-checklist and continuation-state models to the Python sidecar, including transitions for review correction, permissions, validator prerequisites, convergence, and terminal verdicts.
3. Add replay fixtures and tests for each reported pause cause; reject a run that ends with actionable internal work.
4. Update implementation-state template and documentation with the checklist and single scoped-approval policy.

## Verification

- Unit and contract tests for continuation transitions.
- Replay fixtures for review findings, pending task/state work, protected paths, missing PyYAML, and true blockers.
- Full deterministic suite and skill-structure validation.
