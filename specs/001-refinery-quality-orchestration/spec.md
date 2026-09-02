# Feature Specification: Refinery Quality Orchestration

**Feature Branch**: `v2`

**Created**: 2026-08-31

**Status**: Draft (Spec v2, post-review synthesis)

**Input**: Improve the current Idea Refinery workflow with session-native multi-model reviews, model overrides, safe parallelism, coverage-driven synthesis, bounded repair loops, and regression evals.

## Clarifications

### Session 2026-09-01

- Q: Can a run reach `READY FOR IMPLEMENTATION` when a required review role and all its fallback models failed? → A: Yes, after an explicit user waiver; label the handoff ready-but-degraded and preserve the missing perspective, affected coverage, and waiver rationale.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Independent Multi-Model Reviews (Priority: P1)

As a user invoking the full refinement workflow, I receive independent CEO, product, and architecture reviews performed with role-appropriate models available in the current session, so the resulting specification reflects genuinely different perspectives rather than one repeated critique.

**Why this priority**: Independent review is the central quality improvement and the basis for coverage-driven synthesis.

**Independent Test**: Run the workflow against a frozen Spec v1 and verify that all three required review roles return isolated, attributable findings using the resolved default or overridden model configuration.

**Acceptance Scenarios**:

1. **Given** all default role models are available, **When** full review begins, **Then** the CEO, product, and architect reviews use their configured models and reasoning efforts.
2. **Given** a user supplies valid per-role overrides, **When** full review begins, **Then** those overrides take precedence and the resolved configuration is recorded.
3. **Given** an explicit override names an unavailable model, **When** configuration is validated, **Then** review does not begin and the user receives the available choices.
4. **Given** a bundled default model is unavailable, **When** configuration is resolved, **Then** a documented fallback is used and the degraded assignment is visibly recorded.
5. **Given** no configuration is supplied, **When** the existing `$idea-refinery-full <idea>` invocation is used, **Then** the bundled defaults apply without changing the existing interaction.
6. **Given** invocation and repository settings both configure the same role, **When** configuration resolves, **Then** the invocation value wins and the complete resolved configuration is shown before dispatch.

---

### User Story 2 - Synthesize by Coverage, Not Volume (Priority: P1)

As a user reviewing Spec v2, I can see that every material product and engineering risk area was reviewed, resolved, or explicitly identified as a blind spot, so a quiet reviewer response is not mistaken for complete coverage.

**Why this priority**: Multiple reviewers add value only when their combined work covers the specification systematically.

**Independent Test**: Seed known omissions across the coverage taxonomy and verify that synthesis maps findings to requirements, exposes unreviewed high-risk areas, deduplicates overlaps without losing attribution, and issues at most one targeted follow-up.

**Acceptance Scenarios**:

1. **Given** three completed review result sets, **When** synthesis starts, **Then** every applicable coverage item is marked reviewed, unresolved, resolved, or blind spot with supporting evidence.
2. **Given** two reviewers raise the same underlying issue, **When** findings are normalized, **Then** one canonical finding retains both reviewers' attribution and evidence.
3. **Given** a high-risk coverage item has no evidence of review, **When** the matrix is evaluated, **Then** the best-suited role receives one narrowly scoped follow-up request.
4. **Given** a remaining blind spot after the follow-up, **When** synthesis completes, **Then** the blind spot is explicitly dispositioned rather than silently omitted.
5. **Given** a reviewer returns no finding for an assigned item, **When** its result is validated, **Then** an evidence-backed coverage attestation is still required before the item can be marked reviewed.

---

### User Story 3 - Repair Material Gaps Without Looping (Priority: P1)

As a user, I receive focused corrections for material consistency failures without unbounded rewriting, repeated questions, or silent severity reduction.

**Why this priority**: A refinement workflow must converge predictably or stop on a clearly owned decision.

**Independent Test**: Run fixtures with repairable and persistent high-severity contradictions and verify targeted invalidation, relevant re-checking, the two-cycle limit, and correct escalation.

