# Host compatibility research

Date: 2026-11-01. Planning research and controller-owned technical choices; not a claim of completed implementation or native audit acceptance.

## Verified local interfaces

- `hermes --version`: Hermes Agent v0.21.0; local installation at `/Users/nalin-ai/.hermes/hermes-agent`.
- `codex --version`: codex-cli 0.166.0.
- `hermes sessions --help`: local history listing/export supported.
- Hermes `website/docs/developer-guide/session-storage.md:43–119` documents SQLite sessions with `started_at`, `ended_at`, `end_reason`, workspace metadata, and timestamped messages. `hermes_cli/active_sessions.py:1–5,204–213` separately tracks currently open surfaces, including idle CLI/TUI sessions, in an active-session lease registry. Ended-row metadata alone is not proof that a resumed lineage has no live surface.
- Hermes `hermes_cli/foreign_sessions.py:16–23,235–267` describes Codex rollout `session_meta` and `response_item` records. Its import adapter discards tool outputs and skips malformed lines, so it is not sufficient by itself for an auditor that must expose incomplete evidence and diagnose setup failures.
- The installed Codex CLI successfully generated its protocol schema using `codex app-server generate-json-schema --out /tmp/f-auditor-codex-schema-20261101`.
- Generated `v2/ThreadClosedNotification.json` describes a `threadId` close notification. The existence of a protocol notification does not prove it is retained in historical rollouts or globally represents all clients.
- Generated `v2/ThreadAttachmentOwnerListResponse.json:7–9` explicitly says archived status is not whether a thread is currently executing a turn. Archive status must not be substituted for closure.
- Generated `v2/ThreadListResponse.json` has a `notLoaded` status; its precise relationship to idle/open clients and older no-daemon instances still needs version-specific adapter validation.
- Read-only schema introspection confirmed local Codex `state_5.sqlite` thread metadata (`cwd`, `history_mode`, `archived`, activity/recency fields), plus `thread_history_1.sqlite` turns/items. There is no inspected session-closed column. No transcript contents or credentials were read for this introspection.
- Generated `v2/ThreadReadParams.json` says full-history hydration is deprecated for paginated threads and recommends `thread/turns/list` and `thread/items/list`. A rollout-only/import-summary reader cannot claim complete modern history coverage.
- Hermes native CLI supports non-interactive `chat --query-file - --oneshot -Q`; quiet output still includes session information. Codex `exec` supports stdin, JSONL events, `--sandbox read-only`, `--ephemeral` and `--output-schema`. These are launcher interfaces, not evidence that live analysis has run.
- Hermes `toolsets.py` declares `bot_room` text-only, and agent initialization gates context-engine tool injection on enabled toolsets. Actual runtime/plugin/hook restrictions must still be capability-checked before enabling a backend; no unknown toolset spelling or approval bypass is acceptable.

## Planning implications

Use read-only adapters and native metadata where available. Capture one time boundary, inspect actual interaction timestamps instead of file modification time, and distinguish `closed`, `open`, and `unknown` with the evidence supporting each classification. Missing closure evidence is reported as a coverage gap, not inferred from silence, completion of a turn, archive status, or a lack of recent file writes.

A compatibility gate must establish at least one usable, verified closure path for each required host before implementation can claim functional acceptance. Unsupported historical formats must be identified explicitly. Do not solve this by silently redefining the user-approved closed-session criterion.

The Python support runtime has PyYAML/jsonschema dependencies. This session's system Python does not have PyYAML; `uv run --no-project --with PyYAML --with jsonschema` successfully supplied the existing dependencies without editing application manifests.

## Technical decisions

### Separate canonical skill/helper

Decision: Add `f-auditor/` and extend the existing generated skill distribution tables; do not modify either evaluated skill for auditor behavior.
Rationale: Existing sync logic already distributes instruction/reference/runtime assets and checks consistency.
Alternatives: embedding auditing in refinement/implementation couples execution authority to observation; separate provider SDK configuration duplicates host capabilities.

### Conservative source closure and completeness

Decision: Select only proven closed whole conversations. Every missing lifecycle/liveness/completeness capability is explicit unknown/partial coverage, not inferred from inactivity, archive status or completed turns.
Rationale: Native schemas distinguish thread/runtime/session concepts; silently assuming closure creates false coverage.
Alternatives: mtime thresholds and private-server empty lists rejected. Native acceptance must record actual observed proof paths or report affected host versions as unsupported/partial. This compatibility work is required implementation evidence, not a material scope decision left to the implementer.

### One Markdown authority

Decision: Resolve an explicit shared destination independently of CWD. Visible status/priority fields in stable Markdown issue blocks are authoritative; managed index and metadata preserve notes and provenance. Snapshots/backups are not a second status store.
Rationale: Contributors need one file that survives repeat runs, imports and multiple projects.
Alternatives: a per-run report loses shared lifecycle; a hidden database with a regenerated display can erase manual edits.

### Coordinated contribution

Decision: D-012 requires helper-coordinated status/fix-evidence updates during audits; manual edits are supported between runs. Lock only latest-file merge/promotion, use atomic replacement and exact drift checks; no guarantee for arbitrary editors bypassing the lock.
Rationale: Hash-before-rename alone cannot provide atomic compare-and-swap with uncoordinated writers.
Alternatives: unrestricted concurrent manual editing was not selected by the user.

### Behavioral acceptance and model boundary

Decision: Blocking annotated positive/negative replay cases verify root-problem recovery, exclusions and origin evidence. Native runtime execution is separately exercised and honestly reported. Model-judge trend scores remain non-blocking.
Rationale: All reviewers identified the empty-analyzer acceptance gap. Deterministic mechanics must not require provider credentials, and fixture responses cannot substitute for live execution.
Alternatives: exact generated wording is brittle; structural JSON checks alone are vacuous on no findings; uncalibrated scores are not a quality gate.

### Implementation lanes

Decision: Independent adapter test/fixture files may run in parallel after shared contracts freeze; adapter implementations serialize because both write `sources.py`. Packaging/schema/lockfile/sync changes are exclusive.
Rationale: Existing implementation workflow treats disjoint write sets, not a [P] marker alone, as the concurrency gate.
