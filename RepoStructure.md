# Idea Refinery Repository Structure

This reference explains which files are maintained source, which are generated feature artifacts, and which workflow should use each part of the repository.

## Top-level map

```text
IdeaRefinery/
├── README.md                       # project entry point and quick tryout
├── setup.md                        # detailed local/global installation how-to
├── RepoStructure.md                # this repository reference
├── idea-refinery-full/             # refinement skill and deterministic runtime
├── idea-refinery-implement/        # parallel TDD implementation skill
├── specs/                          # Spec Kit feature artifacts for this project
├── .idea-refinery/                 # optional per-repository role/config overrides
├── .specify/                       # Spec Kit configuration, templates, and scripts
├── .agents/skills/speckit-*/       # repository-local Spec Kit skills
├── .agents/skills/idea-refinery-*/ # generated Copilot/Hermes skill distribution
└── .github/workflows/              # deterministic runtime CI
```

The two skill folders are intentionally separate. `idea-refinery-full/` owns refinement and stops at an implementation-ready handoff. `idea-refinery-implement/` consumes that handoff and has separate authority to edit application code and tests.

`tools/sync_host_skills.py` generates `.agents/skills/idea-refinery-*` from the canonical folders and copies their required references. GitHub Copilot discovers this standard project-skill location; Hermes can use it as an external source or receive a copy under its skill home. See [host compatibility](docs/host-compatibility.md).

`.idea-refinery/config.yaml` is optional and may exist in a target repository even when it is absent from this checkout. Its role assignments override bundled defaults but remain below invocation-level overrides.

## `idea-refinery-full/`

```text
idea-refinery-full/
├── SKILL.md
├── ARCHITECTURE.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── orchestration-contract.md
│   └── refinery-state-template.md
├── defaults/
│   └── config.yaml
├── schemas/
│   ├── config.schema.json
│   ├── invocation.schema.json
│   ├── repair-packet.schema.json
│   ├── review-result.schema.json
│   ├── run-manifest.schema.json
│   └── trace-event.schema.json
├── src/idea_refinery/
│   ├── cli.py
│   ├── config.py
│   ├── briefs.py
│   ├── envelopes.py
│   ├── coverage.py
│   ├── findings.py
│   ├── synthesis.py
│   ├── readiness.py
│   ├── invalidation.py
│   ├── repair.py
│   ├── run_store.py
│   ├── schemas.py
│   ├── io.py
│   ├── errors.py
│   ├── types.py
│   └── evals/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── property/
│   ├── integration/
│   ├── performance/
│   └── fixtures/
├── pyproject.toml
└── uv.lock
```

| Path | Purpose | Typical use |
| --- | --- | --- |
| `SKILL.md` | Explicit-only controller workflow | Load when invoking `$idea-refinery-full` |
| `ARCHITECTURE.md` | Explanation of stages, roles, persistence, repair, and readiness | Understand why stages are separate and how data moves |
| `agents/openai.yaml` | UI name, prompt, and implicit-invocation policy | Skill discovery metadata |
| `references/orchestration-contract.md` | Normative finding, coverage, repair, and handoff rules | Implement or audit controller behavior |
| `references/refinery-state-template.md` | Human-readable decision/question/review ledger template | Initialize a new feature's `refinery-state.md` |
| `defaults/config.yaml` | Bundled model roles, fallbacks, effort, and limits | Resolve a run when no repository/invocation override exists |
| `schemas/` | Versioned machine-readable contracts | Validate config, manifests, envelopes, repairs, and events |
| `src/idea_refinery/` | Deterministic support package | Hash, validate, persist, synthesize, repair, and evaluate without calling models |
| `tests/` | Runtime behavior and invariant coverage | Run locally or in CI before changing deterministic behavior |

The Python package is not an autonomous agent runtime. It never discovers or invokes models, reads provider credentials, or calls external model CLIs. The active Codex session owns all model execution and user interaction.

## `idea-refinery-implement/`

```text
idea-refinery-implement/
├── SKILL.md
├── ARCHITECTURE.md
├── agents/
│   └── openai.yaml
└── references/
    ├── orchestration-contract.md
    └── implementation-state-template.md
```

| Path | Purpose | Typical use |
| --- | --- | --- |
| `SKILL.md` | Explicit-only implementation controller | Invoke after a ready Idea Refinery handoff |
| `ARCHITECTURE.md` | Explanation of entry, scheduling, TDD, review, convergence, and completion | Understand the difference between execution gates |
| `agents/openai.yaml` | UI metadata and explicit-only policy | Global or project skill discovery |
| `references/orchestration-contract.md` | Normative worker envelopes, isolation, evidence, review, and recovery rules | Audit or extend implementation behavior |
| `references/implementation-state-template.md` | Resumable wave, assignment, evidence, finding, and verification state | Create `implementation-state.md` in an active feature |

This skill is instruction-backed; it does not currently have a Python sidecar. Add deterministic code only when repeated runtime behavior cannot be expressed or verified reliably through the existing contracts.

## `.specify/`

`.specify/` makes this repository a Spec Kit project.

```text
.specify/
├── feature.json                    # active feature-directory pointer
├── init-options.json               # initialization and numbering choices
├── integration.json                # installed integration metadata
├── integrations/                   # Codex and Spec Kit manifests
├── memory/
│   └── constitution.md             # project governance
├── scripts/bash/                   # prerequisite and artifact setup scripts
├── templates/                      # spec, plan, task, and checklist templates
└── workflows/                      # workflow registry
```

