# Implementation orchestration contract

## Ownership model

The controller owns scheduling, user communication, artifact interpretation, shared state, task checkboxes, review disposition, and final claims. Implementation workers own only their assigned task slice and declared paths. Reviewers are read-only and must be different agents from every worker in the reviewed wave.

Use one shared workspace only for provably disjoint writes protected by a host-enforced scoped sandbox/freeze. Directory separation is insufficient when tasks share a lockfile, generated output, migration order, schema, fixture, snapshot, or configuration. When enforcement is unavailable, workers return patches for controller application or execution is sequential. Use worktrees only after user approval and with an explicit integration plan.

## Task-slice envelope

Every worker receives an immutable brief containing:

```text
Run ID:
Envelope version:
Wave ID:
Slice ID:
Task IDs:
Requirements / acceptance scenarios:
Plan constraints:
Dependencies already satisfied:
Allowed read paths:
Allowed write paths:
Forbidden shared paths:
Narrow test command:
Broader verification command:
Baseline status:
Selected component skill or local fallback:
Stop conditions:
Created-at timestamp:
Protected artifact/path hashes:
Wave lease:
```

Do not give workers ownership of `tasks.md`, `refinery-state.md`, `implementation-state.md`, `.specify/feature.json`, or another worker's paths.

## Write-set scheduling

A candidate slice may join a wave only when all are true:

1. Every predecessor is verified complete.
2. Its write set is known and does not overlap another candidate's write set by exact path or ancestor/descendant relationship.
3. Its tests do not rewrite snapshots, fixtures, generated files, or caches owned by another candidate.
4. It does not touch a global exclusive resource.
5. Its paths do not overlap unrelated dirty work.
6. Failure can be reviewed independently without reverting another slice.

Canonicalize every claim to a normalized repository-relative path. Resolve symlink targets, reject traversal outside the repository, and treat exact matches plus ancestor/descendant pairs as overlaps. Capture tracked content, relevant untracked content, file type/mode, and protected coordination-artifact hashes before dispatch. Hold one controller-owned lease for the wave until post-return drift verification completes.

Sort eligible slices by task ID before packing waves. Use no more than three workers. `[P]` can add a candidate to consideration but cannot override these rules.

## Recorded TDD contract

For each behavior-changing slice:

1. **Baseline**: Run the relevant existing narrow and broader tests before changing the slice. Record timestamp, command output, exit status, and pre-test source hashes. Record unrelated failures separately and prohibit promotion until they are isolated or resolved.
2. **Red**: Change tests only; record the test-diff hash and timestamp; run the narrow command; and capture the command, exit status, newly added failing assertion, and why that failure demonstrates the missing behavior. A syntax error, import failure, environment failure, unrelated assertion, or pre-existing failure is not valid red evidence. If the new test already passes, improve the test or explain why no production change is needed.
3. **Green**: Make the smallest production change that satisfies the test. Re-run the narrow command and capture passing output.
4. **Refactor**: Improve clarity without adding behavior. Re-run the narrow command and relevant broader suite.
5. **Scope check**: Record implementation/refactor diff hashes and ordered timestamps, report changed paths, and verify them against the envelope and protected pre-dispatch hashes.

For documentation-only, generated-artifact-only, or other non-behavioral work, record `test-first: inapplicable` with a concrete rationale and an appropriate validation command. The controller decides whether the rationale is valid.

## Worker result envelope

```text
Slice ID:
Status: complete | blocked | failed
Task IDs addressed:
Changed paths:
Baseline evidence:
Red evidence:
Green evidence:
Refactor evidence:
Broader verification:
Unexpected paths needed:
Decisions encountered:
Risks / follow-ups:
```

Missing fields make the result incomplete. A worker report is evidence to inspect, not authority to mark tasks complete.

## Review contract

The reviewer receives the frozen assignment, applicable spec/plan excerpts, baseline, diff, and evidence envelope. It must not edit files, run destructive commands, update task state, or broaden approved scope.

Each material finding contains:

```text
ID:
Severity: blocker | critical | high | medium | low
Requirement / task:
Evidence:
Why it matters:
Smallest correction:
Material decision required: yes | no
Disposition: pending | accepted | rejected — evidence | deferred — trigger
```

Review for requirement compliance first, then code quality, failure paths, test strength, path-scope violations, and regressions. A missing, timed-out, self-authored, or malformed review leaves the wave `review-blocked`; it cannot be promoted until a replacement independent reviewer returns valid evidence. Objective medium/low improvements may be deferred only with a trigger; blocker/critical/high findings must be resolved or explicitly owned by the user.

## Failure and recovery

- If a worker needs an undeclared path, stop that slice. Recompute ownership; do not expand it silently.
- If a worker fails while other disjoint workers succeed, preserve their changes but promote no failed or unreviewed slice.
- If tests expose an unexplained failure, use `$systematic-debugging` when available or reproduce, isolate, hypothesize, and test the cause before changing code.
- If artifacts or assigned paths change after dispatch, invalidate the affected result and redispatch from a new frozen brief.
- Resume a verified wave only when artifact hashes, changed-path hashes, commands, and review disposition still match.
- If any protected or claimed path drifts while a wave lease is active, quarantine all affected results. Use a three-way comparison against the pre-dispatch snapshot to attribute changes, then re-plan and re-review instead of promoting uncertain work.

## Hook lifecycle

The controller runs each enabled unconditional `before_implement` hook once per run before baselines, snapshots, leases, or worker dispatch. It runs each enabled unconditional `after_implement` hook once after the last convergence cycle and before fresh final verification. Record the hook identity, command, output, timestamp, and changed-path hashes. A hook mutation invalidates every assignment, test result, or review whose protected inputs it changed.

## Convergence budget

The initial implementation pass does not consume convergence budget. The controller snapshots `tasks.md`, invokes `$speckit-converge` under its own identity, verifies that the only mutation is one append-only Convergence section, and records the exact patch and hashes. Each accepted append starts one cycle. Run no more than two such implementation cycles. Canonicalize findings by root requirement and cause so renamed tasks cannot reset the budget.
