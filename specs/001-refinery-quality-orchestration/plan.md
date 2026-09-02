# Implementation Plan: Refinery Quality Orchestration

**Branch**: `v2` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-refinery-quality-orchestration/spec.md`

## Summary

Evolve `$idea-refinery-full` into a hybrid orchestration system: the skill remains the user-facing, session-native controller for model roster discovery and worker dispatch, while an embedded Python package supplies deterministic configuration resolution, schema validation, versioned run persistence, coverage synthesis, bounded repair bookkeeping, and replay evaluation. Independent CEO, Product, and Architect reviews run in parallel when capacity permits, consume immutable inputs, and return validated coverage attestations. A single controller synthesizes their outputs, performs at most one coverage-targeted follow-up, and may execute at most two explicitly authorized, staged repair cycles.

## Technical Context

**Language/Version**: Python 3.11+ for deterministic tooling; Markdown/YAML for skill and user configuration

**Primary Dependencies**: PyYAML 6.x for `.idea-refinery/config.yaml`; jsonschema 4.x for Draft 2020-12 contracts; no provider SDKs or model CLIs

**Storage**: Feature-local JSON/JSONL/Markdown files with SHA-256 identities, temporary sibling staging directories, atomic file replacement, and stage commit markers

**Testing**: pytest, pytest-cov, Hypothesis for state/config invariants; JSON Schema contract tests; approved golden replay fixtures; session-native live benchmark kept outside ordinary CI

**Target Platform**: Codex sessions on POSIX development environments with Python 3.11+; CI requires no model access

**Project Type**: Embedded skill plus deterministic support library and command entry point

**Performance Goals**: Configuration and envelope validation under 250 ms for normal artifacts; deterministic synthesis independent of worker completion order; three-worker review median wall time at least 30% below equivalent sequential review

**Constraints**: Model availability comes only from the active session; workers never mutate shared feature artifacts; controller is the sole writer; maximum one retry per role, one coverage follow-up per synthesis pass, and two repair cycles per root finding; no credentials or provider integrations

**Scale/Scope**: Five configurable roles, three required review roles, tens to low hundreds of coverage items/findings per run, and small feature-local run stores retained for audit and replay

## Constitution Check

The repository constitution is an unratified Spec Kit placeholder and therefore defines no enforceable project principles. This plan does not amend or infer a constitution. Until governance is separately ratified, the following feature-spec gates apply:

- **Session-native boundary — PASS**: deterministic tooling accepts a controller-captured model roster and never discovers or invokes provider models itself.
- **Single-writer isolation — PASS**: workers receive immutable snapshots; only the controller promotes staged artifacts.
- **Bounded autonomy — PASS**: targeted follow-up, retries, and repair cycles have hard limits and explicit stop conditions.
- **Traceability — PASS**: contracts carry input hashes, model assignments, coverage evidence, finding lineage, and stage identities.
- **Offline CI — PASS**: blocking tests use deterministic contracts and approved replay fixtures; live model benchmarks are separately invoked.
- **Backward compatibility — PASS**: the existing `$idea-refinery-full <idea>` invocation remains valid with bundled defaults.

Post-design re-check: **PASS**. The schemas and entity transitions below preserve every gate. Ratifying a project-wide constitution remains a separate governance decision and would invalidate these artifacts for re-check.

## Architecture and Data Flow

```text
user invocation + repo config + bundled defaults + session model roster
                              │
                              ▼
                   deterministic config resolver
                              │ resolved snapshot
                              ▼
                session-native controller / sole writer
                     │ immutable briefs + hashes
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       CEO worker  Product    Architect       (parallel or queued)
          └──────────┼──────────┘
                     │ validated result envelopes
                     ▼
             coverage-driven synthesizer
                     │ optional single focused follow-up
                     ▼
                Spec Kit artifacts
                     │ read-only analysis
                     ▼
        authorized staged repair loop (0..2 cycles)
                     │
                     ▼
             readiness report + replay bundle
```

The Python package is a deterministic sidecar, not an agent runtime. The skill gathers the roster exposed by the active session, performs actual delegation with session tools, and supplies snapshots/results to the package. This keeps model execution portable across sessions while making validation, recovery, and evaluation reproducible.

## Project Structure

### Documentation (this feature)

```text
specs/001-refinery-quality-orchestration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── config.schema.json
│   ├── invocation.schema.json
│   ├── repair-packet.schema.json
│   ├── review-result.schema.json
│   ├── run-manifest.schema.json
│   └── trace-event.schema.json
└── tasks.md
```

### Source Code (repository root)

```text
idea-refinery-full/
├── SKILL.md
├── pyproject.toml
├── references/
│   ├── orchestration-contract.md
│   └── refinery-state-template.md
├── defaults/
│   └── config.yaml
├── schemas/
│   └── *.schema.json
├── src/idea_refinery/
│   ├── cli.py
│   ├── config.py
│   ├── coverage.py
│   ├── envelopes.py
│   ├── findings.py
│   ├── repair.py
│   ├── run_store.py
│   └── evals/
│       ├── replay.py
│       ├── scoring.py
│       └── promotion.py
└── tests/
    ├── contract/
    ├── fixtures/
    │   ├── adversarial/
    │   ├── golden/
    │   └── replay/
    ├── integration/
    ├── property/
    └── unit/

