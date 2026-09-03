# Feature Specification: Parallel TDD Implementation Skill

**Feature Branch**: `feature/v3`

**Created**: 2026-09-02

**Status**: Approved

**Input**: User description: "Extend Idea Refinery with a separate implementation skill that executes generated spec, plan, and tasks using parallel subagents, test-driven development, and independent review. Prefer a Superpowers-first hybrid with Spec Kit traceability and gstack final review."

## User Scenarios & Testing

### User Story 1 - Execute an approved handoff safely (Priority: P1)

An engineer invokes the implementation skill from a Spec Kit repository and receives an implementation that follows the active feature's approved specification, plan, and tasks without requiring new material product or architecture decisions.

**Why this priority**: Executing the refined handoff is the skill's primary value.

**Independent Test**: Invoke the skill against a fixture feature with one buildable task and confirm that it validates prerequisites, records a failing test, makes the smallest implementation change, passes the test, and marks the task complete.

**Acceptance Scenarios**:

1. **Given** an active feature whose refinery verdict is ready, **When** the engineer invokes the skill, **Then** it loads the complete artifact set and executes only traceable tasks.
2. **Given** a task that changes behavior, **When** implementation begins, **Then** failing test evidence is captured before production code changes and passing evidence is captured afterward.
3. **Given** an unresolved material decision, **When** the skill prepares execution, **Then** it stops and identifies the decision rather than allowing a worker to decide it.

---

### User Story 2 - Run independent work concurrently (Priority: P2)

An engineer can accelerate a feature by assigning independent task slices to parallel subagents while preventing overlapping writes and dependency violations.

**Why this priority**: Parallel execution is valuable only after correctness and intent are protected.

**Independent Test**: Provide a fixture with independent tasks in two subfolders and one shared-file task; confirm the independent tasks share a wave while the shared-file task is serialized.

**Acceptance Scenarios**:

1. **Given** tasks with disjoint dependencies and owned paths, **When** a wave is formed, **Then** up to three workers may run concurrently.
2. **Given** tasks that may touch the same file, directory ownership boundary, generated artifact, dependency declaration, migration sequence, or shared configuration, **When** scheduling occurs, **Then** those tasks are serialized.
3. **Given** a worker assignment, **When** the worker executes it, **Then** it may edit only its declared write set and must report unexpected required paths to the controller.

---

### User Story 3 - Review and converge before completion (Priority: P3)

An engineer receives independent review and fresh verification evidence, including detection of work omitted from the original execution pass.

**Why this priority**: Passing local task tests is insufficient proof that the complete specification was implemented.

**Independent Test**: Seed an implementation with a passing unit test but a missing acceptance requirement; confirm review or convergence prevents a successful verdict and produces traceable remediation.

**Acceptance Scenarios**:

1. **Given** a completed implementation wave, **When** review starts, **Then** a read-only reviewer receives the immutable requirements, task IDs, changed paths, diff, and test evidence.
2. **Given** a supported reviewer finding, **When** the controller triages it, **Then** the finding is resolved, explicitly rejected with evidence, or blocks completion.
3. **Given** all planned tasks are complete, **When** convergence runs, **Then** remaining spec-to-code gaps are appended as tasks and executed within a bounded cycle budget.
4. **Given** the implementation is ready to close, **When** completion is reported, **Then** fresh verification output supports every passing claim and final gstack review is offered only for pre-landing scope.

### Edge Cases

- A task marked parallel has an implicit dependency or overlapping generated output not represented by its file path.
- A worker discovers that its task requires editing outside its assigned subfolder.
- A test already passes before implementation, so it does not demonstrate the intended missing behavior.
- A failing test is caused by the environment or an unrelated baseline failure.
- A worker fails, times out, or returns without the required evidence envelope.
- A reviewer recommends a scope or architecture change that is not authorized by the existing artifacts.
- Superpowers component skills are unavailable in the active session.
- Convergence repeatedly reports the same root gap.
- The working tree contains user changes unrelated to the active feature.

## Requirements

### Functional Requirements

