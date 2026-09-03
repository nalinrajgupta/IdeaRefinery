# Copilot Setup Contract

## README quick start

The Copilot quick start must:

1. Identify `.agents/skills/idea-refinery-full` and `.agents/skills/idea-refinery-implement` as repository-local skills.
2. Link to the personal installation lifecycle in `setup.md`.
3. Use `/idea-refinery-full <idea>` and `/idea-refinery-implement`.
4. Explain `/skills reload` or session restart after skill changes.
5. Name `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md` as refinement outputs.
6. Preserve the separate authorization boundary before implementation.

## Personal lifecycle

The setup guide must define:

- source preflight for both generated directories;
- staging and verification before replacement;
- exact replacement of only the two personal targets;
- repeatable install/update behavior;
- missing-safe removal;
- PowerShell and portable shell variants;
- active-copy and precedence troubleshooting;
- skill refresh after changes.

## Spec Kit configuration

- Existing `.specify` configuration is inspected and preserved.
- Uninitialized Copilot repositories use the Copilot integration route only after approval.
- Forced reinitialization is not a normal setup step.

## Compatibility disclosure

Copilot commands use slash invocation. The guide may mention the current dollar-prefixed wording in generated descriptions only as a known cross-host wording limitation, never as a Copilot command.

