# Full workflow orchestration contract

## Pipeline

```text
Idea
  -> Superpowers brainstorming
  -> approved design + Spec Kit Spec v1
  -> independent CEO, product, and architect reviews
  -> synthesis + Spec v2
  -> Spec Kit clarify
  -> Spec Kit plan + tasks
  -> Spec Kit analyze
  -> resolve material gaps, or final handoff
```

`$speckit-analyze` requires all three artifacts: `spec.md`, `plan.md`, and `tasks.md`. Do not omit plan and tasks merely because they are not visualized in the original idea-refinement diagram.

## Required artifact locations

Use Spec Kit's active feature directory. It should contain:

- `spec.md` — product/behavior contract and clarified decisions
- `plan.md` — technical design and implementation approach
- `tasks.md` — ordered, traceable implementation work
- `refinery-state.md` — the persistent question registry, decision queue, review ledger, and stage log

`refinery-state.md` is always persisted in full mode. Keep a separate final refinement report alongside the feature artifacts only when the user asks to persist it.

## Finding format

```text
ID:
Reviewer: CEO | Product | Architect | Spec Kit
Severity: blocker | critical | high | medium | low
Artifact / section:
Evidence:
Why it matters:
Smallest proposed change:
Human decision required: yes | no
Resolution: accepted | rejected — rationale | deferred — trigger | decision-needed
```

## Final readiness gate

The final handoff is `implementation-ready` only when all conditions hold:

1. The user approved the design direction and all material decisions are recorded in `refinery-state.md`.
2. Every blocker, critical, and high-severity review/analyze finding is resolved, explicitly deferred with a trigger, or marked as a user-owned decision.
3. Spec Kit clarification is complete, or its remaining question is recorded as a decision-needed blocker.
4. `spec.md`, `plan.md`, and `tasks.md` agree on terminology, scope, interfaces, and acceptance criteria.
5. Every buildable requirement has task coverage; no task is untraceable to a requirement, risk, or operational need.
6. The final report names deferred scope, known risks, rollout/rollback expectations where relevant, and the test strategy.
7. Every component skill received a stage brief from `refinery-state.md`; no settled question was re-asked unless its reopen rationale is recorded.

Conclude with exactly one verdict:

- `READY FOR IMPLEMENTATION` — an implementation agent can proceed without making a material product or architecture decision.
- `BLOCKED ON DECISION` — name the decision ID, owner, options, recommendation, and impact.
