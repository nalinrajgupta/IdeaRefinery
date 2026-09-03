# Architect Review: First-Class GitHub Copilot Setup Documentation

## ARCH-001

- **Severity**: high
- **Artifact / section**: FR-002, FR-008, SC-004, and generated skill descriptions
- **Evidence**: Copilot invokes skills with `/idea-refinery-*`, while generated skill descriptions still advertise Codex-style `$idea-refinery-*`.
- **Why it matters**: Documentation can teach the correct invocation while the loaded skill advertises a contradictory one.
- **Smallest proposed change**: Require the Copilot slash invocation explicitly and decide whether canonical descriptions may become host-neutral before regeneration.
- **Human decision required**: yes

## ARCH-002

- **Severity**: high
- **Artifact / section**: Windows setup scope and implementation preflight
- **Evidence**: The proposed guide promises native PowerShell installation, while the implementation workflow currently calls a Bash prerequisite script directly.
- **Why it matters**: Setup can succeed on Windows but the separately authorized implementation workflow can fail immediately without Bash-compatible Spec Kit scripts.
- **Smallest proposed change**: Decide whether Windows guidance requires Bash and `sh` scripts or the implementation skill should select an available prerequisite script.
- **Human decision required**: yes

## ARCH-003

- **Severity**: high
- **Artifact / section**: Personal installation lifecycle
- **Evidence**: Spec v1 does not require repeat-run behavior, source preflight, failure-safe replacement, or missing-safe removal.
- **Why it matters**: Naive copy commands can retain stale files, nest directories, or leave partial installations.
- **Smallest proposed change**: Require exact replacement, source validation before deletion, idempotence, failed-preflight safety, and missing-safe removal.
- **Human decision required**: no

## ARCH-004

- **Severity**: medium
- **Artifact / section**: Repository-local and personal precedence
- **Evidence**: Spec v1 notes version drift but does not require guidance for identifying which copy is active.
- **Why it matters**: A stale repository copy can shadow an updated personal copy and make updates appear ineffective.
- **Smallest proposed change**: Document precedence and active-location inspection after reload.
- **Human decision required**: no

## ARCH-005

- **Severity**: high
- **Artifact / section**: Workflow path filters and FR-014
- **Evidence**: The validation workflow filters omit `README.md` and `setup.md`.
- **Why it matters**: Documentation regressions might not run the checks intended to prevent them.
- **Smallest proposed change**: Include both files in push and pull-request path filters.
- **Human decision required**: no

## ARCH-006

- **Severity**: high
- **Artifact / section**: FR-014, SC-005, and documentation tests
- **Evidence**: Existing tests do not validate primary Copilot setup content, paths, lifecycle commands, invocation forms, labels, links, or preservation guidance.
- **Why it matters**: Tests could pass with unsafe or contradictory instructions.
- **Smallest proposed change**: Add a requirement-to-validation matrix and content-focused automated assertions, with explicit manual checks for usability criteria.
- **Human decision required**: no

## ARCH-007

- **Severity**: medium
- **Artifact / section**: Shell labeling across all setup documents
- **Evidence**: The compatibility guide contains unlabeled POSIX commands even though Windows users are directed to it.
- **Why it matters**: Native PowerShell readers can copy commands unavailable in their environment.
- **Smallest proposed change**: Apply shell-label requirements to all three documents and pair or redirect POSIX-only examples.
- **Human decision required**: no

## Coverage attestation

FR-001, FR-009, and FR-012: no issue. FR-002 and FR-008: ARCH-001. FR-003 and FR-006: ARCH-003 and ARCH-004. FR-004 and FR-010: ARCH-002 and ARCH-003. FR-005: ARCH-003 and ARCH-007. FR-007: ARCH-004. FR-011 and FR-013: ARCH-007. FR-014: ARCH-005 and ARCH-006. SC-001: ARCH-001. SC-002: ARCH-003. SC-003: ARCH-001 and ARCH-004. SC-004: ARCH-001 and ARCH-007. SC-005: ARCH-005 and ARCH-006.

