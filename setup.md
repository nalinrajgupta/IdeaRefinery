# Setup and Tryout

This guide covers GitHub Copilot and Codex installation, invocation, update, removal, and troubleshooting. Hermes users should start with [host compatibility](docs/host-compatibility.md).

## Choose a setup mode

| Host | Mode | Best for | Installed location |
| --- | --- | --- | --- |
| GitHub Copilot | Repository-local skills | One project and checked-in team configuration | `.agents/skills/refine-idea`, `.agents/skills/implement-refine-idea` |
| GitHub Copilot | Personal copied skills | Reuse across repositories | `~/.copilot/skills/refine-idea`, `~/.copilot/skills/implement-refine-idea` |
| Codex | Direct-file session | Testing one checkout or branch | No registration |
| Codex | Global symlink | Reuse across repositories | `~/.codex/skills/refine-idea`, `~/.codex/skills/implement-refine-idea` |

## Prerequisites

You need:

- GitHub Copilot CLI or Codex;
- an absolute path to this repository checkout;
- the `specify` CLI for full refinement;
- Python and `uv` only for deterministic repository validation.

Before initializing Spec Kit, inspect the target repository. If `.specify/` already exists, preserve it and do not reinitialize the repository; inspect `.specify/integration.json` when that metadata file is available. Only when `.specify/` is absent does an uninitialized GitHub Copilot target use:

```text
specify init --here --integration copilot
```

Review the files this command will add and approve the mutation before running it. Never use `--force` unless you explicitly intend to merge Spec Kit files into a nonempty repository.

## GitHub Copilot

Copilot personal skills live under `~/.copilot/skills` (`$HOME\.copilot\skills` in PowerShell).

### Repository-local skills

This repository checks in both generated project-local skills:

```text
.agents/skills/refine-idea
.agents/skills/implement-refine-idea
```

To install them into another project, copy both generated folders to that project's `.agents/skills` directory and commit them with the project if team-wide discovery is desired. Do not copy only `SKILL.md`; the full skill bundles its required runtime and references.

After adding or updating skills, start Copilot CLI in the target repository and run:

```text
/skills reload
```

Use `/skills` to inspect the loaded skills and their locations. When project-local and personal copies both exist, the project-local copy is authoritative for that repository; update or remove the stale project copy if a personal update appears ineffective.

Invoke refinement:

```text
/refine-idea <idea>
```

After the workflow returns `READY FOR IMPLEMENTATION`, authorize implementation separately:

```text
/implement-refine-idea
```

The generated descriptions retain dollar-prefixed explicit-invocation wording shared with other hosts. GitHub Copilot CLI commands use the slash-prefixed forms above.

### Personal installation on Windows PowerShell

Set the checkout path, then stage and verify both generated skills before replacing either personal target:

```powershell
$RefineryRepo = "C:\absolute\path\to\IdeaRefinery"
$SourceRoot = Join-Path $RefineryRepo ".agents\skills"
$TargetRoot = Join-Path $HOME ".copilot\skills"
$Skills = @("refine-idea", "implement-refine-idea")
$RunId = [Guid]::NewGuid().ToString("N")
$StagingRoot = Join-Path $TargetRoot ".idea-refinery-staging-$RunId"
$BackupRoot = Join-Path $TargetRoot ".idea-refinery-backup-$RunId"

function Get-TreeManifest([string]$Root) {
    Get-ChildItem -LiteralPath $Root -File -Recurse |
        ForEach-Object {
            [PSCustomObject]@{
                Path = $_.FullName.Substring($Root.Length).TrimStart("\")
                Hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            }
        } |
        Sort-Object Path
}

foreach ($Skill in $Skills) {
    $Source = Join-Path $SourceRoot $Skill
    if (-not (Test-Path -LiteralPath (Join-Path $Source "SKILL.md"))) {
        throw "Missing generated skill source: $Source"
    }
}

$ReplacementComplete = $false
$BackedUpSkills = @()
$InstalledSkills = @()
New-Item -ItemType Directory -Path $TargetRoot, $StagingRoot, $BackupRoot -Force -ErrorAction Stop | Out-Null

try {
    foreach ($Skill in $Skills) {
        $Source = Join-Path $SourceRoot $Skill
        $Staged = Join-Path $StagingRoot $Skill
        Copy-Item -LiteralPath $Source -Destination $Staged -Recurse -ErrorAction Stop
        if (Compare-Object (Get-TreeManifest $Source) (Get-TreeManifest $Staged) -Property Path, Hash) {
            throw "Staging verification failed for $Skill"
        }
    }

    try {
        foreach ($Skill in $Skills) {
            $Target = Join-Path $TargetRoot $Skill
            if (Test-Path -LiteralPath $Target) {
                Move-Item -LiteralPath $Target -Destination (Join-Path $BackupRoot $Skill) -ErrorAction Stop
                $BackedUpSkills += $Skill
            }
        }

        foreach ($Skill in $Skills) {
            Move-Item -LiteralPath (Join-Path $StagingRoot $Skill) -Destination (Join-Path $TargetRoot $Skill) -ErrorAction Stop
            $InstalledSkills += $Skill
        }
        $ReplacementComplete = $true
    }
    catch {
        foreach ($Skill in $InstalledSkills) {
            $Target = Join-Path $TargetRoot $Skill
            if (Test-Path -LiteralPath $Target) {
                Remove-Item -LiteralPath $Target -Recurse -Force -ErrorAction Stop
            }
        }
        foreach ($Skill in $BackedUpSkills) {
            $Target = Join-Path $TargetRoot $Skill
            $Backup = Join-Path $BackupRoot $Skill
            if (Test-Path -LiteralPath $Backup) {
                Move-Item -LiteralPath $Backup -Destination $Target -ErrorAction Stop
            }
        }
        throw
    }
}
finally {
    Remove-Item -LiteralPath $StagingRoot -Recurse -Force -ErrorAction SilentlyContinue
    $BackupEmpty = -not (Get-ChildItem -LiteralPath $BackupRoot -Force -ErrorAction SilentlyContinue)
    if ($ReplacementComplete -or $BackupEmpty) {
        Remove-Item -LiteralPath $BackupRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    else {
        Write-Error "Rollback failed; backup preserved at $BackupRoot"
    }
}
```

The same procedure installs and updates. Source preflight and staging occur before replacement, repeated runs produce exact copies, and a failed preflight leaves the current installation unchanged.

Verify the installed trees:

```powershell
$RefineryRepo = "C:\absolute\path\to\IdeaRefinery"
$SourceRoot = Join-Path $RefineryRepo ".agents\skills"
$TargetRoot = Join-Path $HOME ".copilot\skills"
$Skills = @("refine-idea", "implement-refine-idea")

function Get-TreeManifest([string]$Root) {
    Get-ChildItem -LiteralPath $Root -File -Recurse |
        ForEach-Object {
            [PSCustomObject]@{
                Path = $_.FullName.Substring($Root.Length).TrimStart("\")
                Hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            }
        } |
        Sort-Object Path
}

foreach ($Skill in $Skills) {
    $Source = Join-Path $SourceRoot $Skill
    $Target = Join-Path $TargetRoot $Skill
    if (Compare-Object (Get-TreeManifest $Source) (Get-TreeManifest $Target) -Property Path, Hash) {
        throw "Installed skill differs from generated source: $Skill"
    }
}
```

After both new copies verify successfully, remove any retired personal copies:

```powershell
$TargetRoot = Join-Path $HOME ".copilot\skills"
$LegacySkills = @("idea-refinery-full", "idea-refinery-implement")

foreach ($Skill in $LegacySkills) {
    $Target = Join-Path $TargetRoot $Skill
    if (Test-Path -LiteralPath $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force -ErrorAction Stop
    }
}
```

Remove only the two personal skills; missing folders are treated as already removed:

```powershell
$TargetRoot = Join-Path $HOME ".copilot\skills"
$Skills = @("refine-idea", "implement-refine-idea")

foreach ($Skill in $Skills) {
    $Target = Join-Path $TargetRoot $Skill
    if (Test-Path -LiteralPath $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }
}
```

Run `/skills reload` after install, update, or removal. Restart Copilot CLI if the active session still shows the old catalog.

### Personal installation on POSIX shells

Set the checkout and target locations:

