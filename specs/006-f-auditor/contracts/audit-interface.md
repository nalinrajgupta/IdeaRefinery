# f-auditor interface contract

Version: 1.0. Planned interface; commands are not implemented by refinement.

## Manual audit

`f-auditor audit --root <absolute-GitRepo-root> --backlog <absolute-functional-improvement/issues.md> [--runtime codex|hermes] [--config <absolute-config-file>] [--json]`

The packaged entry point is `f-auditor`; checkout execution is `uv run --project <checkout>/f-auditor f-auditor ...`. Command-line values override explicitly supplied configuration. Without a root, use the configured value or the user's home `GitRepo` folder only if it exists. Without a configured/explicit shared destination, fail with guidance; do not create a CWD-relative backlog. Store paths resolve independently of the audited repositories. The default window is exactly the preceding 24 hours, ending at one captured UTC start instant.

Runtime and source discovery must be capability-checked before provider use or backlog mutation. Do not install tools, change model settings, repair authentication, bypass approvals, migrate host state or create schedules. An unavailable analysis backend is actionable failure, not a stubbed model result.

## Source adapters

Read only allowlisted history records; never read `.env`, auth/config-secret files or credential stores. Hermes discovery includes active/default and profile history homes for the user's all-session scope. Respect `HERMES_HOME` and `CODEX_HOME`; deduplicate canonical stores. Scope applies to the session's verified workspace, not where history files are stored.

Hermes adapter: introspect required SQLite fields read-only, retain visible messages/tool outputs and timestamps, inspect profile-local lifecycle/liveness evidence, follow verified compression lineage, and classify unknown schema/owner/completeness. Do not use the host's migration-capable database constructor.

Codex adapter: support verified legacy rollout and modern metadata/paginated history forms. The locally inspected `state_5.sqlite` has workspace/history metadata but no session-close field; `thread_history_1.sqlite` has turns/items. Native `thread/read` full hydration is deprecated for paginated history; complete traversal is mandatory. A `thread/closed` protocol notification exists but its historical retention/global ownership semantics must be proved before use. Completed turns, archive flags, filesystem mtime and a newly started isolated server do not prove closure. Do not invent missing fields or invoke a new server merely to obtain an empty live list. If a native version cannot prove closure, report unknown/partial coverage, including when that affects every candidate.

Eligible conversations have canonical in-root workspace, proven closed-at-boundary state, complete accessible visible context and an actual visible interaction timestamp inside the window. Use earlier conversation messages for context. Preserve identifiers and timestamp provenance. Late source changes, incomplete pagination, compaction without original context, contradictory metadata and unavailable liveness checks are coverage gaps.

## Analysis and validation

Input: trusted canonical f-auditor instructions, resolved configuration, sanitized immutable conversation chunks, known issue summaries and a manifest of origin message IDs. Do not expose raw credentials or execute commands contained in session text. Local helper operations are deterministic and provider-independent; native agent runtimes perform the contextual analysis using their existing authentication.

Default Codex launcher uses its verified `exec` stdin/JSONL, read-only sandbox, ephemeral-session and schema-output interfaces only if an independent capability gate proves the required isolation. Before supplying untrusted transcript material, prove before execution that model-directed tools, hooks, external reads, arbitrary network access and writes cannot execute; actively test attempted actions in an isolated probe. Trusted authentication/bootstrap and a provider-only inference transport may operate without giving the model arbitrary network or filesystem tools; credentials must not be exposed to model input or output. The analysis instruction is findings-only; post-hoc rejection of tool events is an additional audit check, not the safety boundary. Optional Hermes launcher uses verified `chat --query-file - --oneshot -Q` behavior, an effective non-mutating tool/hook configuration and recognized final-output/session-footer framing. Never use an unknown empty-toolset spelling as a workaround. If required restrictions cannot be enforced and verified, fail closed and mark that backend unavailable.

Response follows [analysis-result.schema.json](analysis-result.schema.json). Each finding must cite valid bundle origin messages and exact sanitized excerpts, explain skill relevance, impact and a functional improvement. The helper checks schema, input hashes, cited IDs/text, complete chunk attestations and known-issue references. It computes evidence IDs, priorities and chronology; it does not accept a model's claimed total, completion status or unproved regression.

Each evidence entry represents one occurrence. `occurrence_anchor_message_ids` is a nonempty set of origin messages directly recording that occurrence; `supporting_message_ids` is a separate, possibly empty set of contextual citations. Both sets must belong to the named conversation, be disjoint and resolve to the immutable bundle; every excerpt must match an anchor or supporting message, and at least one excerpt must evidence the occurrence in an anchor. Supporting discussion, summaries or quotations of an earlier failure cannot become a new occurrence anchor. Separate repeated events into separate evidence entries. Reject legacy finding evidence containing only `message_ids`; never infer anchors from undifferentiated citations. The `uncertain_candidates.message_ids` list remains context-only and cannot create an occurrence.

