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

The command records Completed and fix evidence and immediately removes the issue from the actionable index in the same locked atomic write, preserving unrelated issue blocks and human notes; it does not apply the fix. Existing manual completed status remains preserved even when fix evidence is missing. Potential recurrence without chronology is an explicit unresolved classification, not an unsupported regression. A proved recurrence creates a separate Not Fixed regression linked to the completed predecessor.

## Deterministic verification after implementation

    uv run --project f-auditor --extra dev pytest f-auditor/tests -m "not native_compatibility and not live_analysis"
    uv run --project refine-idea --extra dev pytest refine-idea/tests
    python3 tools/sync_host_skills.py --check

Run repository distribution tests as well using the project's supported Python test environment. T046 adds this credential-free auditor command as a separate CI job and includes `f-auditor/**` in push and pull-request triggers. Native compatibility and actual-launcher acceptance are excluded only from deterministic CI, not from feature acceptance: run `uv run --project f-auditor --extra dev pytest f-auditor/tests -m "native_compatibility or live_analysis"` separately on a supported host with existing authentication. Unavailable prerequisites leave those gates unverified. All commands must return real output before completion is claimed.

## Acceptance scenarios

1. Eligibility: prepared histories from both hosts include closed/open/unknown states, actual activity on window boundaries, pre-window context, outside-root paths, multiple profiles, compression/forks and incomplete pagination. Verify selection and every recorded disposition.
2. Analysis quality: reviewed positive/negative cases require every expected root problem and valid contextual evidence, excluding unrelated/context-disproved candidates. An empty analyzer fails positive cases; exact wording and uncalibrated judge scores are not acceptance metrics. In addition to deterministic replay, genuine analyzer execution through the actual launcher must process annotated positive and negative cases and retain sanitized input/output provenance; canned results cannot pass this gate. If runtime or credentials are unavailable, this acceptance is not verified.
3. Shared file: group repeated roots and origin evidence; preserve human status/priority/notes; show actionable priorities; repeat identical anchors with reordered IDs or changed supporting citations without duplicates or changed timing. A pre-fix failure cited with post-fix discussion is not regression; a post-fix failure with pre-fix context can be. Anchors spanning the fix boundary or missing trustworthy timestamps remain unresolved; anchors exactly at fix time are not subsequent. Status-only completion remains completed with a missing-evidence diagnostic.
4. Coordination: concurrently run audit and contributor completion using the shared lock; confirm latest completion is retained and immediately absent from the actionable index without another audit. Preserve unrelated issue blocks and human notes byte-for-byte. Inject lock timeout, source-read failure, malformed backlog, unexpected byte drift and interruptions before/after promotion; confirm status and index are atomically consistent with no unsafe overwrite or duplicate replay.
5. Stable destination: invoke from two different in-scope repositories with the same arguments/configuration and confirm the same file changes, with no local competing backlog.
6. Safety: representative credentials and transcript instructions do not reach persisted/console/runtime output or trigger transcript-directed tools. Check both normal and error paths.
7. Native trial: exercise the implemented manual command with real supported runtime and native history sources, record actual redacted outcome/coverage and source hashes, and verify histories remain unchanged. Do not substitute mocked/seeded responses for unavailable live execution. Synthetic fixtures are labeled test data and cannot prove native closure or live analysis.

## Deferred operation

No schedule is installed. Once manual results earn confidence, scheduling requires a separate request, the same absolute destination and coordination protocol, and handling partial/failed exit outcomes. Windows auditing, remote sources, automatic fixes and public publishing are deferred.

## Reading bundled refinement evidence

The historical run's [relocation map](runs/20261101T204330Z-f-auditor/relocation.json)
maps the exact `source_run_root + "/"` prefix to `destination_run_root`, relative
to the map's directory. Strip only that prefix; resolve the remaining path (or an
already run-relative reference) beneath that directory. Reject escapes, unmapped
absolute paths and missing files; never fall back to the old machine.

Apply this lookup to all run-file references, including manifest fields, nested
brief paths, event data and references quoted in frozen state or snapshots.
Do not replace historical user requirements, configured audit roots or review
quotations. Integrity mapping is **identity**: all original objects, hashes,
dependent hashes, marker/manifest/event chains and timestamps remain unchanged.
Hash original parsed JSON with `idea_refinery.io.content_hash`, never a rewritten
view. The map's external historical repair scratch directory is unavailable;
do not reconstruct it or missing objects from current feature files.

The existing runtime does **not** consume this map: this is archive reading,
not a portable-resume claim. From the repository root, set `REF` to a run-relative
path or an original absolute reference copied from any nesting depth:

```sh
RUN=specs/006-f-auditor/runs/20261101T204330Z-f-auditor
REF=manifest.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=refine-idea/src python3 - "$RUN" "$REF" <<'PY'
import json
import sys
from pathlib import Path
from idea_refinery.io import content_hash, ensure_within

run = Path(sys.argv[1]).resolve()
mapping = json.loads((run / "relocation.json").read_text(encoding="utf-8"))
root = ensure_within(run, run / mapping["destination_run_root"])
reference = sys.argv[2]
prefix = mapping["source_run_root"] + "/"
relative = reference[len(prefix):] if reference.startswith(prefix) else reference
if Path(relative).is_absolute():
    raise SystemExit("Unmapped historical location; no local evidence asserted")
path = ensure_within(root, root / relative)
if not path.is_file():
    raise SystemExit(f"Missing bundled evidence: {relative}")
text = path.read_text(encoding="utf-8")
if path.is_relative_to(root / "objects"):
    if content_hash(json.loads(text)) != path.stem:
        raise SystemExit(f"Object hash mismatch: {relative}")
print(text, end="")
PY
```
