# Feature Specification: First-Class GitHub Copilot Setup Documentation

**Feature Branch**: `005-copilot-setup-docs`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Update setup.md and README.md with instructions for using Idea Refinery with GitHub Copilot."

## Clarifications

### Session 2026-09-03

- Q: Which prerequisite script families must the implementation workflow support when selecting the active platform path? → A: Bash and PowerShell.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start Idea Refinery with GitHub Copilot (Priority: P1)

A GitHub Copilot user can begin from the project overview, understand the two-skill authority boundary, install or discover the skills, reload skill discovery when needed, and invoke the refinement workflow without relying on Codex-specific instructions.

**Why this priority**: A user who cannot find a complete Copilot path cannot use the product even though compatible skill artifacts already exist.

**Independent Test**: A reader unfamiliar with the repository can follow only the Copilot quick-start guidance in `README.md`, reach the appropriate detailed setup section, and successfully identify the installation location, reload action, and invocation sequence.

**Acceptance Scenarios**:

1. **Given** a Copilot user opens `README.md`, **When** they look for installation guidance, **Then** they see a first-class GitHub Copilot path rather than a Codex-only prerequisite and setup flow.
2. **Given** the repository-local skills are available, **When** the user follows the quick start, **Then** they can discover and invoke `idea-refinery-full` and understand that implementation requires a separate invocation.
3. **Given** the user installed personal skills after starting a session, **When** they follow the troubleshooting guidance, **Then** they are told how to reload or restart skill discovery.

---

### User Story 2 - Manage a Personal Copilot Installation (Priority: P1)

A GitHub Copilot CLI user can install the generated Idea Refinery skills in their personal Copilot skill directory, verify the copy, update it from a newer checkout, and remove only the installed skills.

**Why this priority**: Personal installation makes the workflows available across repositories, but incomplete lifecycle guidance risks stale copies or accidental deletion.

**Independent Test**: Starting with a clean personal skill directory, a reader can use the detailed setup guide to install both skills, verify their presence, update them, and remove them without changing the source checkout or unrelated skills.

**Acceptance Scenarios**:

1. **Given** a Windows user has cloned Idea Refinery, **When** they follow the personal installation steps, **Then** both generated skills are copied into the personal Copilot skills directory.
2. **Given** an existing personal installation, **When** the user follows the update steps, **Then** only the two Idea Refinery skill folders are replaced from the current generated distribution.
3. **Given** a user wants to uninstall Idea Refinery, **When** they follow the removal steps, **Then** only the two installed Idea Refinery folders are removed.
4. **Given** a non-Windows user reads the guide, **When** they need the equivalent personal installation, **Then** the guide provides a clear portable path or equivalent command pattern.

---

### User Story 3 - Preserve Project and Spec Kit Configuration (Priority: P2)

A maintainer can choose repository-local or personal Copilot discovery while preserving an existing Spec Kit integration and understanding where detailed cross-host compatibility rules live.

**Why this priority**: Setup guidance must not encourage reinitialization or overwrite a repository that is already configured for another supported host.

**Independent Test**: Review the instructions against a repository with an existing `.specify` configuration and confirm they direct the user to inspect and preserve it instead of reinitializing or forcing changes.

**Acceptance Scenarios**:

1. **Given** a repository already contains `.specify` configuration, **When** a Copilot user prepares Idea Refinery, **Then** the instructions preserve the existing integration.
2. **Given** a repository is not initialized for Spec Kit, **When** the user follows Copilot setup, **Then** the guide names the Copilot initialization route and retains the approval boundary before repository mutation.
3. **Given** a reader needs capability or fallback details, **When** they follow the documentation references, **Then** they reach the centralized host compatibility guide rather than conflicting duplicated explanations.

---

### User Story 4 - Complete Implementation Preflight on the Active Platform (Priority: P2)

A user who installed and initialized Idea Refinery on Windows or another supported environment can invoke the separate implementation workflow without failing solely because the workflow assumes a different family of Spec Kit scripts.

**Why this priority**: First-class Copilot setup is incomplete if refinement succeeds but the documented implementation handoff fails before validating the feature.

**Independent Test**: Prepare equivalent ready features with supported platform-script distributions and confirm that implementation preflight selects an available prerequisite route or reports a precise unsupported-configuration error.

**Acceptance Scenarios**:

1. **Given** a ready feature with a supported PowerShell prerequisite script, **When** implementation begins on Windows, **Then** preflight uses the available platform script rather than requiring a missing Bash script.
2. **Given** a ready feature with a supported shell prerequisite script, **When** implementation begins in a shell environment, **Then** existing shell behavior remains available.
3. **Given** no supported prerequisite script is present, **When** implementation begins, **Then** it stops with an actionable error that names the expected alternatives.

### Edge Cases

