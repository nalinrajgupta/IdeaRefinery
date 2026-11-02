# f-auditor data model

Status: Planned contract, not implemented application code.

## Audit configuration

`root`: canonical absolute audit scope; initial setup uses `/Users/nalin-ai/GitRepo`.
`backlog`: one explicit canonical absolute Markdown destination inside a `functional-improvement` directory. Relative values in an explicitly supplied config resolve against that config file, never invocation CWD.
`hermes_homes`, `codex_home`: allowlisted history roots, resolving host home overrides and default/profile homes without opening credential or configuration-secret files. Duplicate canonical stores collapse to one source.
`runtime`: `codex` by default, or `hermes` after its non-mutating capability gate passes.
`runtime_context_limit`: verified supported input capacity or explicit configured safe bound; unknown capacity blocks analysis rather than truncate.
`runtime_timeout_seconds`: 900; `runtime_retry_limit`: 1 for retryable transport/contract failure; `lock_timeout_seconds`: 30; `source_busy_timeout_seconds`: 5.

The helper records the resolved values and instruction/redaction/schema/runtime hashes before analysis. It never changes host credentials or settings.

## Audit run

- `run_id`: unique stable run identifier; reused only for exact resume.
- `started_at`, `window_start`, `window_end`: UTC instants; window end is captured once at run start.
- `config_hash`, `instruction_hash`, `redaction_hash`, `schema_hash`, `runtime_hash`: replay identity.
- `source_inventory`: one record per canonical source with adapter/version/capability evidence and `complete`, `partial`, or `unavailable` disposition.
- `session_dispositions`: stable origin key, `eligible`, `open`, `outside-root`, `outside-window`, `unknown-closure`, `unknown-scope`, `incomplete-history`, or `read-failed`, plus reason/evidence.
- `chunk_manifest`: all expected immutable chunk IDs, origin-message membership, hashes and analysis outcomes.
- `findings`, `unresolved_classifications`, `backlog_before_hash`, `backlog_after_hash`, `commit_marker`.
- `outcome`: `full`, `partial`, or `failed`; `backlog_update`: `committed`, `unchanged`, `conflict`, or `not-attempted`.

Transition: discovered -> collected -> analyzed -> validated -> merged/unchanged -> reported. A failed collection or analysis cannot become a full result. A committed merge remains committed even if subsequent report delivery fails; replay uses its commit marker and evidence identity.

Counts come from the recorded dispositions, never from model declarations. Ineligible sessions are not coverage gaps; uncertain/inaccessible expected sources or unprocessed eligible context are gaps. All sources uncertain still means partial, not a successful empty window.

## Logical conversation and message

Conversation key contains host, canonical source/profile identity and verified origin session/thread ID. Compression continuations may belong to one logical conversation; independent forks or delegated children do not collapse merely because they share a parent. Preserve origin provenance across imports when available; uncertain duplicates remain labeled rather than merged by transcript similarity alone.

Conversation fields: workspace metadata/provenance, origin IDs, visible interaction times, lifecycle end evidence, current-owner/liveness evidence, closure state (`closed`, `open`, `unknown`), completeness evidence and messages.

`closed` requires compatible host lifecycle termination and an authoritative current-owner check. An idle surface, archived flag, completed turn, absent recent writes, or an empty private server inventory is not closure proof. Unknown capability is explicit. Host schemas lacking the needed evidence are not silently upgraded.

Message fields: origin ID, role (`user`, `assistant`, `tool`), UTC timestamp with provenance, sanitized visible content, tool-call/result linkage, and source locator. The complete visible history through the captured run boundary is analyzed, including context before the 24-hour window. System credentials, hidden reasoning and credential-store records are not copied. Missing original context is a completeness gap, not a fabricated reconstruction.

## Evidence occurrence

Fields: stable `evidence_id`, host/source/profile/session identity, nonempty `occurrence_anchor_message_ids`, separate `supporting_message_ids`, occurrence start/end timestamps with provenance, sanitized excerpts, observed behavior, expected behavior, affected skill and skill-relevance explanation. Each entry describes one event; anchors directly record it, while supporting citations provide context and may be empty.

