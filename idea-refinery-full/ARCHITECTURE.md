# Idea Refinery Full Architecture

How `$idea-refinery-full` turns a user-approved idea into independently reviewed, repair-bounded, implementation-ready Spec Kit artifacts.

## Purpose and boundary

`$idea-refinery-full` is an explicit-only refinement workflow. It produces an active Spec Kit feature containing:

```text
spec.md + plan.md + tasks.md + refinery-state.md
```

The workflow stops before application-code implementation. A ready handoff may point to `$idea-refinery-implement`, but the implementation skill requires a separate user invocation because it has broader mutation authority.

The system has two cooperating layers:

| Layer | Owns | Does not own |
| --- | --- | --- |
| Session controller | Repository inspection, approvals, user dialogue, model-roster capture, component-skill loading, reviewer dispatch, artifact synthesis, and all shared writes | Provider APIs, credential stores, or hidden background model calls |
| Deterministic Python package | Configuration resolution, schemas, hashing, review-envelope validation, coverage, persistence, invalidation, repair transactions, readiness, and replay evaluation | Model discovery, model execution, user decisions, or external model CLIs |

Component skills perform bounded stages. Reviewers receive immutable briefs and return findings; they never rewrite shared artifacts. The controller is the single writer for `refinery-state.md` and the active Spec Kit files.

## End-to-end flow

```text
Idea + repository context
  -> setup and state initialization
  -> Superpowers brainstorming
  -> approved design
  -> Spec Kit Spec v1
  -> independent CEO + Product + Architect reviews
  -> coverage synthesis and Spec v2
  -> Spec Kit clarification
  -> Spec Kit plan + tasks
  -> Spec Kit analysis
  -> optional targeted repair (0..2 cycles)
  -> readiness verdict
```

Decision points are sequential because they require one authoritative user or controller decision. Independent reviews run concurrently when capacity permits, but each reviewer receives the same frozen Spec v1 and cannot read another review before returning.

## What each step does

| Step | Question answered | Mechanism | Main output | Difference from the next step |
| --- | --- | --- | --- | --- |
| Setup | Can refinement safely start here? | Inspect instructions, `.specify/`, active feature, and prior state | Confirmed target and initialized state | Establishes authority and location; it does not define the product |
| Brainstorming | What should be built, for whom, and why? | Superpowers `$brainstorming` | User-approved design direction | Explores alternatives; Spec v1 turns the chosen direction into a testable contract |
| Spec v1 | What behavior is proposed? | `$speckit-specify` | Initial `spec.md` | States the proposal; independent review tries to break it |
| Independent review | What did the proposal miss? | CEO, Product, and Architect frozen briefs | Findings and coverage attestations | Produces criticism only; synthesis decides how findings affect the spec |
| Synthesis / Spec v2 | Which findings change the contract? | Controller deduplication and review ledger | Revised `spec.md` and finding dispositions | Resolves known findings; clarification targets remaining ambiguity |
| Clarification | Which unanswered detail would change implementation or validation? | `$speckit-clarify` with the settled-state brief | Accepted answers in `spec.md`, or a decision blocker | Resolves questions; planning chooses the technical delivery approach |
| Plan and tasks | How will the behavior be built and ordered? | `$speckit-plan` then `$speckit-tasks` | `plan.md`, supporting design artifacts, and `tasks.md` | Creates implementation structure; analysis checks cross-artifact agreement |
| Analysis | Do spec, plan, and tasks agree? | Read-only `$speckit-analyze` | Consistency and traceability report | Detects gaps without editing; repair may correct authorized material gaps |
| Repair | Can a reported gap be corrected narrowly and safely? | Checkpointed staged transaction | Promoted corrected artifacts or rollback | Changes only the invalidated closure; handoff evaluates the final state |
| Handoff | Can implementation proceed without a new material decision? | Readiness gate | One terminal verdict | Ends refinement; it never starts implementation automatically |

Clarification and repair are deliberately different. Clarification records a new accepted answer and invalidates downstream artifacts. Repair corrects a blocker, critical, or high-severity inconsistency inside an already approved scope and requires bounded authorization.

## Review architecture

| Reviewer | Primary focus | Typical failure found |
| --- | --- | --- |
| CEO | Value, positioning, scope, strategic risk, and reversibility | A technically sound feature that does not solve a valuable problem |
| Product | Actors, journeys, requirements, configuration experience, and acceptance criteria | A missing state, actor, or user-visible failure path |
| Architect | Feasibility, interfaces, data, reliability, security, operations, rollout, and tests | A plan that cannot be operated, secured, rolled back, or verified |

Before dispatch, the controller derives stable `COV-*` coverage IDs and assigns each item a primary and secondary owner. Every reviewer must attest to its assigned items, including reviewed-with-no-finding cases. Missing evidence for applicable high-risk coverage is a blind spot rather than a pass.

Each finding records its reviewer, severity, affected section, evidence, impact, smallest change, decision requirement, and disposition. Synthesis canonicalizes duplicate root findings while preserving all reviewer attribution.

