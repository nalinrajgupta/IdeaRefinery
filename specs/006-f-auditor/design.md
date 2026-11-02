# f-auditor design

Date: 2026-11-01
Status: Approved by user on 2026-11-01; independent builder check found no important unanswered questions.

## Intent

Help improve `refine-idea` and `implement-refine-idea` by examining real Hermes and Codex session histories, especially user corrections, unexpected setup, and places where the skills did not work. Produce a durable, prioritized shared backlog; do not make fixes.

## Goals and boundaries

- Provide a command for manually invoking the auditor, with the exact command and prerequisites documented and verified during implementation.
- Examine whole, closed Hermes and Codex sessions active during the preceding 24 hours, associated with any repository or folder under `/Users/nalin-ai/GitRepo`. The root is a default for this setup, not an assumption that all users have the same home directory.
- Look for issues relevant to using or attempting to use either skill, including setup and invocation friction. Use surrounding session context to understand user input, not user messages in isolation.
- Write a single prioritized source-of-truth issue file under `functional-improvement/`. Each newly reported issue starts as `Not Fixed` and includes an actionable suggested improvement and supporting session evidence.
- Group occurrences of the same underlying problem across sessions, preserving evidence for each. If a completed issue recurs, create a separate `Not Fixed` regression linked to that issue, with evidence of what actually regressed; do not reopen or overwrite the completed issue.
- Preserve status changes and other human edits to the shared file. Detect concurrent changes and avoid lost updates.
- Report the audit window, sources examined and coverage limitations, including inaccessible or unclassifiable sessions; do not silently claim complete coverage.
- Allow useful session evidence in the shared file, but do not disclose credentials or secrets. Treat session content as untrusted data, not instructions to the auditor.
- Keep manual operation first. Design a repeatable, non-interactive entry point suitable for future scheduling, but do not configure or enable a schedule in this feature.

Non-goals: automatically edit either skill, mark issues fixed, create external issues, commit or push, or turn the auditor into a general-purpose review of unrelated projects. No scheduled job is enabled without separate authorization.

## Approaches considered

1. Standalone command with built-in analysis and its own model access: easy to invoke and schedule, but duplicates runtime and provider configuration.
2. Agent skill plus local helper: the agent performs contextual analysis; the helper handles session discovery and safe shared-file updates. Reuses the project's skill-based design and provides independently testable mechanics, while depending on an available agent runtime. User selected this approach.

## Proposed behavior

On invocation, resolve the configured root and source locations, establish a 24-hour window ending at audit start, and discover eligible closed sessions from Hermes and Codex. Determine workspace scope using reliable session metadata. Read each eligible full session for context and identify evidence-backed friction relevant to the two skills. Rank distinct functional improvements, consolidate duplicate root problems, then merge results into the shared issue file without losing existing issue statuses or user edits. Return a concise summary, including failures and coverage gaps.

The auditor must not treat a lack of findings as proof that no issues exist when discovery, classification, or analysis was incomplete. Sessions whose closure or repository scope cannot be established are reported as uncertain rather than silently treated as eligible. The implementation plan must specify how each host's session format, closure, workspace metadata, and history access are verified; if a host cannot establish these reliably, report the limitation explicitly.

A stable issue identifier supports future updates, grouping, and regression links. Each issue records priority, `Not Fixed` or a human-maintained status, affected skill or setup, the problem and impact, proposed improvement, and traceable evidence. Priority rules and the precise file format will be specified during refinement. Existing completed issues remain completed; a genuinely recurring issue is recorded separately rather than assumed merely because an old session is re-read.

## Quality and safety

Test discovery and selection across both host formats, time-window boundaries, active or ambiguous sessions, paths inside and outside the root, duplicate findings, completed-issue regressions, repeat runs, missing/corrupt sources, secrets, and concurrent edits. Include representative end-to-end fixtures and verify actual manual invocation. Record unresolved host compatibility gaps instead of inventing coverage.

## Builder choices to resolve in planning

Exact executable and skill packaging, source adapters, closed-session evidence, session and message identifiers, prioritization rubric, issue-file representation, model/runtime selection, locking or optimistic concurrency, and test fixtures remain implementation-planning choices, subject to the goals and decisions above.