.github/workflows/
└── refinery-evals.yml
```

**Structure Decision**: Keep all executable support code, defaults, schemas, and tests inside `idea-refinery-full/` so the skill remains distributable as one unit. Mirror the feature contract schemas into `idea-refinery-full/schemas/` during implementation and test them for byte-equivalent canonical content. The root contains only CI integration and Spec Kit design artifacts.

## Component Responsibilities

- `SKILL.md`: stage ordering, user approvals, current-session model roster capture, worker spawning/queuing, and final readiness wording.
- `references/orchestration-contract.md` and `references/refinery-state-template.md`: durable workflow/readiness contract and human controller-state shape; both must stay synchronized with the executable schemas and skill instructions.
- `config.py`: merge invocation, repository, and bundled configuration; validate roster availability; choose fallbacks and clamp reasoning effort; emit a resolved immutable snapshot.
- `run_store.py`: create versioned runs, hash artifacts, append trace events, validate resume eligibility, and commit staged stages atomically.
- `envelopes.py`: JSON Schema validation plus semantic checks such as complete assigned coverage attestations and protected-artifact hash equality.
- `coverage.py` and `findings.py`: derive stable coverage IDs, map evidence, canonicalize root findings, preserve aliases/lineage, and select the deterministic follow-up owner.
- `repair.py`: classify authorization, build bounded repair packets, calculate artifact invalidation, track cycle counts by root identity, and stop on unsafe convergence signals.
- `evals/`: score deterministic replay bundles, compare multi-model versus single-model results, and promote explicitly approved live bundles into golden fixtures.

## Delivery Sequence and Parallel Work

1. Freeze contract versions and canonical serialization rules.
2. In parallel, implement configuration resolution and run-store primitives against those contracts.
3. In parallel after core schemas stabilize, implement envelope/coverage/finding logic and the repair state machine.
4. Integrate the deterministic commands into `SKILL.md`, keeping session dispatch in the controller.
5. In parallel, build fixture families and deterministic replay scoring while integration scenarios exercise interruption, fallback, isolation, and repair rollback.
6. Add CI gates and documentation, then run the full deterministic suite and one non-blocking live benchmark.

Parallel tasks must own disjoint files or be explicitly sequenced. Contract/schema changes are a synchronization barrier because every downstream lane consumes them. Only the controller-facing integration lane may change `SKILL.md`.

## Evaluation Strategy

Blocking CI layers:

1. Schema and semantic contract validation.
2. Unit and property tests for precedence, fallback, stable identity, retry/follow-up ceilings, invalidation, atomic promotion, and resume matching.
3. Golden replay regressions for typical, edge, adversarial, interrupted, duplicate-question, coverage-gap, and repair-limit cases.
4. Traceability checks requiring every buildable requirement to map to a task and every task to a requirement, risk, or operational need.

Non-blocking layers until calibrated:

- Session-native live A/B runs of the three-model default versus the `gpt-5.4` single-model control.
- Model-judge scores for seeded-finding recall, unsupported claims, reviewer diversity, coverage completeness, unnecessary questions, and repair quality.
- Latency and effort telemetry.

A quality threshold becomes blocking only after its rubric reaches 90% agreement with approved human labels and the policy change is explicitly approved. Live result promotion is reviewable and never automatic.

## Rollout and Compatibility

- Introduce the deterministic package behind the existing full-mode invocation; absent repo/invocation configuration uses bundled defaults.
- First release records both legacy Markdown state and the versioned run store, with the run manifest authoritative for resume and `refinery-state.md` authoritative only as the human summary.
- Treat older runs without compatible manifest/schema versions as non-reusable; preserve them for audit.
- Surface fallback, failed-role, waiver, and live-eval status in the final report. No silent migration or model substitution is permitted.

## Complexity Tracking

No constitution violations are recorded because no constitution has been ratified. The hybrid split is necessary: session APIs are the only supported model-execution surface, while deterministic offline tooling is required for reproducible validation and CI.