The controller may send one targeted coverage follow-up per synthesis pass. It selects the primary owner first, then the secondary owner, then a deterministic scope tie-break.

## Model and configuration resolution

Configuration precedence is:

```text
invocation overrides.roles
  > repository .idea-refinery/config.yaml
  > idea-refinery-full/defaults/config.yaml
```

The controller captures the models and reasoning efforts available in the active session. The deterministic package resolves each role against that roster and persists the complete assignment before dispatch.

- An explicit unavailable invocation model fails unless that override provides fallbacks.
- Bundled and repository assignments try their ordered fallbacks.
- Unsupported effort may clamp only to the highest supported effort at or below the request.
- Every fallback or effort adjustment is recorded.
- An exhausted required role blocks readiness unless the user explicitly grants a degraded waiver.

The Python package never discovers models or calls them. It only validates the roster snapshot supplied by the controller.

## State and persistence

```text
specs/<feature-id>/
├── spec.md
├── plan.md
├── tasks.md
├── refinery-state.md                 # human-readable control plane
└── runs/<run-id>/                    # authoritative resume plane
    ├── manifest.json
    ├── events.jsonl
    ├── objects/<category>/<hash>.json
    └── commits/<stage>-<hash>.json
```

`refinery-state.md` prevents lost or repeated decisions:

- `D-*` identifies user-owned product, strategy, scope, or risk decisions.
- `Q-*` identifies material questions, including suppressed duplicates and reopened questions.
- `R-*` identifies material review and analysis findings.
- The run/repair ledger and stage log explain what happened and what each component received.

Questions are compared by the underlying decision, actor, behavior, constraint, or acceptance criterion, not by exact wording. A settled question can reopen only when new evidence changes the trade-off; the prior ID and evidence must be recorded first.

`RunStore` supplies content-addressed immutable objects, append-only trace events, atomic manifest updates, protected hashes, and stage commit markers. A completed stage is reusable only when its marker and input, configuration, schema, and protected-artifact hashes still match.

## Coverage states

Coverage tracks journeys, requirements, interfaces, reliability, security, operations, rollout, data, and tests. An item moves through explicit states such as:

```text
pending -> reviewed-no-finding | finding-raised | inapplicable
finding-raised -> resolved | unresolved
blind-spot -> follow-up-pending -> reviewed or unresolved
```

A quiet reviewer result is meaningful only when it includes evidence-backed attestations. Completion order never changes aggregation order or finding identity.

## Repair and invalidation

Artifact dependencies flow downstream:

```text
constitution + spec
  -> plan, research, data model, contracts, quickstart
  -> tasks
  -> analysis
```

Changing one artifact invalidates only its transitive dependents. A repair cycle:

1. Starts from one user authorization covering at most two cycles per canonical root finding.
2. Builds a packet containing evidence, affected requirements and artifacts, the smallest correction, completion checks, and the invalidation closure.
3. Applies changes to a sibling staged artifact tree.
4. Re-runs only relevant checks.
5. Promotes the whole staged tree atomically when checks pass and risk does not increase; otherwise it rolls back.

The root cause, not a renamed task or local finding ID, owns the cycle budget. Repair stops on missing authorization, an excluded decision class, work outside the packet, a recurring root without new evidence, two-cycle exhaustion, a new high-severity contradiction, or non-decreasing risk. Constitution changes, scope changes, product priority, and risk tolerance always return to the user.

## Readiness outcomes

The handoff verifies design approval, decision and finding dispositions, completed clarification, artifact consistency, requirement-to-task traceability, known risks, rollout and rollback expectations, test strategy, and state-brief use at every stage.

It returns exactly one of:

```text
READY FOR IMPLEMENTATION
READY FOR IMPLEMENTATION — DEGRADED
BLOCKED ON DECISION
```

`DEGRADED` requires an explicit user waiver after a required role and its fallbacks are exhausted. The report names the missing perspective, affected coverage, waiver owner, and rationale.

## Deterministic runtime and quality gates

The CLI adapter is available through:

```bash
uv run --project idea-refinery-full idea-refinery <command>
```

It resolves configuration, creates and validates briefs/envelopes, builds coverage, synthesizes results, checks invalidation and repair packets, manages run state, and runs replay/readiness evaluation. It never executes a model.

Blocking gates include schemas and semantic contracts, deterministic tests, approved replay fixtures, protected hashes, and requirement-to-task traceability. Live multi-model comparisons and model-judge scores remain advisory until calibration and explicit policy promotion make them trustworthy enough to block.

## Non-goals

`$idea-refinery-full` does not implement application code, access provider credentials, run hidden model clients, create issues, commit, push, open pull requests, merge, or deploy.

## Related documentation

- [Skill entrypoint](SKILL.md)
- [Normative orchestration contract](references/orchestration-contract.md)
- [Refinery state template](references/refinery-state-template.md)
- [Default role configuration](defaults/config.yaml)
- [Repository structure](../RepoStructure.md)
- [Implementation skill architecture](../idea-refinery-implement/ARCHITECTURE.md)
- [Quality-orchestration feature artifacts](../specs/001-refinery-quality-orchestration/plan.md)
