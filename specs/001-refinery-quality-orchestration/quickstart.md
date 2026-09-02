# Quickstart Validation Guide

This guide describes the runnable validation path expected after implementation. Commands are run from the repository root.

## Prerequisites

- Python 3.11 or newer
- The skill’s development dependencies installed from `idea-refinery-full/pyproject.toml`
- For the live benchmark only, an active Codex session exposing the configured models and worker capacity

## 1. Run deterministic quality gates

```bash
uv run --directory idea-refinery-full --project . pytest
```

Expected outcome: schema, unit, property, integration, and approved replay tests pass without network access or a live model session.

## 2. Validate configuration precedence

Create a temporary repository configuration that changes the Product reviewer, then resolve it with an invocation override for the same role and a controller-captured session roster. The invocation fixture is the serialized form of the request's versioned `overrides.roles` block; it is not a separate user-facing CLI model-discovery surface:

```bash
python -m idea_refinery.cli resolve-config \
  --repo-config .idea-refinery/config.yaml \
  --invocation-config idea-refinery-full/tests/fixtures/config/invocation-override.yaml \
  --session-roster idea-refinery-full/tests/fixtures/rosters/full.json
```

Expected outcome: invocation values win over repository values, repository values win over bundled defaults, all five roles are expanded, and the output records selected models, fallbacks, efforts, limits, and source provenance. An unavailable explicit model without invocation fallbacks exits non-zero and lists available choices.

## 3. Verify coverage-driven synthesis

```bash
python -m idea_refinery.cli replay \
  idea-refinery-full/tests/fixtures/replay/coverage-gap
```

Expected outcome: completed envelopes are accepted regardless of completion order; every assigned item has an attestation; duplicate findings share a root identity; the seeded high-risk omission becomes a blind spot and selects exactly one follow-up owner using the coverage ownership table.

## 4. Verify interrupted-run recovery

```bash
python -m idea_refinery.cli replay \
  idea-refinery-full/tests/fixtures/replay/interrupted-run
```

Expected outcome: committed, hash-matching results are reused; partial or mismatched stages are invalidated; the trace identifies each reuse or invalidation reason.

## 5. Verify the bounded repair loop

```bash
python -m idea_refinery.cli replay \
  idea-refinery-full/tests/fixtures/replay/repair-limit
```

Expected outcome: the root finding receives no more than two staged repair attempts, failed validation rolls back cleanly, aliases do not reset the counter, and persistent or newly introduced high-severity risk stops the loop with `decision-needed` or `blocked`.

## 6. Exercise the full skill in a live session

Invoke `$idea-refinery-full` normally with no overrides. Before review dispatch, verify the displayed resolved defaults:

- CEO: `gpt-5.5` / high
- Product: `gpt-5.6-terra` / high
- Architect: `gpt-5.6-sol` / high
- Eval: `gpt-5.6-luna` / medium
- Baseline: `gpt-5.4` / medium

Expected outcome: the three independent reviews run concurrently when slots exist or queue without input changes, workers return validated envelopes, synthesis reports coverage rather than finding volume, and only the controller changes shared artifacts.

## 7. Run the non-blocking live comparison

From an active session, use the skill’s live-eval stage on the approved benchmark cases. The controller, not the Python package, dispatches both profiles.

Expected outcome: a versioned bundle compares the default three-model profile with the single-model baseline on coverage, seeded high-severity recall, unsupported claims, diversity, unnecessary questions, latency, and effort. Judge scores remain informational until calibrated; promotion into replay fixtures requires explicit approval.

## Readiness checks

A normal handoff is ready only when all required perspectives complete, all high-risk coverage is evidenced or dispositioned, all material findings are resolved/deferred/decision-owned, repair limits are respected, and traceability checks pass. If a failed required perspective is explicitly waived, the exact verdict is `READY FOR IMPLEMENTATION — DEGRADED` and the report includes the missing role, affected coverage, waiver owner, and rationale.
