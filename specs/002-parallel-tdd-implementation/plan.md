# Implementation Plan: Parallel TDD Implementation Skill

**Branch**: `feature/v3` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-parallel-tdd-implementation/spec.md`

## Summary

Add an explicit-only `idea-refinery-implement` sibling skill that consumes the active Spec Kit handoff, schedules only dependency-safe and write-disjoint work in parallel, requires recorded red-green-refactor evidence, obtains independent read-only review, and runs bounded Spec Kit convergence. Superpowers implementation components are preferred when present; the skill retains equivalent local contracts when they are absent. gstack review remains a separate pre-landing gate.

## Technical Context

**Language/Version**: Markdown Agent Skills with YAML frontmatter; repository Python tooling remains unchanged

**Primary Dependencies**: Codex skills runtime, bounded subagents, Spec Kit `speckit-implement` and `speckit-converge`; optional Superpowers and gstack skills

**Storage**: Feature-local Markdown state in `implementation-state.md`

**Testing**: Skill Creator `quick_validate.py`, structural/invariant scans, and isolated forward evaluation

**Target Platform**: Codex sessions operating inside Spec Kit repositories

**Project Type**: Explicit-only orchestration skill

**Performance Goals**: Form a safe execution wave without unnecessary model work; dispatch no more than three workers

**Constraints**: Shared workspace, user-owned dirty changes, component-skill availability varies by session, no automatic git or deployment mutations

**Scale/Scope**: One active Spec Kit feature per invocation; at most three implementation workers and two convergence cycles

## Constitution Check

The repository constitution is an unfilled template, so it imposes no active gates. The plan still follows the template's example principles by keeping the skill isolated, testable, and explicit about TDD and review.

**Post-design re-check**: Pass. No active constitution rule is contradicted.

## Architecture

```text
active Spec Kit feature
  -> entry/readiness gate
  -> task inventory + dependency/write-set graph
  -> deterministic waves (capacity <= 3)
  -> bounded TDD workers
  -> controller evidence inspection
  -> independent read-only reviewer
  -> task promotion + integrated verification
  -> speckit-converge (0..2 implementation cycles)
  -> fresh completion verification
  -> optional gstack pre-landing review
```

The controller is the single writer for shared coordination artifacts. Parallel workers receive immutable, versioned assignments and an enforceable scoped write boundary; without one they return patches or execution is sequential. Reviewers receive immutable evidence and never edit. Skill routing is late-bound from the current session's actual capabilities; local contracts preserve behavior when optional Superpowers components are missing.

## Project Structure

### Documentation for this feature

```text
specs/002-parallel-tdd-implementation/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── refinery-state.md
├── contracts/
│   └── orchestration-envelopes.md
└── tasks.md
```

### Skill source

```text
idea-refinery-implement/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── orchestration-contract.md
    └── implementation-state-template.md
```

Existing integration points:

- `idea-refinery-full/SKILL.md` advertises the separate opt-in handoff without invoking it.
- `README.md` documents both skills and their authority boundary.
- No Python sidecar changes are required until deterministic wave construction becomes demonstrated repeated logic.

## Error Handling

- Missing or blocked handoff: stop before application edits.
- Missing preflight requirement-to-task mapping: stop before dispatch and repair the task plan.
- Unknown/overlapping or unenforceable write set: serialize or use controller-applied patches; if a worker discovers it later, stop and reschedule.
- Invalid red evidence: do not permit production edits or task promotion.
- Worker failure: retain independently inspectable changes but do not promote the slice.
- Missing/invalid reviewer result: set `review-blocked` and obtain a replacement reviewer.
- Artifact/path drift after dispatch: quarantine the affected envelope and result, attribute with a three-way comparison, then re-plan.
- Repeated convergence root: stop after the bounded budget and report the unresolved requirement.

## Test Strategy

1. Structural validation checks skill naming, YAML, metadata, links, and placeholders.
2. Static invariant checks ensure explicit-only policy, three-worker cap, two-cycle cap, single-writer rule, red/green evidence, independent reviewer, and mutation exclusions are present.
3. Forward evaluation uses a temporary Spec Kit fixture with independent and conflicting tasks and verifies safe wave behavior from the skill instructions.
4. Review compares the skill and supporting references against all FR/SC identifiers.

## Complexity Tracking

No constitution violations. The sibling skill and two focused references are the smallest structure that preserves a short entrypoint while keeping the fragile orchestration/evidence contract explicit.
