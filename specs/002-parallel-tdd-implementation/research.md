# Research: Parallel TDD Implementation Skill

## Decision: Use a Superpowers-first hybrid

**Rationale**: Superpowers provides the best task-level composition for subagent development, TDD, debugging, review, and completion verification. Spec Kit provides the stronger artifact, checklist, hook, task-state, and convergence contract. gstack review is strongest as a holistic pre-landing diff review rather than an inner implementation loop.

**Alternatives considered**:

- Direct `$speckit-implement` wrapper: rejected because its TDD evidence and independent review contracts are too shallow for this goal.
- gstack-centered execution: rejected because the available gstack skills focus on planning, QA, review, and landing rather than implementing a task graph.
- Strict Superpowers dependency: rejected because most Superpowers components are cataloged but not loaded in the current session; a disclosed equivalent fallback keeps the custom skill usable without weakening gates.

## Decision: Share a workspace only for disjoint paths

**Rationale**: Multiple workers can safely edit separate subfolders only when they do not also share lockfiles, schemas, generated outputs, fixtures, configuration, or migration order. Conservative write sets and controller-only shared state are simpler than automatic worktree integration.

**Alternatives considered**:

- One worktree per task: stronger filesystem isolation but introduces merge sequencing, branch lifecycle, and cleanup authority not granted by this skill.
- Trust Spec Kit `[P]` markers: insufficient because markers cannot capture implicit shared resources or unrelated dirty paths.

## Decision: Review every wave and converge after the initial pass

**Rationale**: Task-level tests can pass while a requirement remains missing. Independent review catches defects in the changed slice; convergence catches spec-to-code omissions across the whole feature.

**Alternatives considered**:

- Final review only: permits defects to compound across dependent waves.
- Unbounded convergence: risks repeating the same root issue without new information.
