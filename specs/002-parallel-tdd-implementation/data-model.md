# Data Model: Parallel TDD Implementation Skill

## Implementation Run

- `run_id`: stable identifier for one invocation/resume chain
- `feature_directory`: active Spec Kit feature
- `artifact_hashes`: hashes protecting the approved input set
- `initial_git_status`: dirty paths present before execution
- `status`: preparing, executing, reviewing, review-blocked, converging, complete, or blocked
- `worker_capacity`: resolved concurrency cap, never above three
- `convergence_cycles`: integer from zero through two
- `component_routing`: preferred skill or local fallback per stage

An implementation run contains execution waves, slice evidence, review findings, decisions, and verification records.

## Task Slice

- `slice_id` and linked Spec Kit `task_ids`
- linked requirements and acceptance scenarios
- satisfied predecessor IDs
- immutable read/write/forbidden path sets
- narrow and broader verification commands
- baseline status and stop conditions

A slice belongs to exactly one wave attempt. Changing its protected inputs creates a new attempt.

## Execution Wave

- ordered `wave_id`
- ordered eligible slices
- union of disjoint write sets
- dispatch, review, and promotion status
- integrated verification result

Only reviewed and verified waves become promoted.

## Worker Evidence

- baseline result
- red command, status, failing assertion, and causal explanation
- green command and result
- refactor/broader verification result
- changed and unexpectedly required paths
- decisions and risks encountered

## Review Finding

- stable finding ID and severity
- linked requirement/task
- concrete evidence and impact
- smallest correction and material-decision flag
- disposition with evidence or trigger

## State Transitions

```text
preparing -> executing -> reviewing -> promoted
                         -> review-blocked -> reviewing
executing/reviewing -> blocked
promoted -> executing (next wave) | converging | complete
converging -> executing (appended tasks) | complete | blocked
```
