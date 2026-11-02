# f-auditor quickstart and acceptance guide

These are implementation-target commands. Refinement has not created the executable, installed the skill, audited sessions or populated the improvement backlog.

## Prerequisites

- The separately implemented `f-auditor/` package and canonical skill are present.
- Python 3.11+ and uv; initial support is macOS/POSIX.
- At least one supported native analysis runtime with its existing authentication and required non-mutating capability boundary. The helper does not repair/install/authenticate runtimes automatically.
- Read permission for the intended Hermes/Codex history sources; write permission for the one explicit backlog destination.
- Host/version closure evidence is compatible; unavailable or uncertain closure must be reported as partial, not represented as complete coverage.

## Manual invocation after implementation

From any directory, use the same fixed checkout and backlog path:

    uv run --project /Users/nalin-ai/GitRepo/IdeaRefinery-worktrees/func-audit/f-auditor f-auditor audit --root /Users/nalin-ai/GitRepo --backlog /Users/nalin-ai/GitRepo/IdeaRefinery-worktrees/func-audit/functional-improvement/issues.md --runtime codex

For a structured result, append `--json`. A supported Hermes analysis backend can be selected with `--runtime hermes`; that choice does not change which hosts' sessions are collected.

This command captures a fixed 24-hour window, reads whole eligible closed sessions under GitRepo, validates contextual findings and updates the specified shared file. New issues are Not Fixed. No fixes or scheduled jobs are performed.

Expected exit semantics, not fabricated execution results:

- 0: full coverage and committed/unchanged backlog.
- 2: partial coverage, with named source/session/chunk gaps or unresolved classification; safe validated findings may have been committed.
- 1: failed/unavailable prerequisites, contract failure or write conflict, with explicit update state.

Inspect the source/version/closure coverage summary before interpreting a zero-findings result. Codex archive or turn-completion metadata alone is insufficient closure proof. An entirely uncertain source must remain visible in the report.

## Contributor completion

During audits, contributors use the same helper; direct file edits are supported between runs only. After verifying a fix, run:

    uv run --project /Users/nalin-ai/GitRepo/IdeaRefinery-worktrees/func-audit/f-auditor f-auditor complete <FI-issue-id> --backlog <the-same-absolute-path> --fixed-at <UTC-instant> --fix-evidence <reference-or-explanation> --owner <name>

The command records Completed and fix evidence; it does not apply the fix. Existing manual completed status remains preserved even when fix evidence is missing. Potential recurrence without chronology is an explicit unresolved classification, not an unsupported regression. A proved recurrence creates a separate Not Fixed regression linked to the completed predecessor.

## Deterministic verification after implementation

    uv run --project f-auditor --extra dev pytest f-auditor/tests
    uv run --project refine-idea --extra dev pytest refine-idea/tests
    python3 tools/sync_host_skills.py --check

Run repository distribution tests as well using the project's supported Python test environment. All commands must return real output before completion is claimed.

## Acceptance scenarios

1. Eligibility: prepared histories from both hosts include closed/open/unknown states, actual activity on window boundaries, pre-window context, outside-root paths, multiple profiles, compression/forks and incomplete pagination. Verify selection and every recorded disposition.
2. Analysis quality: reviewed positive/negative cases require every expected root problem and valid contextual evidence, excluding unrelated/context-disproved candidates. An empty analyzer fails positive cases; exact wording and uncalibrated judge scores are not acceptance metrics. In addition to deterministic replay, genuine analyzer execution through the actual launcher must process annotated positive and negative cases and retain sanitized input/output provenance; canned results cannot pass this gate. If runtime or credentials are unavailable, this acceptance is not verified.
3. Shared file: group repeated roots and origin evidence; preserve human status/priority/notes; show actionable priorities; repeat identical evidence without duplicates; prove regression only from post-fix evidence. Status-only completion remains completed with a missing-evidence diagnostic.
4. Coordination: concurrently run audit and contributor completion using the shared lock; confirm latest completion is retained. Inject lock timeout, source-read failure, malformed backlog, unexpected byte drift and interruptions before/after promotion; confirm no unsafe overwrite or duplicate replay.
5. Stable destination: invoke from two different in-scope repositories with the same arguments/configuration and confirm the same file changes, with no local competing backlog.
6. Safety: representative credentials and transcript instructions do not reach persisted/console/runtime output or trigger transcript-directed tools. Check both normal and error paths.
7. Native trial: exercise the implemented manual command with real supported runtime and native history sources, record actual redacted outcome/coverage and source hashes, and verify histories remain unchanged. Do not substitute mocked/seeded responses for unavailable live execution. Synthetic fixtures are labeled test data and cannot prove native closure or live analysis.

## Deferred operation

No schedule is installed. Once manual results earn confidence, scheduling requires a separate request, the same absolute destination and coordination protocol, and handling partial/failed exit outcomes. Windows auditing, remote sources, automatic fixes and public publishing are deferred.
