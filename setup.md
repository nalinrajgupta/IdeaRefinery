# Setup and Tryout

This repository contains the `idea-refinery-full` Codex skill. Choose the setup that matches how broadly you want to test it.

## Try the updated skill in one session

This path does not change your global Codex skill installation. From this checkout, start a session rooted at the repository and tell Codex to load the local skill file directly:

```bash
cd /path/to/IdeaRefinery-worktrees/v2
codex --cd "$PWD" \
  "Use the updated skill instructions in $PWD/idea-refinery-full/SKILL.md. Run the full workflow for: <describe your idea>"
```

Inside that session, invoke the workflow with:

```text
$idea-refinery-full <describe your idea>
```

Use this mode to test changes in the checkout without replacing the skill used by other sessions. The workflow’s deterministic support runtime can be checked independently with:

```bash
uv run --directory idea-refinery-full --project . pytest
```

## Install for all sessions

Create (or update) the standard Codex skills symlink so every new session can discover this checkout:

```bash
mkdir -p ~/.codex/skills
ln -sfn "/path/to/IdeaRefinery-worktrees/v2/idea-refinery-full" \
  ~/.codex/skills/idea-refinery-full
```

Verify the link and start a new Codex session:

```bash
readlink ~/.codex/skills/idea-refinery-full
codex --cd /path/to/your/project
```

Then run:

```text
$idea-refinery-full <describe your idea>
```

Because the link points at the checkout, edits to `idea-refinery-full/SKILL.md`, its references, or its deterministic runtime are picked up by later sessions. Existing sessions may need to be restarted to reload skill instructions.

## Updating or removing the global install

To point the global installation at another checkout, rerun the `ln -sfn` command with the new absolute path. To remove only this skill’s global registration, delete the symlink:

```bash
rm ~/.codex/skills/idea-refinery-full
```

This removes the registration link, not the repository contents.
