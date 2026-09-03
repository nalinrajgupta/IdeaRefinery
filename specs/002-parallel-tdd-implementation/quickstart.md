# Quickstart: Validate the Implementation Skill

## Structural validation

From the repository root:

```bash
python3 /absolute/path/to/skill-creator/scripts/quick_validate.py idea-refinery-implement
```

Expected: the validator reports a valid skill with no scaffold placeholders.

## Manual routing scenario

Create or use a temporary Spec Kit fixture whose `tasks.md` contains:

- one task limited to `module-a/`;
- one independent task limited to `module-b/`;
- one task that also changes a root dependency lockfile;
- one task blocked by an unresolved material decision.

Invoke `$idea-refinery-implement` in that fixture. Expected behavior:

1. The two disjoint module tasks may share a wave, capped at three workers.
2. The lockfile task is serialized despite any `[P]` marker.
3. The blocked task is not dispatched.
4. Behavior changes show valid baseline, red, green, and broader evidence.
5. A different read-only agent reviews the wave before the controller updates task checkboxes.
6. Missing Superpowers components are recorded as local fallback, not claimed as invoked.
7. Completion is withheld until convergence and fresh project-level verification pass.
