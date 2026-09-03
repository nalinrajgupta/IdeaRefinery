# Data Model: First-Class GitHub Copilot Setup Documentation

This feature does not introduce persisted application data. The following conceptual entities define the documentation and validation contracts.

## Skill Distribution

- **Name**: `idea-refinery-full` or `idea-refinery-implement`
- **Canonical source**: repository skill directory
- **Generated source**: matching directory under `.agents/skills`
- **Personal target**: matching directory under the user's Copilot skill root
- **Validation state**: missing, valid, stale, staged, installed

### Validation rules

- Both generated sources must exist before personal replacement begins.
- An installed tree must exactly match its generated source after install or update.
- Operations may affect only the two named Idea Refinery targets.

### State transitions

```text
missing/stale
  -> source-preflight
  -> staged
  -> staged-verified
  -> installed

source-preflight failure -> original installation unchanged
staging failure          -> original installation unchanged
remove installed/missing -> missing
```

## Documentation Route

- **Host**: Codex, GitHub Copilot, or Hermes
- **Audience goal**: quick start, full setup, compatibility details, or troubleshooting
- **Shell label**: PowerShell, POSIX shell, or host command
- **Required facts**: install location, invocation, refresh behavior, authority boundary, Spec Kit preservation

### Validation rules

- Copilot commands must use slash invocation.
- Shell-specific commands must be labeled.
- Detailed content has one owning document and may be linked, not contradicted, elsewhere.

## Prerequisite Script Candidate

- **Family**: Bash or PowerShell
- **Expected path**: platform-specific Spec Kit prerequisite path
- **Executable by host**: yes or no
- **Invocation semantics**: JSON output, tasks required, tasks included
- **Selection result**: selected, skipped, or unavailable

### Selection rules

- Select exactly one executable candidate.
- Prefer the host-native candidate when both are available.
- Preserve equivalent prerequisite flags across candidates.
- Stop with an actionable error when no candidate is executable.

## Validation Requirement

- **Requirement ID**: FR-001 through FR-022 or SC-001 through SC-008
- **Validation mode**: automated or manual
- **Artifact under test**: documentation, canonical skill, generated skill, workflow, or command walkthrough
- **Expected evidence**: assertion result, sync result, command output, elapsed discovery time, or reviewer sign-off

