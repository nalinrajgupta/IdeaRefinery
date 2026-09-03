# Feature Specification: Implementor Continuity Controls

**Feature Branch**: `004-implementor-continuity`
**Created**: 2026-09-03
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - Finish an authorized implementation (Priority: P1)

When a user invokes Idea Refinery Implement for a ready feature, the controller completes all normal workflow gates without waiting for additional user prompts.

**Independent Test**: A recorded implementation run with review findings, task promotion, convergence, and final evidence proceeds to a terminal verdict without a user message between routine gates.

**Acceptance Scenarios**:

1. **Given** an authorized active feature, **When** a review returns an objective in-scope finding, **Then** the controller corrects and revalidates it before resuming promotion.
2. **Given** verified tasks, **When** task promotion, convergence, or state recording remains, **Then** the controller completes those routine steps before ending its turn.

### User Story 2 - Resolve environment prerequisites early (Priority: P1)

A user receives one early, precise approval request for protected output paths or an unavailable validator prerequisite, rather than an avoidable mid-run pause.

**Independent Test**: Fixture runs identify protected write paths and missing validation dependencies during preflight and record the chosen remediation.

### User Story 3 - Understand true blockers (Priority: P2)

A user sees a blocked verdict only when missing authority, a material decision, or an external-state failure prevents safe progress.

**Independent Test**: Fixture runs distinguish actionable internal gates from genuine blockers and emit a terminal verdict only for the latter.

### Edge Cases

- A review finding requires a material product decision: stop and request that decision.
- A protected path cannot be approved: block with the exact path and required authority.
- A validator dependency cannot be provisioned: record degraded validation and block only if equivalent evidence is unavailable.

## Requirements

- **FR-001**: The implementation workflow MUST treat invocation as authority to finish all approved routine workflow steps.
- **FR-002**: The controller MUST maintain one explicit completion checklist covering tasks, reviews, corrections, convergence, state, and final evidence.
- **FR-003**: The controller MUST correct objective in-scope review findings without waiting for another user prompt.
- **FR-004**: Preflight MUST identify protected output paths and validator prerequisites before mutable work begins.
- **FR-005**: The workflow MUST issue at most one scoped authorization request per protected path or prerequisite category when such authority is required.
- **FR-006**: Status updates MUST report progress without yielding the workflow while actionable work remains.
- **FR-007**: The workflow MUST reserve blocked outcomes for missing authority, material decisions, or external-state failures.
- **FR-008**: Deterministic validation MUST cover continuity transitions and the listed pause-causing fixture scenarios.
- **FR-009**: The controller MUST run a terminal-verdict drive loop that advances or explicitly blocks every completion-checklist item.
- **FR-010**: The deterministic sidecar MUST validate the completion checklist and reject a non-terminal run with actionable internal work.

## Success Criteria

- **SC-001**: All routine completion gates advance to a terminal verdict without an additional user message in continuity fixtures.
- **SC-002**: Every protected-path and validator prerequisite fixture identifies its remediation before any task mutation.
- **SC-003**: Automated tests reject a run that ends with actionable checklist items.

## Assumptions

- The existing deterministic sidecar remains provider- and credential-independent.
- External permissions and user-owned material decisions remain legitimate stop conditions.
- The feature does not add a persistent background monitor or scheduler.