```bash
set -eu
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
SOURCE_ROOT="$REFINERY_REPO/.agents/skills"
TARGET_ROOT="$HOME/.copilot/skills"
SKILLS="refine-idea implement-refine-idea"

for skill in $SKILLS; do
  test -f "$SOURCE_ROOT/$skill/SKILL.md" ||
    { echo "Missing generated skill source: $SOURCE_ROOT/$skill" >&2; exit 1; }
done

mkdir -p "$TARGET_ROOT"
STAGING_ROOT="$(mktemp -d "$TARGET_ROOT/.idea-refinery-staging.XXXXXX")"
BACKUP_ROOT="$(mktemp -d "$TARGET_ROOT/.idea-refinery-backup.XXXXXX")"

cleanup() {
  rm -rf -- "$STAGING_ROOT"
  if test ! -d "$BACKUP_ROOT" ||
     test -z "$(find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -print -quit)"; then
    rm -rf -- "$BACKUP_ROOT"
  fi
}
trap cleanup EXIT

for skill in $SKILLS; do
  cp -R "$SOURCE_ROOT/$skill" "$STAGING_ROOT/$skill"
  diff -qr "$SOURCE_ROOT/$skill" "$STAGING_ROOT/$skill"
done

backed_up=""
installed=""
transaction_ok=true

for skill in $SKILLS; do
  if test -e "$TARGET_ROOT/$skill"; then
    if mv "$TARGET_ROOT/$skill" "$BACKUP_ROOT/$skill"; then
      backed_up="$backed_up $skill"
    else
      transaction_ok=false
      break
    fi
  fi
done

if test "$transaction_ok" = true; then
  for skill in $SKILLS; do
    if mv "$STAGING_ROOT/$skill" "$TARGET_ROOT/$skill"; then
      installed="$installed $skill"
    else
      transaction_ok=false
      break
    fi
  done
fi

if test "$transaction_ok" != true; then
  rollback_ok=true
  for skill in $installed; do
    rm -rf -- "$TARGET_ROOT/$skill" || rollback_ok=false
  done
  for skill in $backed_up; do
    if test -e "$BACKUP_ROOT/$skill"; then
      mv "$BACKUP_ROOT/$skill" "$TARGET_ROOT/$skill" || rollback_ok=false
    fi
  done
  if test "$rollback_ok" != true; then
    echo "Rollback failed; backup preserved at $BACKUP_ROOT" >&2
    exit 1
  fi
  rm -rf -- "$BACKUP_ROOT"
  exit 1
fi

rm -rf -- "$BACKUP_ROOT"
```

Verify exact copies:

```bash
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
SOURCE_ROOT="$REFINERY_REPO/.agents/skills"
TARGET_ROOT="$HOME/.copilot/skills"
SKILLS="refine-idea implement-refine-idea"

for skill in $SKILLS; do
  diff -qr "$SOURCE_ROOT/$skill" "$TARGET_ROOT/$skill"
done
```

After both new copies verify successfully, remove any retired personal copies:

```bash
TARGET_ROOT="$HOME/.copilot/skills"
for skill in idea-refinery-full idea-refinery-implement; do
  rm -rf -- "$TARGET_ROOT/$skill"
done
```

Remove only the two personal skills; `rm -rf --` is scoped to these resolved literal paths and succeeds when a target is missing:

```bash
TARGET_ROOT="$HOME/.copilot/skills"
rm -rf -- \
  "$TARGET_ROOT/refine-idea" \
  "$TARGET_ROOT/implement-refine-idea"
```

Run `/skills reload` after install, update, or removal. Use `/skills` to inspect whether a project-local or personal copy is active.

## Codex

### Try without global installation

Start Codex in the target repository and load the checkout's canonical skill directly:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/refine-idea/SKILL.md. Refine this idea: <describe your idea>"
```

Do not rely on the `$refine-idea` name inside this session unless the skill is already registered globally. The explicit file instruction is the invocation.

The workflow should:

1. Inspect the target repository and project instructions.
2. Confirm the feature name and Spec Kit initialization state.
3. Ask before initialization or other required mutations.
4. Produce `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md` under the active feature directory.
5. Finish with a readiness verdict.

## Try `$implement-refine-idea` without global installation

Use a target repository whose active feature came from Idea Refinery and is ready:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/implement-refine-idea/SKILL.md. Implement the active ready Idea Refinery feature."
```

The feature must contain `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`. A ready summary does not override an open material decision or unresolved high-severity finding.

Expected implementation behavior:

- run protected-output and validator-prerequisite preflight before any mutable work, requesting authority at most once per normalized category;
- maintain and foreground-drive one completion checklist through tasks, reviews, corrections, promotion, state, convergence, hooks, and final evidence;
- validate checklists, hooks, readiness, and requirement-to-task coverage;
- record baseline/red/green/refactor evidence;
- parallelize only isolated, dependency-safe write sets, with at most three workers;
- obtain independent read-only review before promoting tasks and automatically correct objective in-scope findings;
- run up to two convergence implementation cycles;
- create or resume `implementation-state.md`;
- finish with `IMPLEMENTATION COMPLETE`, `BLOCKED ON DECISION`, or `BLOCKED ON VERIFICATION`.

Milestone updates report what completed and what comes next, but the controller does not yield while an authorized routine checklist item remains. A blocked result is reserved for missing authority, a material product/architecture decision, or an external-state verification failure after equivalent evidence has been considered.

For a fixture-based test, use [the implementation quickstart](specs/002-parallel-tdd-implementation/quickstart.md).

## Run both workflows in one session

Start with the direct-file full-refinement command. Once the workflow returns a ready verdict, send a separate message to authorize implementation:

```text
Read and follow /absolute/path/to/IdeaRefinery/implement-refine-idea/SKILL.md.
Implement the active ready Idea Refinery feature.
```

### Install both skills globally

```bash
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
mkdir -p ~/.codex/skills
ln -sfn "$REFINERY_REPO/refine-idea" \
  ~/.codex/skills/refine-idea
ln -sfn "$REFINERY_REPO/implement-refine-idea" \
  ~/.codex/skills/implement-refine-idea
```

Verify both new links before removing any retired links, then start a new Codex session. Updating the checkout updates the linked skills:

```bash
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
test "$(readlink "$HOME/.codex/skills/refine-idea")" = "$REFINERY_REPO/refine-idea"
test "$(readlink "$HOME/.codex/skills/implement-refine-idea")" = "$REFINERY_REPO/implement-refine-idea"
for skill in idea-refinery-full idea-refinery-implement; do
  rm -rf -- "$HOME/.codex/skills/$skill"
done
```

Remove only the two new links to uninstall.

## Validate the checkout

Regenerate portable Copilot/Hermes skill copies after changing canonical skill instructions, then confirm they match:

```bash
python3 tools/sync_host_skills.py
python3 tools/sync_host_skills.py --check
```

Run the deterministic support-runtime tests:

```bash
uv run --project refine-idea --extra dev pytest -q
```

```powershell
python tools\sync_host_skills.py --check
uv run --project refine-idea --extra dev python -m pytest tests\unit\test_host_skill_distribution.py
```

See [host compatibility](docs/host-compatibility.md) for the capability matrix, integration preservation rules, and generated-distribution ownership.

## Troubleshooting

### Copilot does not list the skills

Run `/skills reload`, inspect the catalog with `/skills`, and restart the session if needed. Confirm both `SKILL.md` files exist in the active project-local or personal location.

### A personal update appears ineffective

A project-local `.agents/skills` copy is authoritative for that repository. Inspect the active source with `/skills`, then update or remove the stale project-local copy.

### Full refinement says Spec Kit is missing

Install `specify`. If `.specify/` already exists, preserve it and inspect `.specify/integration.json` when available. Only when `.specify/` is absent should you review and approve:

```text
specify init --here --integration copilot
```

Never use `--force` as a routine recovery step.

### Implementation prerequisite detection fails

The implementation skill supports Spec Kit prerequisite scripts under `.specify/scripts/bash/` and `.specify/scripts/powershell/`. Repair or reinitialize the script distribution without overwriting an existing integration.

### Implementation requests authority or reports an unavailable validator

The request should name one normalized protected output path or validator prerequisite category, the smallest authority needed, and the affected completion-checklist item. Granting it lets the same invocation continue through routine gates; the controller records the token and must not repeat that category on resume. If the exact validator is unavailable, it records equivalent evidence when available; only the absence of equivalent evidence is an external-state verification blocker.

### Preferred Superpowers skills are unavailable

This changes composition, not required behavior. The workflow records `composition: local-fallback` and applies the same evidence gates locally.

## Related documentation

- [Project overview](README.md)
- [Host compatibility](docs/host-compatibility.md)
- [Repository structure](RepoStructure.md)
- [Full refinement architecture](refine-idea/ARCHITECTURE.md)
- [Implementation architecture](implement-refine-idea/ARCHITECTURE.md)
