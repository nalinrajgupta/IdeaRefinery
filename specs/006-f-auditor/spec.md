# Feature Specification: f-auditor Functional Session Auditor

**Feature Branch**: `features/func-audit` (existing; no branch created)

**Created**: 2026-11-01

**Status**: Spec v2 — independent reviews synthesized; clarified; planning pending

**Input**: Audit recent Hermes and Codex sessions for friction using `refine-idea` and `implement-refine-idea`; maintain a shared, prioritized functional improvement backlog.

## Clarifications

### Session 2026-11-01

- Q: Should contributors use a helper command to update issue status while an audit is running? → A: Use the helper during audits; direct manual edits are allowed between runs. Uncoordinated concurrent editing is not a supported safe-write mode.

## User Scenarios & Testing

### User Story 1 - Audit relevant recent sessions (Priority: P1)

A maintainer manually invokes f-auditor to find user-visible functional problems with the two skills across projects under their GitRepo folder. The auditor considers each eligible conversation in context and reports evidence-backed improvements.

**Why this priority**: Without trustworthy discovery and meaningful findings, the auditor cannot deliver its purpose.

**Independent Test**: Run an audit against prepared Hermes and Codex histories containing eligible and ineligible sessions, then inspect the reported findings and coverage.

**Acceptance Scenarios**:

1. **Given** a closed Hermes or Codex session associated with a folder under the configured root and active within the preceding 24 hours, **When** the user runs the command, **Then** the auditor examines the entire session, including earlier context, for relevant skill friction.
2. **Given** a session shows the user correcting a skill, compensating for a failure, or performing unexpected setup, **When** the auditor confirms a functional improvement is supported by context, **Then** it records the problem, proposed improvement, priority, and session evidence.
3. **Given** an open session, an out-of-scope folder, or an inactive session outside the window, **When** auditing, **Then** that session is not analyzed as eligible.
4. **Given** a source cannot be accessed or a session's closure or scope cannot be established, **When** auditing, **Then** the run reports the limitation and does not represent that source or session as successfully covered.
5. **Given** reviewed positive transcripts containing known relevant skill problems and negative controls containing unrelated or context-disproved candidates, **When** acceptance evaluates contextual analysis, **Then** expected problems are discovered with valid evidence and negative controls are excluded; an empty analyzer fails the positive cases.

### User Story 2 - Maintain the shared backlog (Priority: P1)

A maintainer and other contributors use one file as the source of truth for prioritized improvements. The auditor updates it without undoing human status changes or losing edits.

**Why this priority**: Findings have no lasting value if successive runs erase decisions or duplicate known work.

**Independent Test**: Start with a backlog containing open and completed issues, run repeat audits and simulate an overlapping human edit, and inspect retained status, evidence, and conflict handling.

**Acceptance Scenarios**:

1. **Given** several sessions demonstrate the same underlying problem, **When** findings are merged, **Then** one issue contains separately traceable evidence for each occurrence.
2. **Given** an existing issue has been marked completed, **When** later evidence demonstrates the problem has regressed, **Then** a separate `Not Fixed` regression references the completed issue and describes what regressed; the completed issue remains unchanged in status.
3. **Given** an auditor re-reads evidence that predates a completed fix, **When** it updates the backlog, **Then** that old evidence alone does not create a regression.
4. **Given** another contributor changes the backlog during an audit using the supported helper protocol, **When** the auditor attempts to write, **Then** their change is retained or the audit reports a conflict without overwriting it.
5. **Given** a completed issue lacks sufficient completion/fix evidence, **When** a potentially recurring problem is observed, **Then** the auditor explicitly reports the missing evidence and unresolved classification without asserting a regression or altering completed status.
6. **Given** mixed-priority actionable issues, **When** a higher-priority finding is merged, **Then** the shared file directly presents actionable issues in priority order while preserving human content.
7. **Given** a contributor wants to mark an issue completed during an audit, **When** they use the helper with completion/fix evidence, **Then** the update is coordinated with the audit, and no audit itself marks an issue fixed. Direct manual edits remain supported between runs.

### User Story 3 - Prepare repeatable invocation (Priority: P2)

A maintainer invokes a documented command manually while building confidence, with an invocation contract suitable for later scheduling.