`.specify/feature.json` determines which feature downstream Spec Kit commands treat as active. Inspect it before planning, task generation, analysis, convergence, or implementation.

The current `constitution.md` is an unfilled template. It imposes no active project gates until the project ratifies concrete principles.

## `.agents/skills/`

The `speckit-*` folders are repository-local skill definitions installed by Spec Kit. They create, clarify, plan, task, analyze, converge, and implement the active feature. Idea Refinery composes these skills; it does not replace their artifact formats.

Important boundaries:

- `$speckit-analyze` is read-only.
- `$speckit-converge` may append a convergence phase to `tasks.md` but does not implement it.
- `$speckit-implement` supplies prerequisite, checklist, hook, and task-state conventions; `idea-refinery-implement` adds stronger isolation, TDD evidence, and independent review.

## `specs/`

Each child directory is a Spec Kit feature package. The two checked-in features document the construction of this repository itself:

| Feature | Purpose |
| --- | --- |
| `001-refinery-quality-orchestration/` | Requirements, design, reviews, contracts, and tasks for the deterministic full-refinement runtime |
| `002-parallel-tdd-implementation/` | Requirements, design, review ledger, and tasks for the implementation skill |

A feature may contain:

```text
specs/<feature-id>/
├── spec.md                         # product and behavior contract: what must be true
├── plan.md                         # technical design: how it will be achieved
├── tasks.md                        # ordered execution state: what to do next
├── refinery-state.md               # decisions, questions, findings, stage history, readiness
├── implementation-state.md         # waves, workers, TDD/review evidence, convergence, verification
├── research.md                     # recorded technical choices and alternatives
├── data-model.md                   # entities, relationships, and state transitions
├── quickstart.md                   # runnable validation scenarios
├── contracts/                      # machine or human interface contracts
├── checklists/                     # requirements-quality gates
└── runs/<run-id>/                  # immutable objects, events, manifests, and stage commits
```

`implementation-state.md` and `runs/` are created only when their corresponding workflows need them; they need not exist in every feature.

## `.github/workflows/`

`refinery-evals.yml` runs the deterministic Python tests for changes under `idea-refinery-full/`, Spec 001, or the workflow itself. It currently does not trigger for changes limited to `idea-refinery-implement/`, Spec 002, or top-level documentation. Validate those changes locally.

## Source, generated artifacts, and runtime state

| Category | Examples | Editing rule |
| --- | --- | --- |
| Maintained skill source | Both `SKILL.md` files, architecture docs, references, defaults, schemas, Python package | Edit deliberately and validate |
| Project configuration | `.specify/`, `.agents/skills/`, workflow files | Change only when updating project/tool integration |
| Checked-in feature design | `specs/001-*`, `specs/002-*` | Preserve requirement IDs, decisions, and audit history |
| Per-target generated artifacts | A target repository's `specs/<feature-id>/` | Controller-owned; component workers must not overwrite shared state |
| Ephemeral local output | `.venv/`, `.pytest_cache/`, `.hypothesis/`, bytecode | Do not document as product source or commit accidentally |
| Global registration | `~/.codex/skills/idea-refinery-*` symlinks | Points to source; removing a link does not remove the source |

## Common use cases

| Goal | Entry point | Files involved |
| --- | --- | --- |
| Turn a new idea into an implementation-ready contract | `$idea-refinery-full <idea>` | Target repository `.specify/` and new/active `specs/<feature-id>/` |
| Resume a refinement run | `$idea-refinery-full` with the same active feature | `refinery-state.md` and `runs/<run-id>/` |
| Implement a ready handoff | `$idea-refinery-implement` | Active spec/plan/tasks/state plus target application code/tests |
| Test the deterministic support package | `uv run --project idea-refinery-full --extra dev pytest -q` | `src/idea_refinery/`, schemas, defaults, and tests |
| Inspect deterministic CLI commands | `uv run --project idea-refinery-full idea-refinery --help` | `src/idea_refinery/cli.py` |
| Validate the implementation skill | Skill Creator validator and Spec 002 quickstart | `idea-refinery-implement/`, `specs/002-*/quickstart.md` |
| Review before landing | Optional gstack `$review` after implementation verification | Final branch diff; separate user authorization |
| Initialize Spec Kit in a target repository | `specify init --here --integration codex --integration-options="--skills"` | Adds `.specify/` and repository-local Spec Kit skills after approval |

## Local source versus global registration

The repository folders are the source of truth. Global installation uses symlinks:

```text
~/.codex/skills/idea-refinery-full      -> <checkout>/idea-refinery-full
~/.codex/skills/idea-refinery-implement -> <checkout>/idea-refinery-implement
```

This avoids duplicated skill copies. New Codex sessions read the linked checkout; existing sessions may need restarting after source or link changes. See [setup.md](setup.md) for exact commands.

## Related documentation

- [Project overview and tutorials](README.md)
- [Detailed setup and installation](setup.md)
- [Full refinement architecture](idea-refinery-full/ARCHITECTURE.md)
- [Implementation architecture](idea-refinery-implement/ARCHITECTURE.md)
