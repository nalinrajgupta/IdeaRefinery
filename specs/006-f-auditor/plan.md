# Implementation Plan: f-auditor

**Branch**: `features/func-audit` (unchanged) | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Input**: Clarified Spec v2 and decisions D-001–D-012.

Repository-local Spec Kit planning output. Source paths below are planned, not implemented by refinement.

## Summary

Add a canonical `f-auditor/` skill with a deterministic Python helper and explicit manual audit command. Read Hermes and Codex histories without mutating them; select whole, provably closed conversations active in a fixed 24-hour window under the configured GitRepo root. Sanitize their contextual evidence and have an agent apply the skill's bounded analysis instructions. The helper validates analysis and alone updates one configured shared Markdown backlog. Contributor completion uses the same coordination protocol during audits; direct manual editing is supported between runs.

Unknown closure/history is explicit partial coverage, not assumed eligibility. No scheduler, automatic fix, provider SDK, credential-store access or audit-driven completion marking.

## Technical Context

**Language/Version**: Python 3.11+, matching the existing deterministic runtime.

**Primary Dependencies**: Standard library (`sqlite3`, `pathlib`, `datetime`, `json`, `hashlib`, `subprocess`, POSIX `fcntl`), jsonschema and PyYAML using the existing runtime's ranges. No provider SDK. Native host CLIs own model execution/authentication; the helper never reads credentials.

**Storage**: Read-only host SQLite/JSONL or verified exports; one Markdown backlog; sanitized immutable bundles/manifests under its sibling `.f-auditor/` directory. Only Markdown owns issue status and fix evidence.

**Testing**: pytest unit/contract/integration suites, annotated analysis replay cases, native compatibility probes and actual manual-command smoke validation. Credential-free CI is separate from live quality measurements.

**Target Platform**: Initial macOS/POSIX trial. Unsupported platform locking or runtime capabilities fail explicitly; Windows audit support is deferred.

**Project Type**: Agent skill plus CLI/library helper; portable skill distribution uses the existing sync mechanism.

**Performance Goals**: Stream source records; chunk analyzer input using measured context budget with prompt/response reserve. Account for every eligible message, never silently truncate. Measure manual latency rather than invent a service-level target. Runtime timeout: 900 seconds per chunk with one transport/contract retry, not repeated semantic rerolls.

**Constraints**: One UTC audit-start boundary. Source database URI `mode=ro`, `PRAGMA query_only=ON`, bounded busy timeout; no migration/import/repair constructors. Hash-based exact replay. Reject unknown schemas, unavailable authority, invalid evidence or file drift. No global configuration or automatic auth/dependency repair.

**Scale/Scope**: One local maintainer, all in-scope repositories/folders and matching histories across configured Hermes homes/profiles and Codex home. Entirely uncertain sources still appear in partial coverage even when no sessions can be selected.

## Constitution Check

The constitution is an unratified placeholder containing example comments, not adopted principles. Preserve it; do not pretend its examples are ratified. Apply actual repository authority and D-001–D-012: refinement writes feature artifacts only; application implementation remains separate; no commits, pushes or schedules. Pre-design and post-design checks pass with these boundaries. D-011 waives reviewer model/effort verification, not requirement coverage, independence or data safety.

## Project Structure

### Documentation (this feature)

```text
specs/006-f-auditor/
├── spec.md
├── design.md
├── refinery-state.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
├── reviews/
├── runs/
└── tasks.md
```

### Source Code (repository root)

```text
f-auditor/
├── SKILL.md
├── pyproject.toml
├── uv.lock
├── references/audit-contract.md
├── schemas/analysis-result.schema.json
├── src/f_auditor/
│   ├── cli.py
│   ├── config.py
│   ├── sources.py
│   ├── selection.py
│   ├── evidence.py
│   ├── analysis.py
│   ├── backlog.py
│   └── run_store.py
└── tests/{unit,contract,integration,fixtures}/
.agents/skills/f-auditor/           # generated
tools/sync_host_skills.py          # extend existing tables
functional-improvement/issues.md  # configured destination; created by audit
```

**Structure Decision**: Keep auditor behavior separate from both evaluated skills. Extend `tools/sync_host_skills.py` canonical lists/runtime assets and its tests rather than duplicating distribution logic. The backlog destination is configured absolutely, never relative to an audited repository's CWD. No source implementation or actual backlog issues are created by this refinement.

## Architecture and processing

```text
audit -> config + fixed window -> read-only source inventory
  -> metadata/liveness selection
     -> open/outside/stale: disposition
     -> unknown/corrupt/incomplete: coverage gap
     -> eligible whole history -> sanitize -> immutable chunks
        -> skill-guided analysis -> schema/evidence/coverage checks
        -> root grouping + priority + regression classification
        -> lock -> latest backlog -> merge -> atomic promotion -> report

contributor complete -> same lock -> latest backlog -> status + fix evidence
```

Source selection, runtime, output and contributor interfaces are fixed in [the audit interface contract](contracts/audit-interface.md); entity rules are in [data-model.md](data-model.md). These contracts, not guesses about undocumented fields, govern implementation.

Hermes reads profile-local state metadata, messages and liveness leases; follow verified compression continuations, not independent forks/subagents. Codex supports legacy rollout and discovered modern/paginated formats. The inspected Codex metadata has no session-closed column. A completed turn, archive flag, file mtime or a newly started private server's empty runtime list is never proof of closure. Native adapter probes must establish lifecycle plus current-owner evidence or explicitly classify unknown. Source version limitations are user-visible, including an entirely unsupported/uncertain source. Actual full-support claims require observed compatibility evidence for both hosts.

