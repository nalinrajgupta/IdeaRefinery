# Idea Refinery

Idea Refinery turns a rough product or engineering idea into an implementation-ready contract, then executes that contract through a separately authorized, test-driven workflow.

The repository provides two explicit-only workflows for Codex, GitHub Copilot, and Hermes:

| Skill | Use it when | Result |
| --- | --- | --- |
| `$idea-refinery-full <idea>` | You need to discover, review, clarify, plan, and task an idea | A ready or decision-blocked Spec Kit feature containing `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md` |
| `$idea-refinery-implement` | The active Idea Refinery feature is ready and you want application changes | Reviewed code and tests, completed task state, `implementation-state.md`, convergence, and fresh verification evidence |

The split is an authority boundary. Refinement may create and revise design artifacts but never application code. Implementation may change the code and tests required by the approved handoff but never silently change product scope or architecture.

## End-to-end lifecycle

```text
Rough idea
  -> $idea-refinery-full
       -> repository and Spec Kit setup
       -> Superpowers brainstorming
       -> Spec v1
       -> independent CEO + Product + Architect reviews
       -> synthesis and Spec v2
       -> clarification
       -> technical plan and tasks
       -> consistency analysis and bounded repair
       -> READY FOR IMPLEMENTATION
  -> separate user invocation
  -> $idea-refinery-implement
       -> readiness and traceability preflight
       -> dependency-safe task waves
       -> isolated red-green-refactor workers
       -> independent wave review
       -> Spec Kit convergence
       -> fresh final verification
       -> IMPLEMENTATION COMPLETE
  -> optional gstack review / ship workflow
```

Use the architecture documents for the exact stage boundaries:

- [Full refinement architecture](idea-refinery-full/ARCHITECTURE.md)
- [Implementation architecture](idea-refinery-implement/ARCHITECTURE.md)
- [Repository and file structure](RepoStructure.md)
- [Host compatibility and installation](docs/host-compatibility.md)

## Prerequisites

For refinement:

- Codex with skill support
- Superpowers `brainstorming`
- gstack `plan-ceo-review` and `plan-eng-review`
- Spec Kit's `specify` CLI and repository-local `speckit-*` skills

If the target repository is not a Spec Kit project, `$idea-refinery-full` explains and requests approval before running:

```bash
specify init --here --integration codex --integration-options="--skills"
```

For implementation, the active feature must have:

- `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`;
- a `ready-for-implementation` or explicitly waived `ready-for-implementation-degraded` verdict;
- no unresolved material decision or blocker/critical/high finding;
- complete requirement-to-task traceability.

The implementation skill prefers Superpowers subagent, TDD, debugging, review, and verification components. When one is unavailable, it records `composition: local-fallback` and applies the same evidence gates locally. Missing optional composition never relaxes readiness, isolation, review, or verification.

## Try refinement in one session

You can test the checkout without changing global skill registration. Start Codex in the repository whose idea you want to refine and explicitly point it at the local skill source:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-full/SKILL.md. Refine this idea: <describe your idea>"
```

This direct-file form does not depend on `$idea-refinery-full` already being globally discoverable. The workflow first inspects the target repository, then asks for approval before initialization or artifact writes.

Expected result:

```text
target-repository/specs/<feature-id>/
├── spec.md
├── plan.md
├── tasks.md
└── refinery-state.md
```

The final verdict is `READY FOR IMPLEMENTATION`, `READY FOR IMPLEMENTATION — DEGRADED`, or `BLOCKED ON DECISION`.

## Try implementation in a later session

Starting implementation in a fresh session reduces stale context and makes the authority transition explicit:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-implement/SKILL.md. Implement the active ready Idea Refinery feature."
```

The skill validates the handoff again, records baseline and TDD evidence, schedules at most three safely isolated workers, obtains independent review, runs up to two convergence implementation cycles, and performs fresh final verification.