**Acceptance Scenarios**:

1. **Given** the user grants bounded repair authorization before analysis and analysis reports a blocker, critical, or high finding, **When** repair begins, **Then** only the affected artifact and downstream dependents are regenerated.
2. **Given** a repair corrects the finding, **When** relevant checks rerun, **Then** the loop exits and the resolution is recorded.
3. **Given** the same finding survives two repair cycles without new evidence, **When** the limit is reached, **Then** the workflow stops and records a user-owned decision or explicit deferral.
4. **Given** a repair introduces a new high-severity contradiction, **When** the relevant checks run, **Then** automatic repair stops rather than expanding into an uncontrolled loop.
5. **Given** the user declines bounded repair authorization, **When** analysis reports a material finding, **Then** no artifact is edited and the finding remains explicitly blocked pending approval or deferral.
6. **Given** a proposed repair changes the constitution, feature scope, product priority, or risk tolerance, **When** the repair packet is classified, **Then** bounded authorization does not apply and a separate user decision is required.

---

### User Story 4 - Complete Reviews Efficiently and Recoverably (Priority: P2)

As a user, independent reviews complete concurrently when capacity exists, fall back to equivalent sequential execution when it does not, and resume safely after interruption.

**Why this priority**: Parallelism should reduce wait time without changing review inputs, leaking findings between reviewers, or risking shared-state corruption.

**Independent Test**: Exercise full, reduced, and interrupted worker capacity and verify stable inputs, isolation, deterministic aggregation, single-writer behavior, and safe reuse of matching completed results.

**Acceptance Scenarios**:

1. **Given** three worker slots are available, **When** review begins, **Then** all three independent reviews run concurrently.
2. **Given** fewer than three worker slots are available, **When** review begins, **Then** reviews are queued sequentially without changing role assignments or exposing earlier findings.
3. **Given** one worker times out, **When** its retry policy is exhausted, **Then** its configured fallback or explicit failure disposition is recorded before synthesis proceeds.
4. **Given** an interrupted run is resumed, **When** stored results still match the spec, brief, role configuration, and schema versions, **Then** they are reused; otherwise they are invalidated.
5. **Given** all candidates for a required role fail, **When** synthesis produces a draft, **Then** the missing perspective and affected coverage are visible and final readiness is blocked until the user reruns or explicitly waives that perspective.
6. **Given** a worker changes a protected artifact, **When** its result returns, **Then** the result is rejected, synthesis is aborted, and the drift is recorded.
7. **Given** the user explicitly waives an exhausted required role, **When** the final handoff is issued, **Then** it is labeled ready-but-degraded and identifies the missing perspective, affected coverage, waiver owner, and rationale.

---

### User Story 5 - Measure Workflow Quality Continuously (Priority: P2)

As a maintainer, I can detect orchestration regressions and determine whether multi-model review justifies its added effort using deterministic tests, representative fixtures, calibrated quality evals, and single-model comparisons.

**Why this priority**: Model orchestration cannot improve reliably without repeatable evidence and explicit regression gates.

**Independent Test**: Run the eval suite against the golden fixtures and verify deterministic gating, non-blocking quality reports, traceable failure evidence, and a comparable single-model control.

**Acceptance Scenarios**:

1. **Given** a deterministic contract or approved replay invariant regresses, **When** CI runs, **Then** CI fails with the affected case and criterion.
2. **Given** a model-judge quality score changes, **When** CI runs before calibration approval, **Then** the result is reported but does not block.
3. **Given** the same fixture is run through multi-model and single-model profiles, **When** results are scored, **Then** coverage, precision, unsupported claims, latency, and effort are reported side by side.
4. **Given** a production or human-review failure is accepted as representative, **When** the eval set is updated, **Then** it becomes a durable regression case.
5. **Given** a live session benchmark completes, **When** its result bundle is approved, **Then** it can be promoted into deterministic replay fixtures without requiring live model access in CI.
6. **Given** a handoff is marked ready, **When** a downstream implementation agent encounters a new material product or architecture decision, **Then** the exception is measured and promoted into the regression set.

