# Feature Specification: Cross-Host Idea Refinery Skills

**Feature Branch**: `003-copilot-hermes-skills`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Make the repository's complete Idea Refinery skills workable in GitHub Copilot and Hermes, and update repository setup documentation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run full refinement in any supported host (Priority: P1)

A product or engineering user invokes the full Idea Refinery workflow from Codex, GitHub Copilot, or Hermes and receives the same staged, artifact-backed refinement process and readiness verdict.

**Why this priority**: The refinement workflow is the product's primary entry point; a host-specific shortcut would undermine its decision, review, and readiness guarantees.

**Independent Test**: Inspect each host's discoverable full-skill entrypoint and verify that it preserves explicit invocation, user approval before mutations, the required artifacts, independent review, clarification, analysis, bounded repair, and a single readiness verdict.

**Acceptance Scenarios**:

1. **Given** a user opens a repository with the Copilot distribution installed, **When** they invoke the full skill, **Then** the host can discover the skill and receives instructions for the complete refinement pipeline.
2. **Given** a user installs the Hermes distribution, **When** they invoke the full skill, **Then** Hermes can discover the skill and receives instructions for the complete refinement pipeline.
3. **Given** a required host capability or optional component skill is absent, **When** the full skill reaches that stage, **Then** it applies the documented equivalent local contract or records a degraded/blocked result without claiming the unavailable capability ran.

---

### User Story 2 - Implement a ready handoff in any supported host (Priority: P1)

A user separately invokes the implementation workflow after a ready refinement handoff and receives the same authority boundary, task execution gates, TDD evidence, independent review, convergence, and completion verdict regardless of host.

**Why this priority**: The two-skill separation is a deliberate safety boundary; portability is incomplete if only refinement works outside Codex.

**Independent Test**: Inspect each host's implementation entrypoint and confirm it requires an Idea Refinery ready handoff, preserves explicit invocation, and specifies safe sequential fallback when isolated parallel work is unavailable.

**Acceptance Scenarios**:

1. **Given** a ready Idea Refinery feature, **When** a supported host invokes the implementation skill, **Then** it receives the full entry, scheduling, evidence, review, convergence, and terminal-verdict contract.
2. **Given** a host cannot enforce parallel worker isolation, **When** the skill executes implementation tasks, **Then** it requires controller-applied patches or sequential execution rather than unsafe concurrent edits.
3. **Given** a user has not invoked the implementation skill, **When** the refinement workflow reaches readiness, **Then** it does not edit application code and directs the user to make a separate invocation.

---

### User Story 3 - Install and validate the correct host distribution (Priority: P2)

A maintainer can follow repository documentation to select, install, update, remove, and validate the Codex, Copilot, or Hermes distribution without confusing host-specific locations or guarantees.

**Why this priority**: Correct installation determines whether users actually receive the skills and prevents misleading claims about host support.

**Independent Test**: Follow each documented installation route from a clean checkout and verify the stated skill locations, invocation form, Spec Kit integration choice, and validation command are internally consistent.

**Acceptance Scenarios**:

1. **Given** a maintainer reads the project README, **When** they choose a host, **Then** they can identify the available skills, their authority boundary, and a link to the host-specific setup instructions.
2. **Given** a target repository lacks Spec Kit, **When** a supported host initializes it, **Then** documentation identifies the appropriate integration or generic fallback and retains the explicit confirmation requirement.
3. **Given** a host's installation changes, **When** maintainers update the canonical workflow, **Then** automated checks detect drift in distributed host entrypoints and supporting documentation references.

### Edge Cases

- What happens when a host can discover an entrypoint but cannot provide a named component skill? The entrypoint must use only the documented equivalent contract and record the fallback.
- What happens when a host cannot create isolated workers? The implementation workflow must run sequentially or receive proposed patches for controller application.
- What happens when a target repository is already initialized for another Spec Kit integration? The workflow must preserve that integration, explain the compatibility implications, and not overwrite it without approval.
- What happens when a distributed entrypoint cannot locate its canonical references? Validation must fail rather than presenting a partial workflow as complete.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST provide discoverable, explicit-only full-refinement and implementation skill entrypoints for GitHub Copilot and Hermes in their supported project or install locations.
- **FR-002**: Each host entrypoint MUST preserve the complete behavior of its corresponding Idea Refinery workflow, including all authorization, artifact, review, clarification, analysis, repair, readiness, TDD, review, convergence, and final-verdict gates applicable to that workflow.
- **FR-003**: Each host entrypoint MUST identify host capability discovery and require an equivalent local contract, a safe sequential mode, or an explicit degraded/blocked outcome when a preferred component or isolation mechanism is unavailable.
- **FR-004**: The full-refinement workflow MUST remain unable to make application-code changes and MUST require a separate explicit implementation invocation after a ready handoff.
- **FR-005**: The implementation workflow MUST retain controller-owned coordination artifacts and prohibit unsafe concurrent edits when host-enforced isolation is unavailable.
- **FR-006**: Repository documentation MUST describe host-specific prerequisites, discovery/install locations, invocation methods, update/removal steps, Spec Kit integration guidance, limitations, and validation methods for Codex, GitHub Copilot, and Hermes.
- **FR-007**: Repository documentation MUST describe one canonical workflow source and how each host distribution stays synchronized with it.
- **FR-008**: The project MUST validate distributed skill entrypoints and their reference paths so a release cannot silently ship incomplete or divergent host instructions.
- **FR-009**: Existing Codex discovery, setup, behavior, and deterministic-runtime validation MUST remain supported.
- **FR-010**: The project MUST provide a host capability matrix that distinguishes skill discovery from optional component availability and states the allowed fallback or blocked outcome for each workflow gate.
- **FR-011**: Host distributions MUST be deterministically generated from canonical skill sources, and validation MUST fail when a generated skill body or its required reference paths drift from the canonical source.
- **FR-012**: Setup MUST detect and preserve an existing target repository Spec Kit integration; it MUST document Copilot initialization separately and Hermes's generic integration fallback without overwriting target configuration without approval.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer can identify and install both skills for any one supported host using one documented section and no undocumented path assumptions.
- **SC-002**: All six distributed skill entrypoints (two workflows across three hosts) pass structural and content-parity validation in the repository test suite.
- **SC-003**: Every documented host setup path names the corresponding invocation form, installation location, and Spec Kit integration/fallback without contradiction.
- **SC-004**: A reviewer can trace every portability requirement to at least one implementation task and a validation target before implementation begins.
- **SC-005**: The published capability matrix accounts for every required workflow gate and identifies a safe fallback or blocked result for each host.

## Assumptions

- GitHub Copilot supports repository agent skills with standard `SKILL.md` frontmatter and GitHub-recognized skill directories.
- Hermes supports standard `SKILL.md` skills and can load a repository's skill directory when the user configures it as an external source or installs the skill into its skill home.
- Host-specific component integrations may differ, but equivalent local contracts can preserve the workflow's required safety and evidence gates.
- The existing Codex skill folders remain the canonical behavior source; host entrypoints may be generated or thin wrappers only when parity can be validated.
- The feature excludes publishing, registry submission, code-hosting automation, or changes to the deterministic runtime unless validation requires a narrowly scoped addition.
