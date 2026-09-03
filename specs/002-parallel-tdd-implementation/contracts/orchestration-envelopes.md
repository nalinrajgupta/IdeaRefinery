# Orchestration Envelope Contract

## Worker assignment

A valid assignment identifies the run, wave, slice, task IDs, linked requirements, satisfied dependencies, allowed read/write paths, forbidden shared paths, baseline, test commands, component routing, and stop conditions. The envelope is immutable after dispatch.

## Worker result

A valid result identifies status, addressed tasks, actual changed paths, baseline/red/green/refactor/broader evidence, unexpected paths, decisions, and risks. `complete` is invalid when behavior changed without valid red and green evidence, when changed paths exceed the assignment, or when a required field is absent.

## Review result

A valid review comes from an agent different from all workers in the wave. It binds to the frozen assignment, diff, and worker evidence. Findings identify severity, requirement/task, evidence, impact, smallest correction, material-decision status, and disposition. Missing or malformed review produces `review-blocked`, never implicit approval.

## Promotion

Only the controller promotes a slice. Promotion requires valid worker evidence, path-scope compliance, independent review with all material findings disposed, and passing integrated verification. Promotion is the only event that permits the controller to mark Spec Kit tasks complete.
