# Data Model: Refinery Quality Orchestration

## Entity relationships

```text
ResolvedRunConfiguration ──1:1── RunManifest ──1:N── StageCommit
          │                         │
          │                         ├──1:N── TraceEvent
          │                         ├──1:N── ReviewResultEnvelope
          │                         └──1:N── RepairPacket
          │
          └──1:N── RoleAssignment

ReviewResultEnvelope ──1:N── CoverageAttestation ──N:1── CoverageItem
ReviewResultEnvelope ──1:N── FindingAlias ──N:1── RootFinding
CoverageMatrix ──1:N── CoverageItem
RootFinding ──1:N── RepairPacket
EvalCase ──1:N── ReplayBundle / LiveBenchmarkBundle
```

## ResolvedRunConfiguration

Immutable, fully expanded configuration used by one run.

Fields:

- `schema_version`, `run_id`, `resolved_at`
- `sources`: bundled, repository, and invocation input identities
- `roster_snapshot`: available model IDs and supported reasoning efforts
- `roles`: mapping of CEO, Product, Architect, Eval, and Baseline to `RoleAssignment`
- `concurrency_limit`, `role_retry_limit`, `coverage_followup_limit`, `repair_cycle_limit`
- `timeouts`: validation and worker timeout policy

Validation:

- Required review roles exist exactly once.
- Explicit unavailable assignments fail unless the invocation supplies ordered fallbacks.
- Selected candidates occur in the captured roster; baseline alone may be `skipped-unavailable`.
- Limits do not exceed the feature maxima: role retry 1, follow-up 1, repair cycle 2.
- Reasoning effort is either requested or the highest supported effort below it, with an adjustment reason.

## RoleAssignment

Fields: `role`, `requested_model`, `selected_model`, `requested_reasoning_effort`, `selected_reasoning_effort`, `fallbacks`, `source`, `status`, and optional `degradation_reason`.

States:

```text
unresolved → validated → dispatched → completed
                  │            ├── retrying → completed
                  │            └── fallback → degraded-fallback
                  └──────────────────────────→ failed-role
baseline unavailable ────────────────────────→ skipped-unavailable
```

## StageBrief

Immutable input snapshot for one stage or worker.

Fields: `brief_id`, `stage`, `objective`, `non_goals`, `effort_budget`, `settled_decision_ids`, `answered_question_ids`, `open_decision_ids`, `coverage_assignments`, `artifact_hashes`, `schema_versions`, and `created_at`.

Validation: every referenced decision/question/coverage ID exists; another reviewer’s findings are absent from independent-review briefs; hashes match the frozen artifacts.

## ReviewResultEnvelope

One attributable worker response.

Fields: envelope/run/brief IDs, role, model, reasoning effort, attempt, completion status, input identities, start/end timestamps, findings, coverage attestations, protected-artifact hashes, and failure details.

Validation:

- Model and effort match the dispatch record.
- Every assigned coverage item has exactly one attestation.
- Every linked finding is present and maps to at least one coverage item.
- Completed envelopes contain no failure; failed envelopes contain a coded failure.
- Protected hashes are unchanged. Drift rejects the envelope and aborts synthesis.

## CoverageItem and CoverageMatrix

`CoverageItem` fields: stable ID, area, description, risk, applicability, primary and secondary roles, requirement IDs, evidence, linked root findings, disposition, and follow-up selection rationale.

Disposition states:

```text
pending
  ├── inapplicable
  ├── reviewed-no-finding
  ├── finding-raised → resolved
  │                  ├── unresolved
  │                  ├── deferred
  │                  └── decision-needed
  └── blind-spot → follow-up-pending → any terminal state above
```

An applicable high-risk item cannot be terminally successful without evidence. At most one item set may enter `follow-up-pending` per synthesis pass.

## RootFinding

Stable identity for a material issue across wording and runs.

Fields: `root_id`, semantic identity inputs (`requirement_ids`, `artifact_paths`, `completion_criterion`), severity, aliases, reviewer attribution, evidence, coverage IDs, lineage (`caused_by`, `supersedes`), disposition, and repair cycle count.

Validation: severity never decreases without a recorded evidence-backed disposition; aliases do not create new repair budgets; lineage is acyclic; every material finding has a terminal disposition before readiness.

## RepairPacket

Fields: packet/root/run IDs, cycle number, severity, evidence, affected requirements/artifacts, smallest acceptable correction, completion checks, invalidated downstream artifacts, authorization class/status, pre-repair hashes, staged location, and outcome.

States:

```text
proposed → authorization-required → authorized → staged → validating → promoted
              │                                      ├── rolled-back
              └── declined                           └── stopped
```

Stop conditions: cycle exceeds two, same root recurs without new evidence, a separate material decision is needed, proposed scope exceeds the packet, or validation finds a new high-severity contradiction. Constitution, scope, priority, and risk-tolerance changes can never enter `authorized` through bounded consent.

## RunManifest and StageCommit

`RunManifest` fields: schema/run/feature IDs, status, timestamps, resolved-config hash, active stage, artifact/schema hashes, stage commits, worker attempts, repair counters, prior run linkage, and optional waiver.

`StageCommit` fields: stage ID, input hashes, output hashes, commit-marker path/hash, completion time, and reusable flag.

Run states:

```text
created → configured → reviewing → synthesizing → planning → analyzing
   │          │             │            │             │          │
   └──────────┴─────────────┴────────────┴─────────────┴──→ blocked
                                                               │
analyzing → repairing → ready / ready-degraded                 │
     └─────────────────────────────────────────────────────────┘
```

Resume may reuse a stage only when all input identities, output hashes, schema versions, protected hashes, and the commit marker match.

## TraceEvent

Append-only event with `event_id`, `sequence`, `run_id`, `occurred_at`, `event_type`, `stage`, `actor`, `input_refs`, `output_refs`, and type-specific `data`. Sequence is strictly increasing within a run; existing records are never edited.

Required event families: configuration, stage transition, dispatch, completion, retry, fallback, validation rejection, artifact staging/promotion/rollback, follow-up selection, finding disposition, repair outcome, waiver, and stage commit.

## EvalCase and result bundles

`EvalCase` fields: case ID/version, family, frozen inputs, seeded findings, expected invariants, human labels, scoring rubric version, and blocking policy.

`ReplayBundle` contains stored envelopes/traces, deterministic expected outputs, implementation/schema versions, and provenance approval.

`LiveBenchmarkBundle` adds session roster, role assignments, multi-model/control outputs, quality metrics, latency, effort, judge identity, and promotion status. Promotion creates a new immutable replay fixture; it never overwrites an existing fixture.
