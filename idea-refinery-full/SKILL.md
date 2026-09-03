---
name: idea-refinery-full
description: Orchestrate Superpowers brainstorming, gstack CEO and engineering reviews, and Spec Kit clarification and analysis to turn an idea into implementation-ready spec, plan, and tasks. Use only when explicitly invoked as $idea-refinery-full.
---

# Idea Refinery Full

Use this explicit-only workflow when the user wants the complete, artifact-backed refinement pipeline, not a lightweight in-chat spec. It uses the installed Superpowers, gstack, and Spec Kit skills as distinct stages.

The final deliverable is a Spec Kit feature directory containing `spec.md`, `plan.md`, `tasks.md`, and `refinery-state.md`, plus a concise refinement report. This workflow writes files and may create a feature branch. Do not start those mutations until the user approves the target repository and initialization plan.

## Hybrid runtime and model profile

Full mode is hybrid: this skill owns the active session’s model-roster discovery, delegation, approvals, and single-writer orchestration; the bundled Python package under `src/idea_refinery/` owns deterministic configuration, contracts, persistence, coverage bookkeeping, repair checkpoints, and replay evaluation. The package never calls provider APIs, external model CLIs, or credential stores.

With no overrides, select the first available candidate in each ordered list: CEO `gpt-5.5` → `gpt-5.6-sol` → `gpt-5.6-terra` (high); Product `gpt-5.6-terra` → `gpt-5.6-sol` → `gpt-5.6-luna` (high); Architect `gpt-5.6-sol` → `gpt-5.5` → `gpt-5.6-terra` (high); Eval `gpt-5.6-luna` → `gpt-5.6-terra` → `gpt-5.6-sol` (medium); Baseline `gpt-5.4` (medium).

Users may supply a versioned `overrides.roles` block. Precedence is invocation override, repository `.idea-refinery/config.yaml`, then bundled defaults. Capture and persist the complete resolved assignment before dispatch and revalidate it at dispatch. An explicit unavailable override fails unless it supplies its own fallbacks. If an effort is unsupported, select the highest supported effort not exceeding it and record the adjustment.

The deterministic adapter can be exercised with `uv run --project idea-refinery-full idea-refinery <command>`. Its roster input is a controller-captured JSON snapshot, not a provider-discovery mechanism.

## Required setup

1. Confirm the target repository and feature name. Inspect the repository and project instructions read-only first.
2. Check for `.specify/` and `specify`.
3. If the repository is not a Spec Kit project, resolve the current host and explain that the full workflow needs the matching command from `docs/host-compatibility.md`: Codex uses `specify init --here --integration codex --integration-options="--skills"`; GitHub Copilot uses `specify init --here --integration copilot`; Hermes preserves an existing integration or otherwise uses `specify init --here --integration generic --integration-options="--commands-dir .agents/commands/"`. State the files/directories it will add and request explicit confirmation immediately before running it. Never add `--force` unless the user expressly approves merging Spec Kit files into a nonempty project.
4. If a Spec Kit project already exists, identify its active feature directory before proceeding.
5. Create `refinery-state.md` in the active feature directory from [the state template](references/refinery-state-template.md), or load and preserve the existing state file. This is the human controller summary; the feature-local `runs/<run-id>/` manifest and immutable objects are authoritative for resume.

## Host capability contract

Before each stage, inspect the current host for skill discovery, component skills, delegation, isolated write boundaries, and command support. Use a native capability only when it satisfies the stage gate. When a preferred component is unavailable, apply its equivalent local contract and record `composition: local-fallback`; never claim it ran. If no equivalent evidence can be produced, stop with a blocked or degraded verdict. Reviewers may use sequential execution when delegation is unavailable; they must remain independent. This workflow never changes application code.

## Orchestration contract

Follow the stages in [the orchestration contract](references/orchestration-contract.md) in order. Treat the outputs of each stage as artifacts, not informal conversation. `refinery-state.md` is the source of truth for the decision queue, question registry, and audit ledger. Preserve an audit ledger that maps every material finding to one of: `accepted`, `rejected — rationale`, `deferred — trigger`, or `decision-needed`.

When loading a named skill, read its complete `SKILL.md` and follow it except where this skill explicitly supplies a narrower stage boundary. The user explicitly requested this pipeline, so its stage order overrides a component skill's normal terminal transition.

### State protocol: do not re-ask settled questions

Before invoking any component skill or local reviewer:

1. Load `refinery-state.md` and prepare a stage brief containing all settled decisions, accepted answers, open decisions, and unresolved review findings relevant to that stage.
2. Give the component skill the stage brief and instruct it to return findings only until the controller determines a question is genuinely needed.
3. Compare every proposed question against the state file by its decision, behavior, actor, constraint, or acceptance criterion—not merely exact wording.

If the same underlying question is already `answered` or `decided`, do not ask it again. Use the existing answer in the reviewer or downstream artifact. A question may be reopened only when new evidence materially changes the trade-off; record the evidence, link the original `D-` or `Q-` ID, and explain why the old answer no longer applies before asking the user.