### Edge Cases

- The current session exposes none of the bundled default models but does expose other selectable models.
- A model disappears after configuration validation but before its worker starts.
- A reviewer returns prose that does not conform to the finding contract.
- Two findings use different wording but seek the same decision or describe the same risk.
- A coverage item is inapplicable to the feature and must not lower the coverage score.
- A targeted follow-up returns findings outside its assigned blind spot.
- A repair fixes one artifact while leaving a downstream artifact stale.
- An interrupted run contains valid results for only a subset of roles.
- Reviewer completion order changes across runs.
- An eval judge is the same model family as a reviewed worker, creating correlated scoring risk.
- A user changes model overrides after reviews have already completed.
- A previously answered question is paraphrased by a later reviewer.
- A required role exhausts all fallbacks after other reviews have succeeded.
- A repair validation fails after producing a staged artifact set.
- A later analysis rephrases an existing contradiction and assigns it a new local ID.
- CI has replay fixtures but no active session model roster.

## Requirements *(mandatory)*

### Configuration and Invocation Contract

- The existing `$idea-refinery-full <idea>` form remains valid and uses bundled defaults.
- Invocation-scoped overrides use an optional `overrides.roles` block supplied with the request. Each role may set `model`, `reasoning_effort`, and an ordered `fallbacks` list.
- Repository-scoped defaults use `.idea-refinery/config.yaml` with the same versioned configuration shape.
- Bundled defaults use the skill's versioned default configuration.
- Precedence is invocation override, then repository configuration, then bundled default.
- An explicit model override is fail-fast unless the same override supplies fallback candidates. Bundled and repository assignments may use their configured fallbacks.
- The workflow displays and persists the resolved role assignments, fallbacks, concurrency, timeouts, retries, and repair limits before review dispatch.

Default fallback order:

| Role | Primary | Ordered fallbacks |
| --- | --- | --- |
| CEO reviewer | `gpt-5.5` | `gpt-5.6-sol`, `gpt-5.6-terra` |
| Product reviewer | `gpt-5.6-terra` | `gpt-5.6-sol`, `gpt-5.6-luna` |
| Architect reviewer | `gpt-5.6-sol` | `gpt-5.5`, `gpt-5.6-terra` |
| Eval runner | `gpt-5.6-luna` | `gpt-5.6-terra`, `gpt-5.6-sol` |
| Regression baseline | `gpt-5.4` | none; mark the live cross-generation baseline skipped if unavailable |

At dispatch, the workflow revalidates the selected model, then tries ordered candidates. It preserves requested reasoning effort when supported; otherwise it selects the highest supported effort not exceeding the request and records the adjustment. Exhaustion produces a failed-role disposition rather than an implicit substitution.

### Coverage Ownership Contract

| Coverage area | Primary role | Secondary role |
| --- | --- | --- |
| Value, positioning, strategic scope, reversibility | CEO | Product |
| Actors, journeys, requirements, configuration UX, acceptance criteria | Product | CEO |
| Interfaces, data, feasibility, reliability, security, operations, rollout, tests | Architect | Product |

The primary owner receives a targeted follow-up when available and non-failed. Otherwise the secondary owner is selected. A tie is resolved by the first non-degraded role whose declared scope covers the item. Every selection records the rule and evidence used.

### Persistence and Artifact Dependency Contract