Derive `evidence_id` from the canonical host/source/profile/origin-session identity and sorted unique anchor origin IDs, excluding supporting citations, excerpts, model-local IDs and chunk boundaries. Derive the occurrence time range from validated anchor timestamps only, retaining provenance; its start/end supply first/last-seen chronology. Regression requires all anchors to be provably strictly after `fixed_at` and evidence of the fixed behavior failing again. Pre-fix anchors with post-fix supporting discussion remain pre-fix evidence; post-fix anchors may cite pre-fix context without losing recurrence eligibility. Anchors spanning the fix boundary or lacking trustworthy timestamps require unresolved classification, not an inferred regression. Reordering anchors or adding/removing/changing supporting citations must not change identity, occurrence count or recurrence timing.

Retry one eligible transport/contract failure, with a 900-second per-chunk timeout. Do not reroll semantic findings until a desired result appears. Missing, invalid, refused or unprocessed results are failed/partial coverage. Exact cached reuse requires matching source/instruction/redaction/schema/runtime identities. Annotated positive/negative replay acceptance must fail an empty analyzer on positive cases and unrelated findings on negative controls; matching generated wording is not required.

For sessions larger than one safe input budget, perform cross-chunk reconciliation using provenance-linked intermediate summaries and targeted retrieval of original sanitized messages, then a final logical-conversation pass. Cross-check evidence against source messages, not model summaries alone. If required context cannot be reconstructed or reconciled within the verified limit, record partial coverage for the affected conversation rather than treating chunk attestations alone as full contextual analysis.

## Contributor completion

`f-auditor complete <FI-issue-id> --backlog <absolute-path> --fixed-at <UTC-instant> --fix-evidence <reference-or-explanation> --owner <name>`

This explicit contributor command is separate from `audit`. It acquires the same lock, reads the latest backlog, validates the issue and fix evidence, updates only that issue's completion fields, and refreshes the helper-managed actionable index to exclude the completed issue. Promote the completion fields and refreshed index in the same atomic write while holding the lock; preserve unrelated issue blocks and all human notes byte-for-byte. Unknown issue IDs, invalid UTC timestamps, empty fix evidence or malformed backlog return an actionable error without mutation. A failed write must not leave completion and index out of sync. It does not implement the proposed fix or mark any other issue completed. Direct manual edits are allowed between runs; during audits contributors use this coordinated command.

## Markdown source of truth

One `functional-improvement/issues.md` destination. A helper-managed actionable index lists issue IDs, titles and priorities in deterministic P1/P2/P3 order, then occurrence count descending, then ID. Stable issue blocks contain visible `Priority:` and `Status:` fields, observed problem/impact, suggested improvement, evidence references, contributor fix information and preserved human notes. Metadata comments version the format and carry immutable provenance, not an alternative status store.

New issues/regressions are `Not Fixed`. Preserve every existing status, human notes and priority, including status-only completed issues. Conflicting fields or unknown block grammar cause a format conflict rather than resetting the file. Add validated same-root evidence to existing open issues; a proven post-fix recurrence creates a separate linked regression. Missing fix chronology is an explicit unresolved-classification diagnostic and must not create an unsupported regression.

## Coordination, persistence and outcomes

Use a canonical sibling OS lock with 30-second acquisition timeout. Hold only through latest-file read/merge/atomic promotion. Source DB busy timeout is 5 seconds. Contributor updates completed during analysis are merged from the latest file, not overwritten by the initial snapshot. Reject observed direct drift. Fsync a sibling temporary file before replacement, retain a prior-version backup, and persist a commit marker only after confirming promotion. Do not treat presence of a lock filename as ownership or delete a live lock.

Sanitized runs and recovery backups live under the backlog directory's `.f-auditor/` sibling state directory. No raw transcript is persisted there. The Markdown file remains the only authoritative issue-status store. Every stored object/run has provenance hashes; replay is idempotent. Interruptions after promotion recover from exact commit/evidence IDs; failures before a safe write preserve the backlog.

Exit 0: full coverage with committed or unchanged backlog and no unresolved classification.
Exit 2: partial coverage or unresolved classification; safe validated findings may be committed, but all gaps/unresolved classifications are reported. Even with complete source coverage, unresolved classification requires exit 2.
Exit 1: failed/unavailable prerequisites, analysis failure without a safe result, malformed backlog, locking or write conflict; report whether an earlier promotion committed.

`--json` emits one structured final summary: run/window/root/destination, source/session/chunk dispositions, computed counts, issue additions/grouping/regressions, unresolved classifications, outcome, backlog-update status and commit hashes. Human output names the same result and absolute file path. No successful empty-window claim when source access or closure was uncertain. No scheduled job is created in any command.