- **FR-001**: The repository MUST provide a separate `idea-refinery-implement` skill rather than extending the refinement skill past its handoff boundary.
- **FR-002**: The skill MUST accept only an active Idea Refinery handoff containing `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md` with a recognized ready verdict.
- **FR-003**: The skill MUST reject implementation when the handoff is blocked on a material decision.
- **FR-004**: The skill MUST treat the approved spec and plan as intent authority and the task list as execution state.
- **FR-005**: The skill MUST preserve pre- and post-implementation extension hook behavior defined by Spec Kit.
- **FR-006**: The controller MUST derive task dependencies and conservative write sets before dispatch.
- **FR-028**: Before dispatch, the controller MUST map every buildable requirement to task IDs and acceptance targets and MUST block on unmapped requirements.
- **FR-007**: A task MUST be parallelized only when its dependencies are satisfied and its write set is disjoint from every other task in the wave.
- **FR-008**: The default worker capacity MUST be no more than three concurrent implementation workers.
- **FR-009**: Only the controller identity MAY update shared coordination artifacts, including `tasks.md`, `refinery-state.md`, and implementation run state; controller-invoked convergence operates under that identity and its exact patch MUST be validated and recorded.
- **FR-010**: Every behavior-changing task MUST follow a recorded red-green-refactor cycle unless the controller records why a test-first cycle is inapplicable.
- **FR-011**: Red evidence MUST show the intended assertion failing for the intended reason before implementation code changes.
- **FR-029**: TDD evidence MUST bind ordered baseline, test-diff, red, implementation-diff, green, and refactor events using timestamps and content hashes.
- **FR-012**: Green evidence MUST come from the narrow test and the relevant broader verification command after implementation.
- **FR-013**: Workers MUST stop and report rather than edit outside their assignment or make a material product or architecture decision.
- **FR-030**: Parallel workers MUST run behind an enforceable path boundary such as a scoped sandbox/freeze or isolated worktree; when unavailable, workers MUST return changes for controller application or execution MUST be sequential.
- **FR-014**: The workflow MUST prefer the Superpowers `subagent-driven-development`, `test-driven-development`, `requesting-code-review`, `systematic-debugging`, and `verification-before-completion` skills when available.
- **FR-015**: When those Superpowers skills are unavailable, the workflow MUST apply equivalent local contracts and disclose degraded composition without weakening TDD, review, or verification gates.
- **FR-016**: Each completed wave MUST receive an independent, read-only review before its tasks are promoted to complete.
- **FR-017**: Review findings MUST include severity, evidence, affected requirement or task, proposed correction, and disposition.
- **FR-018**: The controller MUST verify worker changes and evidence before marking task checkboxes complete.
- **FR-019**: The workflow MUST run Spec Kit convergence after the initial implementation pass and MAY run at most two convergence implementation cycles.
- **FR-020**: Repeated root gaps, new material contradictions, or new product/architecture decisions MUST stop convergence.
- **FR-021**: Completion MUST require fresh project-level tests and requirement-to-implementation traceability.
- **FR-022**: The skill MUST keep commit, push, pull-request, merge, deployment, and destructive cleanup operations outside its authority unless separately requested.
- **FR-023**: gstack `review` MUST be treated as an optional final pre-landing review, not as the task implementation engine or per-wave reviewer.
- **FR-024**: The skill MUST preserve unrelated user changes and MUST not assign workers overlapping uncommitted paths.
- **FR-025**: The skill MUST maintain resumable implementation state containing waves, assignments, evidence, findings, and convergence-cycle status.
- **FR-026**: Each wave MUST use versioned canonical repository-relative path claims, ancestor-overlap detection, protected-path hashes, an exclusive lease, and post-return drift verification.
- **FR-027**: Unconditional pre-implementation hooks MUST run once before baseline/snapshot capture, and unconditional post-implementation hooks MUST run once after convergence and before final verification; hook mutations MUST invalidate affected evidence.

### Key Entities

- **Implementation Run**: The active feature, artifact hashes, status, wave history, verification results, review findings, and convergence count.
- **Task Slice**: One or more traceable task IDs, dependencies, acceptance targets, declared read set, declared write set, and verification command.
- **Execution Wave**: A deterministic group of mutually independent task slices eligible for concurrent execution.
- **Worker Evidence**: Red, green, refactor, changed-path, and verification evidence returned by a worker.
- **Review Finding**: An independently produced defect or coverage finding and its controller-owned disposition.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In scheduling fixtures, 100% of overlapping write sets and unsatisfied dependencies are serialized.
- **SC-002**: In TDD fixtures, 100% of behavior-changing completed tasks contain valid red and green evidence or an explicit test-inapplicable rationale approved by the controller.
- **SC-003**: Every unauthorized worker mutation of coordination state or an undeclared path is detected before promotion, invalidates the result, and leaves shared task state controller-owned.
- **SC-004**: Every completed wave has one independent review envelope and a disposition for every high-severity finding.
- **SC-005**: Every buildable functional requirement maps to at least one completed task and verification result before completion.
- **SC-006**: Interrupted runs can resume without repeating already verified waves whose artifact and change hashes still match.
- **SC-007**: The workflow stops after at most two convergence implementation cycles and identifies any unresolved root gap.
- **SC-008**: The new skill passes structural validation with no scaffold placeholders and can be discovered independently from `idea-refinery-full`.

## Assumptions

- The active coding host supports bounded subagents, but safe sequential execution remains available when capacity is lower.
- Superpowers may be installed after the new skill is authored; availability is rechecked at invocation time.
- Parallel execution uses a shared workspace only for disjoint write sets; broader isolation may use user-approved worktrees.
- Spec Kit remains the source of artifact formats and extension-hook semantics.
- The new skill orchestrates implementation but does not itself land or deploy changes.

## Out of Scope

- Replacing Spec Kit artifact generation.
- Installing or upgrading Superpowers automatically.
- Automatically committing, pushing, opening pull requests, merging, or deploying.
- Allowing reviewers or workers to rewrite approved product scope.
- Optimizing model selection beyond using available bounded implementation and review agents.