- A personal Copilot skill directory does not exist before installation.
- One Idea Refinery skill is installed but the other is missing or stale.
- A Copilot session was opened before the skill folders were added.
- Repository-local and personal copies both exist and may be from different revisions.
- Installation or update is run repeatedly against an already current target.
- One generated source folder is missing before an update begins.
- Removal is requested when one or both personal skill folders are already absent.
- The repository already uses a non-Copilot Spec Kit integration.
- Command examples must distinguish Windows PowerShell from shell syntax so readers do not copy commands for the wrong environment.
- A ready feature contains only one supported family of Spec Kit prerequisite scripts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `README.md` MUST identify GitHub Copilot as a first-class supported host in prerequisites, installation, invocation, and troubleshooting guidance.
- **FR-002**: `README.md` MUST provide a concise Copilot quick start that identifies repository-local discovery, personal installation availability, skill reload or session restart behavior, and the separate refinement and implementation invocations.
- **FR-003**: `setup.md` MUST provide complete GitHub Copilot project-local and personal installation paths for both Idea Refinery skills.
- **FR-004**: `setup.md` MUST provide Windows PowerShell commands for personal installation, verification, update, and removal.
- **FR-005**: `setup.md` MUST provide equivalent non-Windows guidance without obscuring the Windows path.
- **FR-006**: Installation and removal instructions MUST target only `idea-refinery-full` and `idea-refinery-implement` and MUST not delete the source repository, unrelated personal skills, or feature artifacts.
- **FR-007**: The documentation MUST explain when to use `/skills reload` or restart a Copilot session after installation or updates.
- **FR-008**: The documentation MUST show `/idea-refinery-full <idea>` and `/idea-refinery-implement` as the Copilot invocation forms and MUST preserve the separately authorized implementation boundary.
- **FR-009**: The documentation MUST explain how to detect and preserve an existing Spec Kit integration and MUST not recommend forced reinitialization.
- **FR-010**: The documentation MUST direct users without Spec Kit configuration to the Copilot-specific initialization route and retain explicit approval before repository mutation.
- **FR-011**: The two documents MUST link to `docs/host-compatibility.md` for the canonical distribution, capability fallback, and cross-host compatibility details.
- **FR-012**: Existing Codex and Hermes instructions MUST remain available and must not be contradicted by the new Copilot guidance.
- **FR-013**: Command examples in `README.md`, `setup.md`, and `docs/host-compatibility.md` MUST clearly label host and shell assumptions so commands are not presented as universally interchangeable.
- **FR-014**: Repository validation MUST detect removal of the required first-class Copilot guidance from `README.md` or `setup.md`.
- **FR-015**: Personal installation and update instructions MUST validate both generated source folders before replacing either installed folder, MUST produce the same result when repeated, and MUST leave the existing installation unchanged when preflight fails.
- **FR-016**: Personal removal instructions MUST succeed when either target folder is already absent and MUST remain narrowly scoped to the two Idea Refinery folders.
- **FR-017**: Troubleshooting MUST explain repository-local versus personal skill precedence and MUST show how to inspect the active location of both skills after reload.
- **FR-018**: The documentation MUST disclose that current generated descriptions use dollar-prefixed explicit-invocation wording while Copilot users invoke the slash-prefixed skill names, without presenting the dollar-prefixed form as a Copilot command.
- **FR-019**: The implementation workflow MUST select an available Bash or PowerShell Spec Kit prerequisite script for the active environment instead of unconditionally requiring one script family.
- **FR-020**: If neither a Bash nor PowerShell prerequisite script is available, implementation preflight MUST stop with an actionable error naming both supported alternatives.
- **FR-021**: Validation workflow path filters MUST include `README.md` and `setup.md` so changes to either file run the relevant documentation checks.
- **FR-022**: The feature MUST define automated assertions for each content-verifiable requirement and an explicit manual review for timed discovery, command walkthrough, and readability outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new Copilot user can identify a valid installation path and the first refinement invocation from `README.md` in under three minutes.
- **SC-002**: A Windows user can complete install, verify, update, and removal using one contiguous Copilot section in `setup.md` without consulting undocumented commands.
- **SC-003**: Every Copilot setup route names both skills, the skill refresh action, the separate invocation boundary, and the Spec Kit preservation rule.
- **SC-004**: Documentation review finds zero contradictory Copilot installation locations or invocation forms across `README.md`, `setup.md`, and `docs/host-compatibility.md`.
- **SC-005**: Automated documentation checks cover every functional requirement that can be validated from repository content, with non-automatable usability criteria assigned an explicit manual review step.
- **SC-006**: The Copilot quick start states all four expected refinement artifacts, the readiness verdict, and the requirement for a separate implementation invocation.
- **SC-007**: Repeating the documented personal install or update procedure produces an exact copy of both generated source folders without nested or stale files.
- **SC-008**: Supported Windows and shell-based ready features both complete implementation prerequisite selection, while a feature with no supported script receives one actionable failure message.

## Assumptions

- GitHub Copilot CLI continues to discover repository skills under `.agents/skills` and personal skills under the user's `.copilot/skills` directory.
- The generated `.agents/skills/idea-refinery-*` folders remain the portable source for Copilot installations.
- The primary requested environment is Windows PowerShell, based on the current installation session; portable shell guidance remains necessary for other users.
- The existing cross-host distribution design and capability fallback rules from feature 003 remain authoritative and are not being redesigned.
- Per D-004, canonical skill descriptions remain unchanged in this feature; Copilot documentation explicitly distinguishes slash invocation from the descriptions' host-neutral explicit-invocation wording.
- Per D-005, scope includes the smallest implementation-skill change needed for platform-aware Spec Kit prerequisite selection and any generated-distribution synchronization required by that change.
- This feature does not change application code or the product and architecture decisions established by feature 003.