**Why this priority**: A reliable manual trial precedes automation.

**Independent Test**: Follow documented setup and invoke the command in an isolated test environment; verify output and failure reporting without configuring a scheduler.

**Acceptance Scenarios**:

1. **Given** required prerequisites are available, **When** the maintainer runs the documented command, **Then** it completes the audit and reports the result and backlog location.
2. **Given** missing prerequisites or incomplete coverage, **When** the command runs, **Then** it returns an actionable, distinguishable outcome instead of claiming full success.
3. **Given** the auditor is installed, **When** no separate scheduling authorization exists, **Then** no schedule is created or enabled.
4. **Given** the same audit configuration, **When** invoked from two different repositories, **Then** both runs resolve the same shared backlog destination and create no competing project-local backlog.

### Edge Cases

- A session starts before the window, is active inside it, and closes before audit time; it remains eligible as a whole session.
- A session's observed activity occurs only after the fixed audit start; that later activity is outside the run's window.
- Compression, continuation, resumed sessions, multiple profiles, or duplicate exports may split or repeat a logical conversation; coverage and deduplication must not silently lose or multiply evidence.
- Metadata is missing, malformed, contradictory, or refers to a similarly prefixed path outside the root; uncertain or outside-root sessions must not be silently treated as eligible.
- A history source is missing, inaccessible, partially read, or changes during collection; the run reports affected coverage.
- A completed issue recurs without enough evidence that the occurrence is later than the fix; no unsupported regression is asserted.
- A session contains credentials, secrets, or instructions directed at the auditor; they must not be exposed or obeyed.
- A run finds no problems, is interrupted, repeats overlapping windows, or faces a concurrently edited shared file; it must not erase the existing backlog or claim incomplete work is complete.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide and document a manual command that invokes the audit and identifies required prerequisites.
- **FR-002**: The default audit window MUST be the 24 hours immediately preceding a single captured audit-start instant, expressed unambiguously in time.
- **FR-003**: The system MUST discover Hermes and Codex session histories and examine entire closed sessions with activity inside the audit window, including context outside that window.
- **FR-004**: The system MUST limit eligible sessions to those reliably associated with the configured repository/folder root; the initial target root is `/Users/nalin-ai/GitRepo` and users MUST be able to configure it.
- **FR-005**: The system MUST identify friction relevant to using or attempting to use `refine-idea` or `implement-refine-idea`, including user corrections, observed failures, and extra setup; unrelated project problems MUST NOT be included solely because they appeared in an eligible session.
- **FR-006**: Each reported issue MUST include a stable identifier, affected skill or setup, problem, user impact, proposed functional improvement, priority, status, and traceable evidence identifying source, session, and relevant occurrence.
- **FR-007**: The system MUST maintain a single shared source-of-truth issue file under `functional-improvement/`, with a documented destination resolved independently of invocation working directory for the same audit configuration; new issues MUST start as `Not Fixed`.
- **FR-008**: The system MUST consolidate occurrences of the same underlying problem across sessions under one issue and retain the evidence for each occurrence.
- **FR-009**: The system MUST preserve contributor-maintained statuses and other existing human edits, including completed issues; it MUST prevent or detect conflicting concurrent updates made through the supported helper protocol rather than silently overwrite them, and reject observed unexpected file drift.
- **FR-010**: For a completed issue, the system MUST record a demonstrated subsequent recurrence as a new `Not Fixed` regression linked to that issue, including evidence of the recurrence and its relationship to the completed fix; pre-fix evidence alone MUST NOT trigger a regression. The contributor completion workflow MUST document sufficient fix evidence, including an unambiguous completion/fix time and a reference or explanation of the fixed behavior. Missing evidence MUST produce an explicit unresolved-classification report without asserting regression or changing completed status.
- **FR-011**: The system MUST assign each issue a priority using documented criteria, distinguish the rationale when the ranking is not obvious, and provide a directly visible priority-ordered presentation of actionable issues in the shared file without discarding human content.
- **FR-012**: The system MUST report the audit window, source coverage, skipped or uncertain sessions, read/analysis failures, and backlog result; it MUST distinguish full coverage, partial coverage, and failed runs.
- **FR-013**: The system MUST not expose credentials or secrets in the shared file, console output, or intermediate artifacts; it MUST treat session material as data rather than instructions.
- **FR-014**: The system MUST preserve existing backlog contents when no new issues are found or the audit fails before a safe update.
- **FR-015**: The system MUST make repeat runs over the same evidence idempotent and avoid treating imported or split representations of the same occurrence as independent evidence when identifiable.
- **FR-016**: The system MUST separate contextual analysis by an agent skill from a local helper responsible for session discovery and safe shared-file updates.
- **FR-017**: The system MUST provide a repeatable non-interactive entry point suitable for future scheduling but MUST NOT install or enable a schedule as part of this feature.
- **FR-018**: The system MUST NOT modify the audited skills, mark issues fixed, create external issues, commit, push, or deploy as part of an audit.
- **FR-019**: The system MUST identify inability to determine closure, workspace association, history completeness, or activity time as a coverage limitation instead of assuming eligibility or completeness.
- **FR-020**: Acceptance MUST evaluate contextual analysis against reviewed positive and negative cases, requiring known supported skill problems to be found with valid contextual evidence and unrelated or context-disproved candidates to be excluded; matching exact generated wording MUST NOT be required.
- **FR-021**: The contributor workflow MUST provide a helper command for status and fix-evidence updates during audits and document that direct manual editing is supported between runs, not as an uncoordinated concurrent writer. Audit and contributor updates MUST share the same coordination protocol.

