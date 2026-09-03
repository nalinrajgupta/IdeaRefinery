# Host compatibility

Idea Refinery ships the same full refinement and implementation workflows for Codex, GitHub Copilot, and Hermes. The canonical sources are `idea-refinery-full/` and `idea-refinery-implement/`; run `python3 tools/sync_host_skills.py` to regenerate the portable `.agents/skills/` distribution. Each generated folder bundles the deterministic runtime it needs (`pyproject.toml`, `src/`, `defaults/`, and `schemas/` for the full workflow), so a copied installation runs `uv run --project <copied-skill-directory> idea-refinery <command>` without a canonical checkout.

| Host | Discovery / install | Invocation | Spec Kit setup |
| --- | --- | --- | --- |
| Codex | Symlink canonical folders into `~/.codex/skills/` | `$idea-refinery-full`, then `$idea-refinery-implement` | `specify init --here --integration codex --integration-options="--skills"` |
| GitHub Copilot | Commit `.agents/skills/idea-refinery-*` to the project, or copy both generated folders to `~/.copilot/skills/` | `/idea-refinery-full`, then `/idea-refinery-implement` | `specify init --here --integration copilot` |
| Hermes | Configure `.agents/skills/` as an external skill source, or copy each generated folder to `~/.hermes/skills/` | Invoke the matching slash skill | Preserve an existing integration; otherwise use `specify init --here --integration generic --integration-options="--commands-dir .agents/commands/"` |

Complete failure-safe personal installation, update, removal, refresh, and precedence commands are in the [setup guide](../setup.md).

## PowerShell

On Windows, inspect an existing integration without changing it:

```powershell
Test-Path -LiteralPath ".specify"
if (Test-Path -LiteralPath ".specify\integration.json") {
    Get-Content -LiteralPath ".specify\integration.json"
}
specify check
```

## POSIX shell

On POSIX-compatible systems:

```bash
test -d .specify && echo "Spec Kit already initialized"
test -f .specify/integration.json && sed -n '1,160p' .specify/integration.json
specify check
```

## Detect before initialization

If `.specify/` already exists, report its configured integration and preserve it. Do not overwrite or reinitialize it. If it is absent, explain the host-appropriate initialization command, the files it adds, and obtain explicit approval immediately before running it. Never use `--force` without the user's explicit approval.

## Capability and fallback rules

| Workflow gate | Codex | GitHub Copilot | Hermes |
| --- | --- | --- | --- |
| Skill discovery | Registered global skill | `.agents/skills` project skill | External source or `~/.hermes/skills` copy |
| Component skill | Use when available; otherwise local fallback | Use when available; otherwise local fallback | Use when available; otherwise local fallback |
| Independent review | Native delegation or sequential independent reviewer | Native delegation or sequential independent reviewer | Native delegation or sequential independent reviewer |
| Isolated implementation writes | Enforced boundary or sequential execution | Enforced boundary or sequential execution | Enforced boundary or sequential execution |
| Missing equivalent evidence | Block or degrade; never claim success | Block or degrade; never claim success | Block or degrade; never claim success |

Discovery of a skill does not guarantee that a host supplies every optional component. Each workflow inspects available skills, delegation, command support, and isolated write boundaries before its stages. A missing preferred component uses the documented equivalent local contract and records `composition: local-fallback`; it is never claimed as executed. When isolation is unavailable, implementation uses controller-applied patches or sequential execution. If equivalent evidence cannot be produced, the workflow blocks or returns a degraded verdict.

## Update, remove, and validate

Regenerate checked-in project skills after canonical changes. PowerShell:

```powershell
python tools\sync_host_skills.py
python tools\sync_host_skills.py --check
```

POSIX shell:

```bash
python3 tools/sync_host_skills.py
python3 tools/sync_host_skills.py --check
```

For copied Copilot or Hermes installs, replace each installed `idea-refinery-*` folder with its newly generated counterpart only after both sources validate. The [setup guide](../setup.md) provides failure-safe PowerShell and POSIX procedures. `tools/sync_host_skills.py --check` validates only the checked-in distribution. To remove an installation, delete only the copied or linked `idea-refinery-full` and `idea-refinery-implement` folders, never the repository or target feature artifacts.
