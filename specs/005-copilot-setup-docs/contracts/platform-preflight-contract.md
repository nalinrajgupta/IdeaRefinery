# Platform Preflight Contract

## Inputs

- Active repository root
- Active feature pointer
- Available command executors
- Presence of:
  - `.specify/scripts/bash/check-prerequisites.sh`
  - `.specify/scripts/powershell/check-prerequisites.ps1`

## Required behavior

1. Inspect both supported candidate paths.
2. Prefer the platform-native executable candidate.
3. Invoke exactly one candidate with equivalent semantics:
   - emit JSON;
   - require tasks;
   - include tasks.
4. Parse the active feature and required artifact paths exactly as the existing entry gate requires.
5. Continue through all existing checklist, readiness, decision, and evidence gates.

## Failure behavior

If neither supported candidate is present and executable, stop before implementation work and report:

- both expected paths;
- that Bash and PowerShell are the supported families;
- that the repository's Spec Kit initialization or script distribution must be repaired.

The workflow must not silently skip prerequisite validation or infer success-shaped paths.

## Compatibility

- Existing Bash behavior remains supported.
- Native PowerShell repositories can enter the same implementation workflow.
- Python-only prerequisite scripts are outside this feature.