- Each feature keeps a versioned run store under its active Spec Kit directory. A run stores the resolved configuration, immutable stage briefs, validated review envelopes, append-only trace events, repair packets, artifact hashes, and a manifest containing stage commit markers.
- `refinery-state.md` remains the human-readable controller summary and points to the active run; it is not the sole store for resumable worker results.
- Protected artifacts are persisted atomically. A stage is reusable only after its result artifacts and commit marker agree.
- The artifact dependency graph is: constitution and `spec.md` feed the plan and its supporting `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` outputs; the spec and all applicable plan outputs feed `tasks.md`; the constitution, `spec.md`, `plan.md`, applicable supporting outputs, and `tasks.md` feed analysis.
- A changed specification invalidates its checklist, plan outputs, tasks, and analysis. A changed plan or supporting output invalidates tasks and analysis. Changed tasks invalidate analysis. Accepted clarification answers are specification changes. Constitution changes invalidate all feature artifacts and always require separate approval.
- Repair writes to a staged artifact set created from a pre-repair checkpoint. The controller validates the staged set and atomically promotes it only when relevant checks pass and no new high-severity contradiction appears. Otherwise it restores the checkpoint and records the failed cycle.

### Functional Requirements

- **FR-001**: The full workflow MUST resolve required review roles against the models available in the current session before review execution.
- **FR-002**: The bundled default assignments MUST be CEO review with `gpt-5.5` at high reasoning, product review with `gpt-5.6-terra` at high reasoning, architect review with `gpt-5.6-sol` at high reasoning, quality evaluation with `gpt-5.6-luna` at medium reasoning, and regression baseline with `gpt-5.4` at medium reasoning.
- **FR-003**: Users MUST be able to override the model and reasoning effort independently for each role.
- **FR-004**: Explicit overrides MUST be validated against the current session roster and rejected with actionable available choices when invalid.
- **FR-005**: Bundled and repository role assignments MUST use deterministic ordered fallback candidates, dispatch-time roster revalidation, explicit reasoning-effort adjustment, and a terminal failed-role disposition when candidates are exhausted.
- **FR-006**: The complete resolved configuration MUST be recorded for reproducibility, including defaults, overrides, fallbacks, concurrency, retry, timeout, and repair limits.
- **FR-007**: CEO, product, and architect reviews MUST run concurrently by default when capacity is available.
- **FR-008**: The workflow MUST automatically queue reviews when capacity is insufficient without changing their frozen inputs, role configuration, or independence.
- **FR-009**: Reviewers MUST receive a frozen Spec v1, a stage brief of settled state, assigned stable coverage-item IDs, a bounded objective, evidence requirements, non-goals, an effort budget, and a required result format.
- **FR-010**: Reviewers MUST NOT receive another reviewer's findings before submitting their own result.
- **FR-011**: Review workers MUST be read-only with respect to shared feature artifacts, use immutable input snapshots, and run with write isolation when supported; otherwise the controller MUST verify protected-artifact hashes before accepting results and abort on drift.
- **FR-012**: Reviewer results MUST identify role, selected model, reasoning effort, input versions, attempt, completion status, findings, and one coverage attestation per assigned item with applicability, reviewed status, evidence references, and linked finding IDs.
- **FR-013**: Only the controller MUST update the question registry, decision queue, review ledger, coverage matrix, and Spec Kit artifacts.
- **FR-014**: The controller MUST validate all required reviewer results or explicit degraded/failure dispositions before synthesis starts; incomplete coverage attestations MUST reject the envelope and trigger the bounded retry policy.
- **FR-015**: The controller MUST derive an applicable coverage taxonomy from Spec v1 that includes user journeys, requirements, interfaces, data, reliability, security, operations, rollout, and test strategy.
- **FR-016**: Every material finding MUST map to applicable coverage items and affected requirement identifiers where present.
- **FR-017**: Semantically duplicate findings MUST be canonicalized without losing reviewer attribution or distinct evidence, and a persisted root identity based on affected requirements, artifacts, and completion criterion MUST retain aliases and `caused-by` or `supersedes` lineage across runs.
- **FR-018**: The coverage matrix MUST distinguish reviewed-with-no-finding, finding-raised, resolved, unresolved, blind-spot, and inapplicable states.
- **FR-019**: An applicable high-risk item without review evidence MUST be treated as a blind spot, not as successful coverage.
- **FR-020**: The workflow MAY issue at most one targeted follow-up review per synthesis pass, selected by the coverage ownership contract, restricted to uncovered high-risk items, and recorded with its selection rationale.
- **FR-021**: Every material finding and remaining blind spot MUST receive an accepted, rejected-with-rationale, deferred-with-trigger, or decision-needed disposition before handoff.
- **FR-022**: Before analysis, the workflow MUST request one explicit authorization that may cover at most two narrowly scoped repair cycles for blocker, critical, or high analysis findings; without authorization analysis remains read-only, and clarification outputs do not enter the severity-based repair loop.
- **FR-023**: Each repair attempt MUST use a repair packet containing evidence, affected requirements and artifacts, the smallest acceptable correction, and a completion check.
- **FR-024**: Repair MUST follow the artifact dependency contract, operate on a staged checkpoint, regenerate only invalidated artifacts and downstream dependents, rerun only relevant checks, and promote or restore atomically.
- **FR-025**: Automatic repair MUST allow no more than two cycles for the same persisted root finding, regardless of wording or local analysis ID changes.
- **FR-026**: Automatic repair MUST stop early when the same finding recurs without new evidence, a material user decision is required, or a repair creates a new high-severity contradiction.
- **FR-027**: The workflow MUST NOT silently reduce finding severity to achieve convergence.
- **FR-028**: Each repair cycle MUST record whether unresolved material risk decreased, stayed unchanged, or increased.
- **FR-029**: The feature-local run store MUST persist structured trace events for stage transitions, resolved model assignments, input identities, worker outcomes, retries, fallbacks, validation failures, artifact mutations, repair outcomes, and stage commit markers.
- **FR-030**: Resume logic MUST reuse a completed result only when its spec, stage brief, role configuration, result schema, protected-artifact hashes, and committed stage identity still match.
- **FR-031**: Deterministic contract tests and approved replay-fixture regressions MUST block CI on failure without requiring a live model session.
- **FR-032**: Uncalibrated model-judge quality scores MUST remain visible but non-blocking.
- **FR-033**: Quality evals MUST cover seeded-finding recall, unsupported-claim rate, reviewer diversity, coverage completeness, unnecessary-question rate, repair convergence, and requirement-to-task traceability.
- **FR-034**: A session-native live benchmark MUST compare the default three-model workflow with a single-model control on the same cases and emit a versioned result bundle reporting quality, latency, and effort; approved bundles MAY be promoted into deterministic replay fixtures.
- **FR-035**: Eval fixtures MUST include typical, edge, adversarial, interruption, fallback, duplicate-question, coverage-gap, and repair-limit cases.
- **FR-036**: A quality metric MUST become blocking only after its rubric and threshold demonstrate stable agreement with human labels and the policy change is explicitly approved.
- **FR-037**: A fallback-completed role MUST mark the run `degraded-fallback` and remain eligible for readiness when all coverage and finding gates pass; an exhausted required role MUST mark the run `failed-role` and prevent readiness until the role succeeds or the user explicitly waives it as a material risk decision, after which the verdict MUST be `READY FOR IMPLEMENTATION — DEGRADED` with the missing perspective, affected coverage, waiver owner, and rationale.
- **FR-038**: Bounded repair authorization MUST NOT cover constitution changes, scope expansion, product priority, risk-tolerance changes, or any repair whose smallest correction exceeds its repair packet; each requires a separate user decision.
- **FR-039**: Unanswered high-impact clarification questions MUST become `decision-needed`; accepted clarification answers MUST update the specification and invalidate downstream artifacts without being classified as repair findings.
- **FR-040**: The final refinement report MUST show resolved configuration, degraded or failed roles, unresolved coverage, repair history, live-versus-replay eval status, and any waived perspective.
- **FR-041**: The workflow MUST measure material product or architecture decisions newly required by downstream implementation agents and promote accepted exceptions into regression cases.