The deterministic validator verifies both disjoint ID sets and excerpts against the named conversation in the immutable bundle, including at least one occurrence-bearing anchor excerpt. It rejects unsupported quotes, timestamp fabrication, outside-bundle citations and transcript instructions masquerading as authorization. Hash canonical host/source/profile/origin-session identity plus sorted unique anchor origin IDs for `evidence_id`; only anchor timestamp minima/maxima determine occurrence start/end. Supporting citations and their timestamps, excerpt wording, chunk boundaries and model-local IDs never affect identity or chronology. Actual repeated occurrences have separate entries; rereading/importing the same origin occurrence, reordering anchors or changing supporting citations is not a new event. Finding evidence without explicit anchors is rejected rather than migrated by guessing.

## Improvement issue

- `issue_id`: `FI-` plus stable unique suffix; never renumber existing IDs.
- `title`, `affected_skill`: `refine-idea`, `implement-refine-idea`, or `both`, with setup issues attributed to their affected workflow.
- `problem`, `impact`, `suggested_improvement`, `grouping_rationale`.
- `priority`: P1/P2/P3; `priority_rationale`; optional human override. Existing priorities are preserved unless a contributor explicitly changes them; new analysis may suggest a revision without applying it.
- `status`: new issues always `Not Fixed`; explicit contributor completion uses `Completed`. Preserve legacy/manual completed markings and unsupported custom status text rather than reset it; conflicting parseable status fields are a format conflict.
- `evidence`: individually traceable occurrences.
- `first_seen`, `last_seen`: derived only from confirmed occurrences.
- `fixed_at`, `fix_evidence`, `fixed_by`: contributor-owned completion information, optional for legacy manual completion but required for new completion-command use.
- `regression_of`: optional completed predecessor ID.
- `human_notes`: retained bytes outside intentionally patched helper fields.

The Markdown block's visible `Status:` and `Priority:` fields are authoritative. Metadata comments contain version/identity/provenance, not competing status copies. Immutable run snapshots and backups are evidence/recovery artifacts, not an alternate issue database.

## Grouping and regression rules

Validated same-root findings merge into an existing actionable issue; unsupported similarity is reported for review, not silently consolidated. Priority index orders actionable issues P1/P2/P3, then confirmed occurrence count descending, then stable ID. Completed issues remain retained but outside that index.

If a completed root recurs, require every validated occurrence anchor to be strictly after the contributor's fix time plus evidence explaining what fixed behavior failed again. Pre-fix failure anchors with post-fix discussion remain pre-fix evidence; post-fix failure anchors with pre-fix supporting context may establish regression. Old contextual messages alone cannot trigger regression. Anchors spanning the fix boundary, untrustworthy anchor timestamps or missing/ambiguous fix evidence preserve completion and produce an unresolved-classification diagnostic. A proven recurrence creates a separate Not Fixed regression linked to the predecessor; additional occurrences merge into the open regression. Re-auditing the same post-fix anchors with different supporting citations does not create another occurrence or regression.

## Shared-file mutation

Audit merge and contributor completion share the canonical sibling lock. Read the latest Markdown inside that lock, preserve human-owned content, check unexpected byte drift, write/fsync a sibling temporary file and atomically promote. Preserve a prior-version backup and exact commit evidence. The lock is held during mutation, not model analysis; contributor changes during analysis are incorporated from the latest file.

Contributor completion patches the selected issue's completion fields and refreshes the managed actionable index in that same locked atomic promotion. A completed issue is absent from the index immediately, without waiting for an audit; unrelated issue blocks and all human notes retain their bytes. Failure before promotion preserves both old status and old index.

Direct edits are supported between runs per D-012. Uncoordinated concurrent editors are not a supported safe-write mode; observed drift aborts rather than overwrites. Failure or no findings preserves the existing issue blocks. Malformed or unknown Markdown structure is a conflict, never a reason to rebuild or reset the file.
