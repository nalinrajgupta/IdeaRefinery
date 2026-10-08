# GitHub Copilot Instructions

## Pull request reviews

When reviewing a pull request in this repository:

- Read the pull request title and description, the complete diff, and enough surrounding code or documentation to understand each change.
- Compare the implementation with the applicable `spec.md`, `plan.md`, `tasks.md`, architecture documents, schemas, and contracts. Treat those artifacts as requirements, not background reading.
- Report only issues introduced by the pull request. Do not report pre-existing problems unless the change makes them materially worse.
- Prioritize correctness, security, data integrity, compatibility, state recovery, concurrency, and missing test coverage over formatting or subjective style.
- For every finding, identify the affected path and line, explain the concrete failure mode and impact, and suggest the smallest safe correction.
- Distinguish confirmed defects from questions or uncertain risks. Do not claim that tests, commands, or workflows passed unless the available evidence proves it.
- Avoid duplicate comments and low-value style observations unless they violate an explicit repository rule or obscure a defect.
- Check error paths and boundary cases, including missing files, malformed configuration, partial runs, stale state, interrupted execution, and unsupported host capabilities.

## Change-set gate

Before beginning the normal review, classify the complete pull request diff against the target branch:

- A specification change is a change under `specs/**` that modifies approved requirements, scope, architecture, contracts, or planned work. Implementation bookkeeping updates that only record task completion, run state, or validation evidence are not specification changes.
- An implementation change is a behavior-changing change to source code, tests, workflows, tools, or generated runtime or skill files. This includes changes under `refine-idea/src/**`, `refine-idea/tests/**`, `implement-refine-idea/**`, `tests/**`, `tools/**`, `.github/workflows/**`, or `.agents/skills/**`. Documentation or configuration outside `specs/**` counts only when it changes executable workflow or product behavior.
- If the pull request contains both specification and implementation changes, raise one blocking finding that identifies representative paths from both groups and requires the work to be split into separate pull requests. Do not approve the pull request or describe it as ready to merge. This is a review policy finding; repository rules, not this instruction, determine whether GitHub technically permits the merge.
- If the pull request contains specification changes and no implementation changes, review every requested iteration holistically. Compare the complete affected feature package at the pull request head with the target branch, not only with the previous iteration or latest pushed diff.
- For a specification-only review, read all relevant `spec.md`, `plan.md`, `tasks.md`, `refinery-state.md`, `implementation-state.md`, `research.md`, `data-model.md`, `quickstart.md`, contracts, and checklists together, including unchanged files needed to evaluate the change. Check internal consistency, requirement-to-task traceability, scope drift, unresolved decisions, contradictory acceptance criteria, and stale downstream artifacts.

## Review consistency across iterations

On every requested review or re-review:

- Treat prior review findings and the target-branch requirements as continuity constraints when that context is available. Re-evaluate the whole affected specification package, but comment only on defects that remain actionable in the current pull request head.
- Do not repeat a prior finding that the current iteration resolves. Do not reopen a resolved finding unless the new iteration reintroduces the defect or creates concrete contradictory evidence.
- Do not recommend an alternative that conflicts with a still-valid earlier recommendation. Anchor recommendations in explicit repository requirements, recorded decisions, contracts, or demonstrable failure modes rather than interchangeable stylistic preferences.
- If new evidence requires changing an earlier recommendation, explicitly state that the new finding supersedes the earlier one, identify the changed evidence, and provide one unambiguous current action. Never leave the author responsible for satisfying mutually exclusive recommendations.
- Consolidate overlapping findings into one comment and distinguish persistent blockers from newly introduced issues. If repository artifacts themselves conflict, report the conflict as a decision blocker instead of alternating between possible resolutions across iterations.

## Repository invariants

Verify that every pull request preserves these boundaries:

- `refine-idea` may refine requirements and design artifacts but must not implement application code.
- `implement-refine-idea` may implement only an approved, ready handoff and must not silently change product scope or architecture.
- The deterministic package under `refine-idea/src/idea_refinery` must not discover or invoke models, read provider credentials, or call external model CLIs.
- Review workers are read-only. Shared task, run, and state artifacts remain controller-owned.
- Existing Spec Kit configuration must be preserved. Initialization or forced replacement must require explicit approval.
- Requirement identifiers, decisions, findings, stage history, and audit evidence must remain traceable across `spec.md`, `plan.md`, `tasks.md`, `refinery-state.md`, and `implementation-state.md`.
- Canonical skill sources live in `refine-idea` and `implement-refine-idea`. Generated copies under `.agents/skills/idea-refinery-*` must not be edited directly and must remain synchronized.
- Changes to schemas or persisted formats must account for existing artifacts and include compatibility, migration, or explicit rejection behavior.
- Commits, pushes, pull requests, merges, deployments, destructive cleanup, and repository-structure changes require separate authorization.

## Validation expectations

- Changes to the deterministic runtime should include focused tests and pass `uv run --project refine-idea --extra dev pytest -q`.
- Changes affecting generated host skills should pass `python3 tools/sync_host_skills.py --check`.
- Documentation and examples must agree on host-specific invocation: Copilot uses slash-prefixed skills, while other hosts may use different forms.
- Confirm that changed local Markdown links, referenced files, workflow paths, and commands exist and remain accurate.
- Flag skipped or weakened verification, tests that cannot fail for the reported regression, and assertions of success based only on implementation intent.