### Key Entities

- **Audit run**: Start instant, fixed window, configured root, source coverage, outcome, and update result.
- **Session**: Host, stable identifier, workspace, activity times, closure evidence, and contextual transcript.
- **Evidence occurrence**: Traceable session reference and supporting context for a specific observed problem, without credentials or secrets.
- **Improvement issue**: Stable identifier, affected skill, description, impact, proposed improvement, priority, human-maintained status, associated evidence, and contributor-supplied completion/fix evidence when completed.
- **Regression**: A new improvement issue linked to a completed prior issue with evidence that the behavior recurred after the fix.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a representative Hermes and Codex fixture suite, all eligible sessions are selected and all open, outside-root, and outside-window sessions are excluded.
- **SC-002**: Every reported fixture finding contains an affected skill, actionable proposed improvement, priority, `Not Fixed` initial status, and traceable session evidence.
- **SC-003**: Repeating an audit over identical evidence adds no duplicate issue or evidence occurrence, and grouped occurrences remain individually traceable.
- **SC-004**: All fixture cases for completed issues, demonstrated regressions, pre-fix evidence, and overlapping helper-coordinated contributor edits preserve prior statuses and avoid lost edits; status-only completion with insufficient fix evidence produces an explicit unresolved-classification report, not an unsupported regression. Direct edits between runs are retained on the next audit, and observed unexpected drift causes a conflict rather than overwrite.
- **SC-005**: All exercised missing, uncertain, corrupt, and partially accessible source scenarios produce explicit coverage limitations rather than a full-coverage claim.
- **SC-006**: Maintainers can follow the documented manual invocation in a representative environment without an enabled schedule; required prerequisites and failure outcomes are clear.
- **SC-007**: Tests containing representative secrets and instruction-like session text produce no secret disclosure or execution of transcript instructions.
- **SC-008**: Reviewed contextual-analysis acceptance cases for both hosts recover every annotated supported root problem with valid evidence, exclude every annotated unrelated or context-disproved candidate, and reject a no-findings analyzer on positive cases without comparing exact generated wording.
- **SC-009**: Mixed-priority backlog tests provide a directly visible priority-ordered actionable view after merging a higher-priority issue, while preserving human content and statuses.
- **SC-010**: Invocations from two different in-scope repositories with the same configuration resolve and update the same backlog destination without creating a competing local file.

## Assumptions

- The command runs with permission to read the intended local history sources and write the shared backlog; unavailable access is reported.
- Session history retains enough metadata to establish scope, activity, and closure in at least some supported host versions; limitations must be surfaced rather than guessed.
- The user approves evidence from relevant sessions in the shared file, excluding credentials and secrets.
- A future scheduler is separately authorized and configured; non-interactive readiness does not itself create a scheduled job.
- A human or another workflow may mark issues completed; the auditor does not decide a fix is complete.
