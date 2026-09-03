# Product review: Cross-Host Idea Refinery Skills

ID: R-003
Reviewer: Product
Severity: high
Artifact / section: Spec v1, User Stories 1–3
Evidence: The draft treats skill discoverability and component availability as related but does not make their distinction visible to users.
Why it matters: A user may conclude that the full workflow failed when a named helper is unavailable, even though the local safety contract can complete the same stage.
Smallest proposed change: Document a capability matrix and require every fallback to state what ran, what did not run, and whether the verdict is degraded or blocked.
Human decision required: no
Resolution: accepted

ID: R-004
Reviewer: Product
Severity: medium
Artifact / section: Spec v1, User Story 3
Evidence: Copying skills into personal locations creates a risk that later source updates never reach installed copies.
Why it matters: Users could unknowingly run stale workflow instructions.
Smallest proposed change: Provide explicit update and version/validation instructions for copied Hermes installs, alongside project-source options.
Human decision required: no
Resolution: accepted
