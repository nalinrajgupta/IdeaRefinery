# Quickstart: Validate First-Class GitHub Copilot Setup

## Requirement validation map

| Requirement | Automated evidence | Manual evidence |
| --- | --- | --- |
| FR-001, FR-002, FR-008, FR-018 | README content assertions | Three-minute Copilot discovery walkthrough |
| FR-003-FR-007, FR-015-FR-017 | Setup content and safety-marker assertions | PowerShell and POSIX temporary-target lifecycle walkthroughs |
| FR-009-FR-013 | Cross-document content and link assertions | Shell-label and configuration-preservation review |
| FR-014 | Focused documentation contract tests | None |
| FR-019, FR-020 | Canonical/generated skill contract assertions | Four-layout platform-preflight walkthrough |
| FR-021 | Workflow path-filter assertions | None |
| FR-022 | Traceability and required-marker assertions | Review of timed discovery, commands, and readability |
| SC-001, SC-003, SC-006 | README assertions | Three-minute Copilot discovery walkthrough |
| SC-002, SC-007 | Setup safety-marker assertions | Repeated lifecycle walkthrough |
| SC-004 | Cross-document assertions | Link, path, invocation, and shell-label review |
| SC-005 | Requirement-to-validation assertions | Evidence completeness review |
| SC-008 | Preflight contract assertions | Bash-only, PowerShell-only, both-present, and neither-present walkthrough |

## Prerequisites

- Repository checkout on the feature branch
- Python environment capable of running the existing pytest suite
- GitHub Copilot CLI for manual discovery and invocation checks
- PowerShell for the Windows walkthrough
- A POSIX-compatible shell for the portable walkthrough

## 1. Validate generated skill parity

```powershell
python tools\sync_host_skills.py --check
```

Expected: exit code 0 with no stale-distribution message.

## 2. Run focused contract tests

```powershell
uv run --project idea-refinery-full --extra dev python -m pytest tests\unit\test_host_skill_distribution.py
```

Expected: all distribution, documentation, platform-preflight, and workflow-filter assertions pass.

## 3. Review the Copilot documentation route

Starting at `README.md`, confirm in under three minutes that a new reader can identify:

- repository-local and personal installation choices;
- `/idea-refinery-full <idea>`;
- `/skills reload` or restart guidance;
- the four refinement artifacts and readiness verdict;
- `/idea-refinery-implement` as a separate authorization.

Then follow the link to one contiguous GitHub Copilot section in `setup.md`.

## 4. Walk through personal installation lifecycle

Use temporary personal-skill roots rather than the real user profile for validation.

For both the PowerShell and portable-shell procedures:

1. Install both skills from `.agents/skills`.
2. Verify exact source-to-target file parity.
3. Add a stale file to one target and run update.
4. Confirm the stale file is removed and no nested skill directory appears.
5. Remove one generated source and confirm update leaves both existing targets unchanged.
6. Restore the source and repeat update twice; confirm identical results.
7. Remove one target manually, then run documented removal; confirm both targets are absent without error.

## 5. Validate project-versus-personal troubleshooting

Create different marker revisions in a temporary repository-local skill and personal skill. Follow the documented Copilot skill-management steps after `/skills reload` and confirm the guide lets the reader identify the active copy and correct the stale source.

## 6. Validate platform-aware preflight

Create four temporary ready-feature layouts and follow the canonical implementation skill's entry-gate selection instructions:

- Bash-only script layout;
- PowerShell-only script layout;
- both layouts present;
- neither layout present.

For each layout, record the selected command or failure message in `refinery-state.md`. The Bash-only and PowerShell-only cases must select their available script with equivalent JSON/task semantics. The both-present case must select the host-native script. The missing-layout case must stop with both expected paths and must not continue to implementation.

Also confirm the generated implementation skill contains the same entry-gate instructions as the canonical source.

## 7. Validate workflow coverage

Confirm `.github/workflows/refinery-evals.yml` includes `README.md` and `setup.md` in both push and pull-request path filters.

## 8. Final checks

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; only feature-scoped files are changed.