To test the implementation skill itself against a fixture rather than a real application, follow [Spec 002's quickstart](specs/002-parallel-tdd-implementation/quickstart.md).

## Try both in the same session

Start with the refinement command above. After it returns `READY FOR IMPLEMENTATION`, explicitly authorize the second skill in a new message:

```text
Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-implement/SKILL.md.
Implement the active ready feature.
```

Do not combine both instructions into the initial prompt. The pause preserves the approval boundary between writing plans and changing application code.

## Install both skills globally

Global registration lets new Codex sessions invoke the skills by name:

```bash
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
mkdir -p ~/.codex/skills
ln -sfn "$REFINERY_REPO/idea-refinery-full" \
  ~/.codex/skills/idea-refinery-full
ln -sfn "$REFINERY_REPO/idea-refinery-implement" \
  ~/.codex/skills/idea-refinery-implement
```

Verify both links:

```bash
readlink ~/.codex/skills/idea-refinery-full
readlink ~/.codex/skills/idea-refinery-implement
```

Start a new Codex session in the target project, then invoke:

```text
$idea-refinery-full <describe your idea>
```

After the resulting handoff is ready, invoke separately:

```text
$idea-refinery-implement
```

Existing Codex sessions may need restarting after skill links or instructions change. See [setup.md](setup.md) for updating, removing, and troubleshooting registrations.

## Architecture summary

### Refinement

`$idea-refinery-full` combines an active-session controller with a deterministic Python sidecar. The controller owns dialogue, model roster capture, delegation, and all shared writes. The package under `idea-refinery-full/src/idea_refinery/` owns versioned configuration, schemas, hashes, immutable run objects, coverage, repair checkpoints, readiness, and offline evaluation. It never invokes provider APIs or model CLIs.

The default reviewer roles are CEO `gpt-5.5`, Product `gpt-5.6-terra`, Architect `gpt-5.6-sol`, Eval `gpt-5.6-luna`, and Baseline `gpt-5.4`, with ordered fallbacks and effort rules in [the bundled configuration](idea-refinery-full/defaults/config.yaml). Invocation overrides take precedence over repository config, which takes precedence over bundled defaults.

### Implementation

`$idea-refinery-implement` keeps the controller as the only writer of shared task and state artifacts. It derives conservative write sets, requires host-enforced isolation for parallel edits, caps waves at three workers, binds implementation to recorded baseline/red/green/refactor evidence, and requires a different read-only reviewer before task promotion. `$speckit-converge` detects omitted work after the planned tasks complete; gstack `$review` remains an optional pre-landing concern.

## Develop and validate

Run the deterministic full-runtime suite:

```bash
uv run --project idea-refinery-full --extra dev pytest -q
```

Inspect deterministic CLI commands:

```bash
uv run --project idea-refinery-full idea-refinery --help
```

Validate the implementation skill structure with Codex's Skill Creator validator:

```bash
python3 /absolute/path/to/skill-creator/scripts/quick_validate.py \
  idea-refinery-implement
```

The GitHub workflow currently runs deterministic tests for changes under `idea-refinery-full/`, Spec 001, and the workflow file. Documentation-only and implementation-skill changes still need local validation.

## Safety boundaries

Neither skill commits, pushes, opens pull requests, merges, deploys, creates issues, or performs destructive cleanup unless the user separately requests a workflow with that authority.

- `$idea-refinery-full` asks before Spec Kit initialization or artifact mutation where required.
- `$idea-refinery-implement` stops on material decisions, unexplained verification failures, unsafe write overlap, or missing independent review.
- Review workers are read-only; shared state remains controller-owned.
- Existing unrelated user changes are preserved.

## Documentation map

| Document | Reader goal |
| --- | --- |
| [Full refinement architecture](idea-refinery-full/ARCHITECTURE.md) | Understand stages, reviewer roles, state, repair, and readiness |
| [Implementation architecture](idea-refinery-implement/ARCHITECTURE.md) | Understand scheduling, isolation, TDD, review, convergence, and completion |
| [Repository structure](RepoStructure.md) | Find source, generated artifacts, configuration, tests, and use cases |
| [Setup and tryout](setup.md) | Install, update, remove, or test both skills |
| [Full skill entrypoint](idea-refinery-full/SKILL.md) | Read the normative refinement instructions |
| [Implementation skill entrypoint](idea-refinery-implement/SKILL.md) | Read the normative implementation instructions |
| [Full orchestration contract](idea-refinery-full/references/orchestration-contract.md) | Audit refinement finding/readiness rules |
| [Implementation orchestration contract](idea-refinery-implement/references/orchestration-contract.md) | Audit worker, evidence, review, and recovery rules |
| [Spec 001](specs/001-refinery-quality-orchestration/spec.md) | See requirements for the full deterministic runtime |
| [Spec 002](specs/002-parallel-tdd-implementation/spec.md) | See requirements for the implementation skill |

## Troubleshooting

- **Skill name is not recognized**: verify both `readlink` commands, then start a new Codex session.
- **Refinement cannot locate Spec Kit**: install `specify`; allow `$idea-refinery-full` to initialize the target only after reviewing its proposed changes.
- **Implementation rejects the feature**: inspect `refinery-state.md` for the verdict, open decisions, unresolved high-severity findings, and missing traceability.
- **Superpowers implementation components are absent**: the skill should record local fallback composition; it must not claim those components ran.
- **`uv` cannot write its cache in a sandbox**: run validation in an environment where the project cache is writable or approve the narrowly scoped cache access.
