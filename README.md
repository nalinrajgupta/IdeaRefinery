# Idea Refinery

Idea Refinery turns a rough product or engineering idea into a handoff that other coding agents can implement without making material product or architecture decisions.

It provides one explicit-only Codex skill:

| Command | Use it when | Output |
| --- | --- | --- |
| `$idea-refinery-full <idea>` | You want the complete, artifact-backed pipeline with reviews, clarification, a technical plan, and an execution task list. | A Spec Kit feature directory containing `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`. |

## Quick start

Start a new Codex CLI session in the repository you want to refine, then run:

```text
$idea-refinery-full Build a collaborative idea-review workspace for product teams.
```

## Full workflow

```text
Idea
  -> Superpowers brainstorming
  -> approved design + Spec Kit Spec v1
  -> CEO, product, and architect reviews
  -> gstack-style synthesis + Spec v2
  -> Spec Kit clarification
  -> Spec Kit plan + tasks
  -> Spec Kit analysis
  -> resolve material gaps
  -> implementation handoff
```

The workflow is intentionally sequential at decision points and independent at review points. Reviewers do not rewrite the spec directly; their findings flow into an audit ledger, then a synthesis pass resolves each finding.

## Skills and responsibilities

| Stage | Skill or component | Reads | Produces |
| --- | --- | --- | --- |
| Discovery | `$brainstorming` (Superpowers) | The raw idea, repository context, project instructions | One-question-at-a-time discovery, 2–3 approaches, trade-offs, and an approved design direction |
| Spec v1 | `$speckit-specify` | Approved design and Spec Kit project principles | Initial feature `spec.md` |
| CEO review | `$plan-ceo-review` (gstack) | Spec v1 and relevant repository context | Value, positioning, scope, and strategic-risk findings |
| Product review | Idea Refinery’s product critic | Spec v1 | User-journey, value, and requirement findings |
| Architect review | `$plan-eng-review` (gstack) | Spec v1 and relevant repository context | Feasibility, architecture, reliability, security, operational, and test-strategy findings |
| Synthesis | Idea Refinery | The three independent review artifacts and `refinery-state.md` | Spec v2 and a resolved review ledger |
| Clarification | `$speckit-clarify` | Active `spec.md`, `.specify/` project configuration | Up to five high-impact clarification answers written into `spec.md` |
| Design and tasking | `$speckit-plan`, `$speckit-tasks` | Clarified spec and project constitution | `plan.md` and `tasks.md` |
| Consistency gate | `$speckit-analyze` | `spec.md`, `plan.md`, `tasks.md`, and project constitution | Read-only coverage, ambiguity, terminology, and consistency report |

## Inputs

### Required inputs

- The idea supplied after `$idea-refinery-full`.
- The active repository’s source, tests, existing specifications, and project instructions such as `AGENTS.md`.
- User decisions made during discovery. These are retained in the decision queue and are not reopened without new evidence.

- The globally installed Superpowers brainstorming skill: `~/.codex/skills/brainstorming/SKILL.md`.
- The installed gstack review skills: `~/.codex/skills/gstack-plan-ceo-review/` and `~/.codex/skills/gstack-plan-eng-review/`.
- The `specify` CLI and a Spec Kit project structure in the target repository:

  ```text
  .specify/                 # constitution, templates, scripts, integration config
  .agents/skills/           # project-local speckit-* skills
  ```

If `.specify/` is absent, full mode explains the required `specify init` operation and asks for confirmation before creating it. Initialization, specification, planning, and tasking write repository files; analysis remains read-only.

## Outputs

Spec Kit creates the active feature directory, normally:

```text
specs/<feature-id>/
├── spec.md                 # Final refined product and behavioral contract
├── plan.md                 # Final technical design and delivery approach
├── tasks.md                # Final ordered, executable implementation worklist
└── refinery-state.md       # Shared decisions, questions, review findings, and stage history
```

## Final output for implementation agents

**`specs/<feature-id>/tasks.md` is the final execution entry point.** Give implementation agents this file first, but require them to read its companion `spec.md` and `plan.md` before changing code. The three files form one contract:

- `spec.md` says **what** must be true for users.
- `plan.md` says **how** the system should achieve it.
- `tasks.md` says **what to do next**, in order.

The full pipeline finishes only when high-severity review and analysis findings are resolved, explicitly deferred with a trigger, or placed in a human-owned decision queue. Its handoff verdict is either `READY FOR IMPLEMENTATION` or `BLOCKED ON DECISION`.

`refinery-state.md` prevents component skills from asking the same underlying question twice. Before every stage, Idea Refinery passes it as a brief of settled decisions and answered questions. A question may be reopened only when new evidence changes the trade-off and the reopen rationale is recorded.

## Skill source and global registration

All custom source files live in this folder:

```text
idea-refinery-full/         # Full orchestration source
README.md                   # This guide
```

Codex discovers them globally through symlinks:

```text
~/.codex/skills/idea-refinery-full
```

This symlink points back to this folder, so updating `SKILL.md` changes the globally available skill without duplicating custom files.
