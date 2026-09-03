# Research: First-Class GitHub Copilot Setup Documentation

## Decision 1: Use the generated distribution for all Copilot installation paths

**Decision**: Repository-local discovery uses `.agents/skills/idea-refinery-*`; personal installation copies those generated directories into `~/.copilot/skills/`.

**Rationale**: Feature 003 established the generated directories as the portable, self-contained distribution. The current Copilot session successfully discovered and invoked the personal copy from that location.

**Alternatives considered**:

- Copy canonical skill folders directly: rejected because the generated full skill bundles required runtime assets and the repository already validates distribution parity.
- Maintain a separate Copilot-only distribution: rejected because it would reintroduce drift.

## Decision 2: Separate quick-start and lifecycle documentation

**Decision**: Keep the README short and outcome-oriented; put executable installation and maintenance procedures in `setup.md`; keep cross-host capability rationale in `docs/host-compatibility.md`.

**Rationale**: This satisfies the approved first-class approach without duplicating a large compatibility matrix across documents.

**Alternatives considered**:

- Minimal links only: rejected by the user because Copilot should be first-class.
- Duplicate complete instructions in both files: rejected because duplicate commands drift.

## Decision 3: Treat personal installation as an exact, failure-safe replacement

**Decision**: Validate both generated sources, stage both copies, verify staging, then replace only the two named personal skill targets. Missing-safe removal is required.

**Rationale**: Direct recursive copying over an existing directory can leave stale files or create nested directories. Deleting targets before source validation can leave a partial installation.

**Alternatives considered**:

- Overlay copy: rejected because it does not remove stale files.
- Unconditional delete then copy: rejected because source or copy failure can destroy a working installation.
- Symlinks as the only personal mode: rejected because Windows permissions and portability vary.

## Decision 4: Document Copilot slash invocation without rewriting canonical descriptions

**Decision**: Copilot guidance uses `/idea-refinery-full <idea>` and `/idea-refinery-implement`; it discloses that current generated descriptions retain dollar-prefixed explicit-invocation wording for cross-host compatibility.

**Rationale**: This is the user's D-004 decision. It avoids widening the feature to rewrite canonical descriptions while preventing the dollar-prefixed wording from being presented as a Copilot command.

**Alternatives considered**:

- Make descriptions host-neutral and regenerate: recommended by review but declined for this feature.
- Present both syntaxes as interchangeable: rejected because it is misleading.

## Decision 5: Support Bash and PowerShell implementation preflight

**Decision**: The implementation skill resolves and invokes an available Bash or PowerShell prerequisite script with equivalent task-required JSON semantics.

**Rationale**: Bash preserves existing behavior; PowerShell supports the requested native Windows setup. The user explicitly limited the compatibility contract to these two families.

**Alternatives considered**:

- Require Bash on Windows: rejected by D-005.
- Add Python script support: rejected as unnecessary scope.
- Trust only the integration metadata: rejected because repositories can contain migrated or mixed layouts and the executable path still needs validation.

## Decision 6: Validate documentation through existing contract tests

**Decision**: Extend `tests/unit/test_host_skill_distribution.py` and the existing workflow path filters rather than adding a new test runner.

**Rationale**: The current test already owns host-skill distribution and compatibility documentation contracts. Keeping related assertions together minimizes tooling and CI complexity.

**Alternatives considered**:

- Add a Markdown linter: rejected because the feature does not require a new tool.
- Manual-only review: rejected because primary guidance could regress silently.

