# Setup and Tryout

This guide covers GitHub Copilot and Codex installation, invocation, update, removal, and troubleshooting. Hermes users should start with [host compatibility](docs/host-compatibility.md).

## Choose a setup mode

| Host | Mode | Best for | Installed location |
| --- | --- | --- | --- |
| GitHub Copilot | Repository-local skills | One project and checked-in team configuration | `.agents/skills/idea-refinery-*` |
| GitHub Copilot | Personal copied skills | Reuse across repositories | `~/.copilot/skills/idea-refinery-*` |
| Codex | Direct-file session | Testing one checkout or branch | No registration |
| Codex | Global symlink | Reuse across repositories | `~/.codex/skills/idea-refinery-*` |

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
.agents/skills/idea-refinery-full
.agents/skills/idea-refinery-implement
```

To install them into another project, copy both generated folders to that project's `.agents/skills` directory and commit them with the project if team-wide discovery is desired. Do not copy only `SKILL.md`; the full skill bundles its required runtime and references.

After adding or updating skills, start Copilot CLI in the target repository and run:

```text
/skills reload
```

Use `/skills` to inspect the loaded skills and their locations. When project-local and personal copies both exist, the project-local copy is authoritative for that repository; update or remove the stale project copy if a personal update appears ineffective.

Invoke refinement:

```text
/idea-refinery-full <idea>
```

After the workflow returns `READY FOR IMPLEMENTATION`, authorize implementation separately:

```text
/idea-refinery-implement
```

The generated descriptions retain dollar-prefixed explicit-invocation wording shared with other hosts. GitHub Copilot CLI commands use the slash-prefixed forms above.

### Personal installation on Windows PowerShell

Set the checkout path, then stage and verify both generated skills before replacing either personal target:

```powershell
$RefineryRepo = "C:\absolute\path\to\IdeaRefinery"
$SourceRoot = Join-Path $RefineryRepo ".agents\skills"
$TargetRoot = Join-Path $HOME ".copilot\skills"
$Skills = @("idea-refinery-full", "idea-refinery-implement")
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
$Skills = @("idea-refinery-full", "idea-refinery-implement")

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

Remove only the two personal skills; missing folders are treated as already removed:

```powershell
$TargetRoot = Join-Path $HOME ".copilot\skills"
$Skills = @("idea-refinery-full", "idea-refinery-implement")

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
SKILLS="idea-refinery-full idea-refinery-implement"

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
SKILLS="idea-refinery-full idea-refinery-implement"

for skill in $SKILLS; do
  diff -qr "$SOURCE_ROOT/$skill" "$TARGET_ROOT/$skill"
done
```

Remove only the two personal skills; `rm -rf --` is scoped to these resolved literal paths and succeeds when a target is missing:

```bash
TARGET_ROOT="$HOME/.copilot/skills"
rm -rf -- \
  "$TARGET_ROOT/idea-refinery-full" \
  "$TARGET_ROOT/idea-refinery-implement"
```

Run `/skills reload` after install, update, or removal. Use `/skills` to inspect whether a project-local or personal copy is active.

## Codex

### Try without global installation

Start Codex in the target repository and load the checkout's canonical skill directly:

```bash
codex --cd /absolute/path/to/target-repository \
  "Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-full/SKILL.md. Refine this idea: <describe your idea>"
```

After a ready handoff, authorize implementation in a separate message:

```text
Read and follow /absolute/path/to/IdeaRefinery/idea-refinery-implement/SKILL.md.
Implement the active ready Idea Refinery feature.
```

### Install both skills globally

```bash
REFINERY_REPO="/absolute/path/to/IdeaRefinery"
mkdir -p ~/.codex/skills
ln -sfn "$REFINERY_REPO/idea-refinery-full" \
  ~/.codex/skills/idea-refinery-full
ln -sfn "$REFINERY_REPO/idea-refinery-implement" \
  ~/.codex/skills/idea-refinery-implement
```

Verify both links with `readlink`, then start a new Codex session. Updating the checkout updates the linked skills. Remove only the two links to uninstall.

## Validate the checkout

```powershell
python tools\sync_host_skills.py --check
uv run --project idea-refinery-full --extra dev python -m pytest tests\unit\test_host_skill_distribution.py
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

### Preferred Superpowers skills are unavailable

This changes composition, not required behavior. The workflow records `composition: local-fallback` and applies the same evidence gates locally.

## Related documentation

- [Project overview](README.md)
- [Host compatibility](docs/host-compatibility.md)
- [Repository structure](RepoStructure.md)
- [Full refinement architecture](idea-refinery-full/ARCHITECTURE.md)
- [Implementation architecture](idea-refinery-implement/ARCHITECTURE.md)
