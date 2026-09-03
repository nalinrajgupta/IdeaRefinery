# CEO review: Cross-Host Idea Refinery Skills

ID: R-001
Reviewer: CEO
Severity: high
Artifact / section: Spec v1, User Story 3 and FR-006
Evidence: A repository skill is only useful when a maintainer can install it without guessing whether their host discovers project folders, home folders, or copied files. The draft commits to documentation but does not yet require an end-to-end installation path per host.
Why it matters: Users could mistake a copied file or partial setup for a supported full workflow and lose the explicit authority boundary.
Smallest proposed change: Require a host matrix with discovery, installation, invocation, Spec Kit setup, update/removal, and honest capability limitations for Codex, Copilot, and Hermes.
Human decision required: no
Resolution: accepted

ID: R-002
Reviewer: CEO
Severity: medium
Artifact / section: Spec v1, FR-001
Evidence: The value proposition is portable full workflows, not merely broader syntax support.
Why it matters: Host-specific instructions could accidentally reduce a skill to a generic prompt and erode the product promise.
Smallest proposed change: State that workflow parity is validated against canonical content and that any host exception is an explicit fallback with recorded limitations.
Human decision required: no
Resolution: accepted
