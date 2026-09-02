# Research: Refinery Quality Orchestration

## Decision 1: Preserve a hybrid skill/runtime boundary

**Decision**: Keep model roster discovery, delegation, and user interaction in `SKILL.md`; use a Python 3.11 support package only for deterministic inputs, validation, persistence, synthesis bookkeeping, and eval replay.

**Rationale**: The current session exposes the authoritative model roster and agent controls, while local code has no stable session-agent API. Separating the two makes orchestration usable now without provider credentials and makes its non-model behavior testable offline.

**Alternatives considered**:

- Provider SDK or external model CLI: rejected because it duplicates session capabilities, adds credentials, and violates the approved boundary.
- Instruction-only skill: rejected because precedence, hashes, resume rules, schema validation, and eval replay are too error-prone as prose-only behavior.
- Standalone service: rejected as unnecessary operational scope for a repository-local workflow.

## Decision 2: Use Python with two narrow runtime dependencies

**Decision**: Use Python 3.11+, PyYAML for user configuration, and jsonschema for Draft 2020-12 validation. Use dataclasses/enums and standard-library JSON, hashing, paths, and atomic replacement elsewhere.

**Rationale**: Python is widely available in Codex development environments and supports reliable file tooling. Reusing mature parsers avoids building security-sensitive YAML handling or duplicating schema rules.

**Alternatives considered**:

- JSON-only configuration: simpler but contradicts the approved `.idea-refinery/config.yaml` interface.
- Handwritten validators/parsers: fewer dependencies but creates two sources of contract truth and weak error reporting.
- TypeScript/Node: viable, but adds no benefit for a non-web file-oriented package in this repository.

## Decision 3: Treat the session model roster as explicit input

**Decision**: The controller serializes the current session’s available models and supported reasoning efforts into a roster snapshot passed to configuration resolution and recorded in the run manifest.

**Rationale**: Availability is time-sensitive and session-specific. An explicit snapshot makes resolution reproducible without pretending local code can discover session capabilities. Dispatch revalidation detects roster drift.

**Alternatives considered**:

- Probe CLIs or environment variables: rejected because they are not the active session roster.
- Hard-code only bundled models: rejected because defaults can become unavailable and overrides must be checked.
- Resolve availability only at dispatch: rejected because users need a complete preview before workers start.

## Decision 4: Use versioned JSON contracts with semantic validation

**Decision**: Define JSON Schema contracts for configuration, review results, repair packets, run manifests, and trace events. After structural validation, run semantic checks for cross-field rules such as complete coverage attestations, unique IDs, fallback semantics, and matching hashes.

**Rationale**: JSON schemas provide portable, inspectable envelopes; semantic validation handles rules that schema alone cannot express clearly. Both validation layers return stable error codes suitable for tests and recovery.

**Alternatives considered**:

- Markdown-only worker responses: rejected because completeness and replay cannot be validated deterministically.
- Python object serialization: rejected because it couples persisted artifacts to implementation details.
- One monolithic schema: rejected because independently versioned interfaces reduce invalidation scope.

## Decision 5: Make the run store append-oriented and stage-committed

**Decision**: Store immutable input/result objects by content identity, append JSONL trace events, and consider a stage complete only when its manifest entry, output hashes, and commit marker agree. Write via a sibling temporary file/directory, fsync where supported, then atomically replace.

**Rationale**: Partial worker completion and interrupted repairs are expected. Stage commits give resume logic a simple durable boundary and prevent half-written artifacts from being reused.

**Alternatives considered**:

- Markdown controller state alone: human-readable but not crash-consistent or exact enough for reuse.
- SQLite: strong transactions but unnecessary for the expected scale and less transparent in code review.
- Overwrite-in-place JSON: simple but vulnerable to interruption and ambiguous stage completion.

## Decision 6: Drive synthesis from coverage attestations

**Decision**: Derive stable coverage items before fan-out, assign them by the ownership table, and require one evidence-backed attestation per assigned item even when no finding exists. Normalize findings only after all independent results arrive.

**Rationale**: Counting findings rewards verbosity and cannot distinguish “reviewed and sound” from “not reviewed.” Attestations make blind spots observable and enable a single targeted follow-up for uncovered high-risk items.

**Alternatives considered**:

- Finding count or judge score alone: rejected because neither proves systematic review.
- Unlimited follow-up reviewers: rejected because latency/cost can grow without convergence.
- Shared reviewer scratchpad: rejected because it compromises independence and creates anchoring.

## Decision 7: Bound repair by root identity and staged invalidation

**Decision**: Analysis creates root findings based on affected requirements, artifacts, and completion criteria. With explicit authorization, each root may receive at most two repair cycles. Each cycle checkpoints the artifact DAG, changes the smallest affected set in staging, reruns relevant checks, and promotes atomically only if risk decreases and no new high-severity contradiction appears.

**Rationale**: A wording-based counter is easy to reset accidentally. Root lineage plus bounded staging provides predictable convergence and recovery while preserving approval boundaries.

**Alternatives considered**:

- Re-run the entire workflow after every finding: safe but wasteful and likely to change unrelated settled material.
- Unlimited evaluator/optimizer loop: rejected because it can oscillate and silently widen scope.
- Direct edits to live artifacts: rejected because a failed validation can leave inconsistent Spec Kit outputs.

## Decision 8: Split deterministic replay from live evaluation

**Decision**: CI runs contracts, properties, and approved replay bundles without model access. A session-native benchmark separately compares the three-model profile with a single-model control, reports quality/latency/effort, and requires explicit approval before its bundle becomes a golden replay fixture.

**Rationale**: Live model behavior and session availability are non-deterministic, costly, and unavailable in ordinary CI. Replay preserves known orchestration invariants while live benchmarks measure whether the architecture still earns its complexity.

**Alternatives considered**:

- Live model calls in required CI: rejected for availability, cost, and reproducibility.
- Deterministic tests only: rejected because they cannot measure omission recall or unsupported claims.
- Immediately blocking on an LLM judge: rejected until calibration demonstrates at least 90% human agreement.

## Decision 9: Use protected-artifact hashes as the portable isolation backstop

**Decision**: Prefer worker write isolation when supported; always record protected-artifact hashes before dispatch and verify them before accepting an envelope.

**Rationale**: Agent sandbox features can differ by session. Hash verification provides a portable trust-boundary check and turns unexpected mutation into a hard, attributable failure.

**Alternatives considered**:

- Instructions alone: rejected because accidental writes remain possible.
- Dedicated worktree for every reviewer: strong isolation but heavier than needed for read-only review and not universally available.

## Research provenance

The workflow direction is consistent with first-party guidance reviewed during discovery: use simple composable agent patterns, parallelize independent work, make evaluation outcome-oriented, and use trace-level evidence for diagnosing agent failures. Those principles informed the hybrid boundary, independent fan-out, coverage attestations, and replay/live-eval split; the feature’s exact limits and contracts are repository-specific decisions approved in this refinement.
