# Setup and Tryout

This guide covers Codex local/global registration. For GitHub Copilot and Hermes project-skill installation, invocation, update, removal, and Spec Kit guidance, see [host compatibility](docs/host-compatibility.md).

## Choose a setup mode

| Mode | Best for | Changes global Codex skills? |
| --- | --- | --- |
| Direct-file session | Testing one checkout or branch | No |
| Global symlink | Regular use across repositories and future sessions | Yes, by adding two reversible links |

## Prerequisites

You need:

- a working `codex` command;
- an absolute path to this repository checkout;
- the `specify` CLI for full refinement;
- `uv` only when running the deterministic Python tests.

The target repository does not need to be initialized with Spec Kit in advance. `$idea-refinery-full` detects a missing `.specify/` directory, explains the files that initialization adds, and asks before running the command.

## Try `$idea-refinery-full` without global installation

Start Codex in the target repository and tell it to load the checkout's skill file directly:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-full/SKILL.md. Refine this idea: <describe your idea>"
```

Do not rely on the `$idea-refinery-full` name inside this session unless the skill is already registered globally. The explicit file instruction is the invocation.

The workflow should:

1. Inspect the target repository and project instructions.
2. Confirm the feature name and Spec Kit initialization state.
3. Ask before initialization or other required mutations.
4. Produce `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md` under the active feature directory.
5. Finish with a readiness verdict.

## Try `$idea-refinery-implement` without global installation

Use a target repository whose active feature came from Idea Refinery and is ready:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-implement/SKILL.md. Implement the active ready Idea Refinery feature."
```

The feature must contain `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`. A ready summary does not override an open material decision or unresolved high-severity finding.

Expected implementation behavior:

- validate checklists, hooks, readiness, and requirement-to-task coverage;
- record baseline/red/green/refactor evidence;
- parallelize only isolated, dependency-safe write sets, with at most three workers;
- obtain independent read-only review before promoting tasks;
- run up to two convergence implementation cycles;
- create or resume `implementation-state.md`;
- finish with `IMPLEMENTATION COMPLETE`, `BLOCKED ON DECISION`, or `BLOCKED ON VERIFICATION`.

For a fixture-based test, use [the implementation quickstart](specs/002-parallel-tdd-implementation/quickstart.md).

## Run both workflows in one session

Start with the direct-file full-refinement command. Once the workflow returns a ready verdict, send a separate message:

```text
Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-implement/SKILL.md.
Implement the active ready Idea Refinery feature.
```

The second message is required. Approval to refine an idea is not approval to change application code.

## Install both skills globally

Choose the checkout that should be the global source, then create two symlinks:

```bash
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
mkdir -p ~/.codex/skills
ln -sfn "$REFINERY_REPO/idea-refinery-full" \
  ~/.codex/skills/idea-refinery-full
ln -sfn "$REFINERY_REPO/idea-refinery-implement" \
  ~/.codex/skills/idea-refinery-implement
```

The source directories remain in the repository. The symlinks make them discoverable without creating duplicate copies.

Verify the registrations:

```bash
readlink ~/.codex/skills/idea-refinery-full
readlink ~/.codex/skills/idea-refinery-implement
```

Each command should print the matching folder under the checkout selected in `REFINERY_REPO`. If an existing link points to a different checkout, rerun the `ln -sfn` command with the intended absolute path.

Start a new Codex session after installing or changing the links:

```bash
codex --cd /absolute/path/to/target-repository
```

Then invoke refinement:

```text
$idea-refinery-full <describe your idea>
```

After the handoff is ready, invoke implementation separately:

```text
$idea-refinery-implement
```

## Update the global installation

Pull or edit the chosen checkout normally. Because the links point at that checkout, later sessions see the updated files automatically.

To switch to another checkout, set `REFINERY_REPO` to its absolute path and rerun both `ln -sfn` commands. Restart active Codex sessions so their available-skill catalog is rebuilt.

## Remove the global installation

First verify that the targets are symlinks pointing to the expected skill folders:

```bash
ls -ld ~/.codex/skills/idea-refinery-full
ls -ld ~/.codex/skills/idea-refinery-implement
```

Then remove only the two registration links:

```bash
rm ~/.codex/skills/idea-refinery-full
rm ~/.codex/skills/idea-refinery-implement
```

This does not delete the repository or any target project's feature artifacts.

## Validate the checkout

Run the deterministic support-runtime tests:

```bash
uv run --project idea-refinery-full --extra dev pytest -q
```

Inspect the CLI surface:

```bash
uv run --project idea-refinery-full idea-refinery --help
```

Validate either skill with the Skill Creator validator installed by Codex:

```bash
python3 /absolute/path/to/skill-creator/scripts/quick_validate.py \
  idea-refinery-full
python3 /absolute/path/to/skill-creator/scripts/quick_validate.py \
  idea-refinery-implement
```

The validator needs PyYAML. If the system Python lacks it, run the validator through a managed environment that includes this repository's dependencies.

## Troubleshooting

### The `$idea-refinery-*` command is missing

Run both `readlink` checks and confirm each target exists. Start a new Codex session; existing sessions do not necessarily reload the global skill catalog.

### The wrong checkout is loaded

`readlink` shows the active source. Rerun `ln -sfn` for both skills with the intended `REFINERY_REPO` path, then restart Codex.

### Full refinement says Spec Kit is missing

Install the `specify` CLI. If only the target repository is uninitialized, review and approve the initialization proposed by `$idea-refinery-full`:

```bash
specify init --here --integration codex --integration-options="--skills"
```

Never add `--force` unless you deliberately approve merging Spec Kit files into a nonempty project.

### Implementation refuses to start

Inspect the active feature pointer and state:

```bash
sed -n '1,120p' .specify/feature.json
sed -n '1,220p' "specs/<feature-id>/refinery-state.md"
```

Resolve open material decisions, missing artifacts, failed checklists, unresolved high-severity findings, or absent requirement-to-task mappings through the refinement workflow.

### Preferred Superpowers skills are unavailable

This changes composition, not required behavior. `$idea-refinery-implement` records `composition: local-fallback` and applies its local scheduling, TDD, review, and verification contracts. It must never claim that an unavailable skill ran.

## Related documentation

- [Project overview](README.md)
- [Repository structure](RepoStructure.md)
- [Full refinement architecture](idea-refinery-full/ARCHITECTURE.md)
- [Implementation architecture](idea-refinery-implement/ARCHITECTURE.md)
