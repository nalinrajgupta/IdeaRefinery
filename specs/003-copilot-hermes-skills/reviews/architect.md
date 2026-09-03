# Architect review: Cross-Host Idea Refinery Skills

ID: R-005
Reviewer: Architect
Severity: critical
Artifact / section: Spec v1, FR-002, FR-007, FR-008
Evidence: Full workflow instructions are large and safety-sensitive. Independently edited copies in host directories will drift, silently producing inconsistent behavior.
Why it matters: A portability change that fragments the workflow defeats the explicit requirement for the same full skills.
Smallest proposed change: Define canonical skill bodies, deterministic generation of host distributions, and a parity test that rejects stale or missing generated entries and reference paths.
Human decision required: no
Resolution: accepted

ID: R-006
Reviewer: Architect
Severity: high
Artifact / section: Spec v1, FR-003 and FR-005
Evidence: Copilot and Hermes may differ in subagent, isolation, and named-skill support. The existing text says fallback but does not specify an enforceable selection order.
Why it matters: An agent could run unsafe parallel edits or falsely imply an unavailable review occurred.
Smallest proposed change: Add a host-neutral capability contract: inspect first; use native capability when it satisfies the gate; otherwise use controller-applied patches or sequential execution; record fallback; block if no equivalent evidence can be produced.
Human decision required: no
Resolution: accepted

ID: R-007
Reviewer: Architect
Severity: medium
Artifact / section: Spec v1, FR-006 and FR-009
Evidence: Spec Kit's current project metadata is Codex-specific, while target repositories can use a different integration.
Why it matters: A host conversion could overwrite an existing target integration or create incompatible commands.
Smallest proposed change: Require detection and preservation of an existing integration; document Copilot initialization separately and Hermes's generic integration command directory as a fallback.
Human decision required: no
Resolution: accepted