After every user answer, material review finding, resolution, or reopened decision, update `refinery-state.md` first, then update the relevant Spec Kit artifact. Keep IDs stable: `D-` for decisions, `Q-` for questions, and `R-` for review findings.

### Stage 1 — Superpowers brainstorm

Resolve `$brainstorming` using the current host's documented skill discovery mechanism (see the Host capability contract) and load its complete `SKILL.md` for discovery. Classify the work, inspect context, ask one high-value question at a time, present 2–3 approaches with trade-offs and a recommendation, and obtain user approval for the selected design.

For this full workflow, stop Superpowers after the approved design and its self-review. Do **not** transition to its normal implementation-planning terminal step: the remaining stages below are the user-requested continuation. Create Spec Kit's initial `spec.md` through `$speckit-specify` after user approval.

### Stage 2 — Spec v1 and independent gstack review

Create Spec v1 with `$speckit-specify`. Update `refinery-state.md` with its initial assumptions, decisions, and unanswered questions. Then obtain three independent review artifacts:

- **CEO review:** load `$plan-ceo-review`; ask it to identify value, positioning, scope, and strategic-risk gaps in Spec v1. Return review findings only, not a replacement plan.
- **Product review:** perform an independent product/user-journey review using the required finding format. This is local because the installed gstack set has no standalone product-review skill.
- **Architect review:** load `$plan-eng-review`; ask it to identify feasibility, interface, data, reliability, security, operational, and test-strategy gaps in Spec v1. Return review findings only, not a replacement plan.

Do not let reviewers read one another's findings before they report. If delegation is available and the user explicitly asks for parallel review, run the three reviews in parallel; otherwise run them sequentially while preserving independence.

Each material finding needs an ID, reviewer, severity, affected artifact/section, evidence, minimal proposed change, and whether it needs a human decision.

### Stage 3 — gstack-style synthesis and Spec v2

Synthesize the review artifacts into Spec v2. Resolve every material finding in the audit ledger; do not silently drop critiques. Ask the user only for decisions that change product priority, risk tolerance, or strategic direction and that are not already settled in `refinery-state.md`. Update the Spec Kit spec through its appropriate refinement command or an explicitly approved edit.

### Stage 4 — Spec Kit clarification and consistency analysis

1. Load and run `$speckit-clarify` against Spec v2. Give it the state brief first; it may ask up to five high-impact clarification questions that are not already answered in `refinery-state.md`, then writes accepted answers into the active `spec.md`.
2. Load and run `$speckit-plan`, then `$speckit-tasks`, to create the implementation plan and tasks that `$speckit-analyze` requires.
3. Load and run `$speckit-analyze`. Its report is read-only and must check coverage, ambiguity, duplication, terminology, constitution alignment, and task ordering across `spec.md`, `plan.md`, and `tasks.md`.

If clarification or analysis reports blocker, critical, or high-severity gaps, return to Stage 3 with only those gaps. Regenerate only artifacts invalidated by the dependency graph, then re-run the relevant checks. Before analysis, obtain one explicit authorization for at most two narrowly scoped repair cycles. Stage repairs from a checkpoint and promote atomically only when relevant checks pass and risk does not increase. Stop on recurring roots, new high-severity contradictions, or excluded decisions; do not loop on low-value wording.

## Coverage, parallelism, and evals

Derive stable coverage IDs before fan-out. Each reviewer receives only its immutable brief and assigned IDs, and must attest to every assigned item even when it found no issue. Run CEO, Product, and Architect concurrently up to three slots; otherwise queue the same frozen briefs. The controller sorts completed envelopes deterministically, canonicalizes duplicate root findings, and may issue one targeted follow-up for an uncovered high-risk item.

Blocking quality gates are schema/semantic contracts, deterministic tests, approved replay fixtures, and requirement-to-task traceability. Live three-model versus single-model benchmarks and model-judge scores are non-blocking until calibrated. A failed required role blocks readiness unless the user records a waiver; then report `READY FOR IMPLEMENTATION — DEGRADED` with the missing perspective, affected coverage, owner, and rationale.

### Stage 5 — final handoff

Deliver the required report and verify the final readiness gate in the orchestration contract. Do not implement application code in this workflow.

When the verdict is ready, identify `$idea-refinery-implement` as the separate opt-in implementation workflow if it is available. Do not invoke it automatically; its application-code mutation authority requires a separate user request.

## Safety and scope

- Initialization, spec generation, planning, and task generation create or modify repository files. Announce the exact operation before it happens and obtain any confirmation required by the component skill or the user’s environment.
- `$speckit-analyze` is read-only. Do not turn its recommendations into edits without approval.
- Never create issues, commit, push, deploy, or invoke implementation skills unless the user separately asks.
- Preserve user-approved decisions across iterations. Reopen them only with new evidence and an explicit explanation.
