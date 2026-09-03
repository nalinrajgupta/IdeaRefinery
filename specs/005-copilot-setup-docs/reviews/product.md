# Product Review: First-Class GitHub Copilot Setup Documentation

## PRODUCT-001

- **Severity**: critical
- **Artifact / section**: Current README prerequisites, tryout, installation, and troubleshooting
- **Evidence**: Copilot is named as supported, but actionable setup and troubleshooting paths remain Codex-specific.
- **Why it matters**: A Copilot user cannot discover a first-class path to refinement or the separate implementation workflow.
- **Smallest proposed change**: Add the concise Copilot quick start required by Spec v1.
- **Human decision required**: no

## PRODUCT-002

- **Severity**: critical
- **Artifact / section**: Current setup guide scope and modes
- **Evidence**: The guide explicitly covers Codex and redirects Copilot readers without project-local, personal, lifecycle, or platform commands.
- **Why it matters**: Copilot installation and recovery are not executable user journeys.
- **Smallest proposed change**: Add a contiguous Copilot section covering both generated skills and Windows plus portable commands.
- **Human decision required**: no

## PRODUCT-003

- **Severity**: high
- **Artifact / section**: Copilot refresh and lifecycle guidance
- **Evidence**: No current document tells users to reload skills or restart after copying or updating them.
- **Why it matters**: Correctly installed skills may appear missing or stale.
- **Smallest proposed change**: Put refresh and restart guidance beside install, update, and troubleshooting steps.
- **Human decision required**: no

## PRODUCT-004

- **Severity**: medium
- **Artifact / section**: Documentation validation
- **Evidence**: Existing checks do not assert the required Copilot README and setup content.
- **Why it matters**: First-class guidance can regress without detection.
- **Smallest proposed change**: Add focused assertions for setup paths, lifecycle, invocation boundary, and configuration preservation.
- **Human decision required**: no

## Coverage attestation

FR-001, FR-002, and FR-008: PRODUCT-001. FR-003 through FR-005 and FR-013: PRODUCT-002. FR-007: PRODUCT-003. FR-014 and SC-005: PRODUCT-004. FR-006 and FR-009 through FR-012: no issue. SC-001: PRODUCT-001. SC-002: PRODUCT-002. SC-003: PRODUCT-001 through PRODUCT-003. SC-004: no issue.