### Key Entities

- **Resolved Run Configuration**: The versioned, fully expanded assignment of roles, models, reasoning effort, concurrency, budgets, retry behavior, fallback candidates, and repair limits for one run.
- **Stage Brief**: The immutable subset of settled decisions, answered questions, open decisions, constraints, and relevant review state supplied to one stage or worker.
- **Review Result Envelope**: One worker's attributable completion status, input identities, run metadata, validated findings, and complete assigned coverage attestations.
- **Coverage Item**: One applicable product or engineering concern derived from the specification, with risk level, evidence, reviewer attribution, and current disposition.
- **Coverage Matrix**: The aggregate mapping from coverage items to reviewer evidence, findings, resolutions, and task coverage.
- **Root Finding**: A persisted identity for one material issue across rewording and analysis runs, including aliases and causal or supersession lineage.
- **Repair Packet**: A bounded correction request for one root finding, including evidence, affected artifacts, minimal correction, completion check, authorization classification, and cycle count.
- **Run Manifest**: The versioned identities, artifact hashes, and stage commit markers that make one orchestration run resumable and auditable.
- **Trace Event**: A structured record of an orchestration decision or outcome used for diagnosis, resume validation, and eval scoring.
- **Eval Case**: A versioned input fixture, expected invariants or labels, scoring rubric, and blocking policy.
- **Live Benchmark Bundle**: A versioned session-native multi-model or control run that can be reviewed and promoted into deterministic replay fixtures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the approved golden set, 100% of applicable high-risk coverage items are either supported by review evidence or explicitly identified as blind spots before synthesis completes.
- **SC-002**: Every blocker, critical, and high finding has an explicit resolution, deferral trigger, or user-owned decision at handoff.
- **SC-003**: No persisted root finding receives more than two automatic repair cycles, and persistent findings stop with a recorded reason.
- **SC-004**: All seeded duplicate-question fixtures complete without re-asking an already answered or decided underlying question.
- **SC-005**: All buildable requirements in final golden artifacts map to at least one implementation task, and all tasks map to a requirement, risk, or operational need.
- **SC-006**: With three worker slots available, median independent-review wall time is at least 30% lower than the equivalent sequential profile on the same fixture set.
- **SC-007**: Interrupted runs reuse 100% of still-valid completed review results and reuse 0% of results invalidated by changed inputs or configuration.
- **SC-008**: Deterministic orchestration and artifact-contract tests pass on every accepted change.
- **SC-009**: Before model-judge metrics become blocking, their pass/fail labels achieve at least 90% agreement with the approved human-labeled calibration set.
- **SC-010**: The default three-model profile improves seeded high-severity omission recall by at least 15 percentage points over the single-model control without increasing unsupported findings by more than 5 percentage points on the approved golden set.
- **SC-011**: A maintainer can identify the model assignment, input identity, fallback status, and repair history for every material finding from persisted run artifacts.
- **SC-012**: Every `READY FOR IMPLEMENTATION` handoff in the approved golden set results in zero newly required material product or architecture decisions during downstream implementation; every accepted exception becomes a regression case.

## Assumptions

- Full mode is a high-confidence workflow whose users accept additional model effort in exchange for independently reviewed, implementation-ready artifacts.
- The active Codex session exposes a selectable model roster and sufficient delegation capability for the default profile; reduced capacity is expected and supported.
- Model execution remains native to the active agent session. Local deterministic tooling does not call provider APIs, external model CLIs, or require model credentials.
- The existing Idea Refinery stage order, persistent decision protocol, independent-review rule, and single-controller synthesis remain authoritative.
- Human calibration uses a small representative golden set first and expands when real failures reveal missing cases.
- Result ordering does not affect synthesis semantics or stable identifiers.
- One explicit pre-analysis authorization is sufficient only for the bounded repair envelope defined by D-008; all other artifact edits retain their existing approval gates.

## Out of Scope

- Direct provider API integrations, external model CLI adapters, credential management, or a standalone model-serving runtime.
- Application-code implementation, issue creation, commits, pushes, deployment, or production monitoring as part of this refinement workflow.
- Unbounded reviewer expansion, worker-to-worker coordination, or unrestricted evaluator-optimizer loops.
- Replacing Spec Kit artifacts or the existing user approval gates with an autonomous implementation process.