Normalize visible user/assistant/tool history with origin message IDs; omit credentials/system configuration/reasoning sidecars, not relevant user context. Preserve source completeness and activity timestamps. Eligibility requires reliable canonical workspace containment, proven closure at audit start and visible activity in the captured window. Historical context outside the window remains available for interpretation; only a post-fix occurrence can support regression.

The helper embeds trusted skill instructions and sanitized bundles in the native analysis invocation. Default shell-backed execution uses Codex's documented `exec --sandbox read-only --ephemeral --output-schema` and stdin/JSONL interface only after an independently verified pre-execution isolation gate; the sandbox flags alone are not proof. Optional Hermes execution uses documented `chat --query-file - --oneshot -Q` only after the same gate; the observed text-only `bot_room` configuration is a capability candidate, not an assumed guarantee. Before untrusted content reaches the runtime, demonstrate that model-directed tools, hooks, external reads, arbitrary network access and writes are blocked, and fail closed if the boundary cannot be established. Trusted host authentication/bootstrap and the host's provider-only inference transport remain available but are not model-directed tools, and credentials are not exposed to analysis. Host CLIs own authentication; helper/schema/replay code is provider-independent.

Every supplied chunk needs analysis coverage and every finding needs valid origin citations. Preserve cross-chunk context with provenance-linked intermediate summaries, targeted retrieval of original sanitized messages, and a final reconciliation pass across each logical conversation; validate cited origins against the source bundle, not summaries alone. If context cannot be preserved or reconciled within verified limits, mark that conversation's analysis partial, not complete. Bound context by a supported budget and reserve; unknown budget/runtime capability is an actionable prerequisite. Exhausted retries, refusal, malformed output or unprocessed chunks remain failed/partial, not a successful empty analysis.

## Persistence, priorities and collaboration

One configured Markdown file contains a helper-managed actionable priority index, stable `FI-` issue blocks with parseable metadata comments, and preserved human notes. Metadata is not a second status store. Require explicit `--backlog` or config destination; relative config paths resolve against the config file, never CWD. Keep issue IDs stable, deduplicate evidence by verified origin IDs, and validate analyzer grouping rationale. Uncertain root similarity cannot silently merge issues.

Rubric: P1 blocks/invalidates successful or safe skill use; P2 repeated corrections/setup or workaround-dependent completion; P3 lower-impact functional ergonomics. Actionable order is P1→P2→P3, confirmed occurrence count descending, then stable ID. Preserve human priority overrides. Audit-created statuses are `Not Fixed`; only explicit contributor completion sets `Completed` with UTC fix time and fix evidence. Status-only legacy completion remains completed and yields an unresolved-classification diagnostic if recurrence timing cannot be established. A proved recurrence creates one separate open regression; later occurrences group there without reopening its completed predecessor.

Lock the canonical destination's sibling lock file only for latest-file read/merge/promotion, not during analysis. All helper writers cooperate. Contributor updates during analysis are merged from the latest file under lock. Compare bytes before promotion, fsync a sibling temporary file and atomically replace. Persist a prior-version backup and mark the run committed only after confirming promotion. Replaying committed evidence cannot duplicate issues. Unknown/malformed backlog or observed direct drift causes conflict without overwrite; never discard a live OS lock because its filename exists. Direct manual edits are supported between runs per D-012; arbitrary concurrent editors bypassing coordination have no lost-update guarantee.

## Errors, tests and delivery

| Failure | User-visible behavior | Required test |
| --- | --- | --- |
| Missing source/schema/closure or liveness uncertainty | Partial with named gaps; no inferred eligibility | Host compatibility, open/unknown, corruption fixtures |
| Complete empty window | Full zero findings; preserve backlog | Empty-window integration |
| Every candidate uncertain | Partial zero findings; explicit gaps | Unknown-source integration |
| Incomplete paging/chunks | Partial; enumerate unprocessed coverage | Pagination and large-session fixtures |
| Invalid/refused/empty contract result | One eligible retry then failed/partial; no unchecked write | Contract/evidence/runtime failures |
| Empty analysis on positive cases or unrelated controls reported | Acceptance fails | Annotated positive/negative replay |
| Secrets/instruction-like transcript | Sanitize before model or persistence; no directed tools | Redaction and injection cases |
| Missing fix chronology | Preserve completed status; unresolved classification | Status-only, pre/post-fix cases |
| Lock/conflict/write interruption | No overwrite; explicit recovery | Multi-process and fault-injection cases |
| Missing runtime/auth/platform | Actionable prerequisite; no auto-repair | Manual invocation failures |

Tests precede behavior implementation. Schema/semantic contracts, deterministic tests, annotated approved replay fixtures and requirement-to-task traceability are blocking. Separate from deterministic cached replay, a real analyzer must process reviewed annotated positive and negative cases through the actual launcher, with recorded input/output provenance and no canned responses; unavailable live execution leaves behavioral acceptance unverified. Native manual smoke checks are also required completion evidence; a mock cannot establish live acceptance. Model-judge scores and trend benchmarks remain non-blocking unless separately calibrated.

Ship canonical skill/helper, generated distribution, usage/contribution/setup docs and CI/distribution checks. The first manual run reports native source and closure coverage so the user can assess confidence. Rollback disables invocation and restores a known backup under coordination and explicit operator authority; never rewrite host histories. Scheduling, Windows auditing, automatic fixes, public publishing and remote histories remain deferred.

Shared configuration/models/evidence contracts precede adapter and backlog lanes. Hermes and Codex adapter test/fixture work can run independently after contracts freeze; adapter implementations serialize because both write `sources.py`. Parser/coordination precedes completion and audit merge; analysis precedes behavioral replay; distribution/docs and native smoke follow integrated validation. Packaging, schema, lockfile and sync-script edits are exclusive write sets.
