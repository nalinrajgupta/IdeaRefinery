# Implementation Plan: First-Class GitHub Copilot Setup Documentation

**Branch**: `005-copilot-setup-docs` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-copilot-setup-docs/spec.md`

## Summary

Make GitHub Copilot a first-class documented host by adding a concise README quick start and a complete setup lifecycle for repository-local and personal skills. Keep cross-host rationale centralized in `docs/host-compatibility.md`, add safe and repeatable Windows PowerShell plus portable shell commands, disclose Copilot's slash invocation alongside the current skill-description wording, and make implementation preflight select either Bash or PowerShell Spec Kit prerequisites. Extend distribution/documentation tests and workflow path filters so these contracts cannot silently regress.

## Technical Context

**Language/Version**: Markdown; Python 3.11+ for repository contract tests; YAML for workflow filters

**Primary Dependencies**: GitHub Copilot CLI skill discovery; Spec Kit Bash and PowerShell script layouts; existing `tools/sync_host_skills.py`

**Storage**: Repository files only

**Testing**: `pytest` contract tests, generated-distribution sync check, Markdown link/content assertions, `git diff --check`

**Target Platform**: GitHub Copilot CLI on Windows PowerShell and POSIX-compatible shells; existing Codex and Hermes hosts remain supported

**Project Type**: Documentation and agent-skill repository

**Performance Goals**: A new Copilot user locates an install path and first invocation in under three minutes; install/update commands complete in time proportional to the two skill directories

**Constraints**: Preserve the feature 003 distribution design; do not modify application code; personal lifecycle commands must be narrowly scoped, repeatable, and failure-safe; canonical skill descriptions remain unchanged per D-004

**Scale/Scope**: Three documentation files, one canonical implementation skill plus its generated copy, one contract-test module, one workflow file, and feature-local design artifacts

## Constitution Check

The repository constitution is still an uncustomized template, so it supplies no enforceable project-specific gate. The plan applies the established repository contracts instead:

- Canonical skills remain the source of generated `.agents/skills` copies.
- Refinement and implementation remain separately authorized.
- Existing Spec Kit integrations are preserved.
- Generated distributions must pass deterministic parity checks.
- Documentation examples must be safe, host-labeled, and non-destructive.

**Pre-design gate**: PASS. The plan does not introduce a new distribution architecture or application-code authority.

**Post-design gate**: PASS. The design keeps one canonical implementation skill, regenerates its portable copy, and adds verification for all modified contracts.

## Project Structure

### Documentation (this feature)

```text
specs/005-copilot-setup-docs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── copilot-setup-contract.md
│   └── platform-preflight-contract.md
├── reviews/
├── checklists/
├── refinery-state.md
├── spec.md
└── tasks.md
```

### Source Code (repository root)

```text
README.md
setup.md
docs/
└── host-compatibility.md
idea-refinery-implement/
└── SKILL.md
.agents/skills/
└── idea-refinery-implement/
    └── SKILL.md
tools/
└── sync_host_skills.py
tests/unit/
└── test_host_skill_distribution.py
.github/workflows/
└── refinery-evals.yml
```

**Structure Decision**: Extend the existing canonical-skill and generated-distribution structure. Documentation changes remain in current top-level files; platform-aware preflight is specified in the canonical implementation skill and propagated only through the existing synchronization tool.

## Design

### Documentation layering

`README.md` provides host selection, a short Copilot quick start, expected refinement output, the separate implementation handoff, and a link to the full lifecycle. `setup.md` owns executable project-local and personal Copilot installation, verification, update, removal, refresh, precedence, and troubleshooting. `docs/host-compatibility.md` retains cross-host capability, initialization-preservation, and synchronization rationale while labeling shell-specific commands.

### Personal installation safety

Both generated source directories are validated before either installed directory is replaced. Update uses a staging directory under the personal skills parent, verifies the staged trees, then replaces only the two named targets. Repeat execution yields exact source copies without nested directories or stale files. Removal treats missing targets as success.

### Platform-aware implementation preflight

The implementation entry gate inspects supported prerequisite scripts and invokes exactly one:

1. Prefer PowerShell on a Windows/PowerShell host when `.specify/scripts/powershell/check-prerequisites.ps1` exists.
2. Otherwise use `.specify/scripts/bash/check-prerequisites.sh` when it exists and the host can execute it.
3. Otherwise use the PowerShell script when it exists and the host can execute it.
4. If neither supported route is executable, stop and identify both expected paths.

Each route must request the same JSON, task-required, and task-inclusion semantics. The resolver changes only the preflight command; all existing entry gates remain intact.

### Validation strategy

Extend the existing host-distribution contract tests to read `README.md`, `setup.md`, `docs/host-compatibility.md`, the canonical implementation skill, and the workflow. Assertions cover:

- Copilot repository-local and personal paths;
- slash invocation, reload/restart, expected artifacts, and authority boundary;
- Windows and portable lifecycle sections;
- safe replacement/removal guarantees and precedence troubleshooting;
- Spec Kit preservation and initialization guidance;
- Bash and PowerShell preflight alternatives plus actionable failure;
- generated parity after synchronization;
- workflow path filters for both primary documentation files.

Timed discovery, full command walkthroughs, readability, and controlled execution of the four platform-preflight layouts remain explicit manual checks in `quickstart.md`.

## Complexity Tracking

No constitution violations require justification.
