# Implementation Plan: Cross-Host Idea Refinery Skills

**Branch**: `003-copilot-hermes-skills` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

## Summary

Make the existing full-refinement and implementation workflows portable to GitHub Copilot and Hermes without weakening their authority, safety, or evidence gates. Canonical skill bodies remain in `idea-refinery-full/` and `idea-refinery-implement/`; a deterministic generator produces the shared project-skill distribution consumed by Copilot and installable by Hermes. Documentation provides per-host setup and capability guidance.

## Technical Context

**Language/version**: Python 3.11+ (existing deterministic runtime)  
**Primary dependencies**: Standard library; existing `pytest` development dependency  
**Storage**: Repository Markdown and generated project-skill files  
**Testing**: `pytest`; structural skill validation where available; documentation/reference assertions  
**Target platforms**: Codex, GitHub Copilot, Hermes Agent  
**Constraints**: Full instructions must be generated from one canonical source; fallback never relaxes authorization, evidence, independent review, or safe parallelism gates.

## Architecture

```text
canonical Codex skill folders
  ├─ idea-refinery-full/SKILL.md
  └─ idea-refinery-implement/SKILL.md
             │
             ▼ deterministic sync + parity test
  .agents/skills/idea-refinery-{full,implement}/SKILL.md
             ├─ GitHub Copilot project-skill discovery
             └─ Hermes external-source or copied installation
```

### Components

| Component | Responsibility |
| --- | --- |
| Canonical skills | Declare the complete workflows and host-neutral capability contract. |
| Distribution generator | Produces the shared `.agents/skills` host distribution from canonical sources without manual copying. |
| Parity validation | Verifies generated content, frontmatter, reference availability, and required safety clauses. |
| Host documentation | Explains discovery, installation, invocation, Spec Kit integration, update/removal, and limitations per host. |

### Capability contract

Every host entrypoint first discovers available skills, isolation, delegation, and command support. It uses a host-native capability only when it satisfies the relevant gate. Otherwise it applies the same local contract, uses controller-applied patches or sequential execution where isolation is absent, records `composition: local-fallback`, and blocks rather than claiming unavailable evidence. Existing Spec Kit configuration is preserved; initialization only uses a host-specific integration for a previously uninitialized target after explicit approval.

### Distribution format

The generator copies canonical `SKILL.md` bodies and every required relative support document into `.agents/skills/idea-refinery-full/` and `.agents/skills/idea-refinery-implement/`, adding a minimal generated-source marker and host-neutral capability preamble. The generated files use standard agent-skill frontmatter and relative references that exist in the distribution. A sync check runs in CI/tests and rejects stale output, missing references, or source-to-distribution drift. GitHub Copilot discovers `.agents/skills`; Hermes can configure the same directory as an external source or install the generated folders under its skill home.

## Data and interfaces

No runtime data model changes. The generator interface accepts a repository root and supports `--check` (no writes) and default synchronization. Validation imports the generator rather than parsing shell output.

## Implementation phases

1. Define the canonical host-neutral capability and initialization language in both workflow skills.
2. Add deterministic distribution generation of skill bodies and required support references, plus tests.
3. Generate the shared project-skill folders and verify their required references.
4. Add a host setup/capability document and update overview, setup, and repository-map documentation.
5. Extend validation/CI triggers for distributions and documentation, then run the full suite and structural checks.

## Test strategy

- Unit-test generation and `--check` behavior using temporary repositories.
- Assert canonical-to-generated parity and the presence of mandatory workflow gates.
- Assert required host setup topics and generated paths are documented.
- Run the existing deterministic runtime suite and `git diff --check`.

## Complexity and risk

Generated distributions prevent semantic drift but require reference paths to be portable. The implementation must prefer a shared `.agents/skills` distribution instead of independent Copilot and Hermes copies. Host features remain capability-detected; the documented fallback hierarchy is the safety boundary when host tooling changes.
