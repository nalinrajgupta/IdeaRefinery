from __future__ import annotations

from dataclasses import asdict
import json

import pytest

from idea_refinery import continuation
from idea_refinery.errors import ContractError, StateError


def test_drive_terminal_completes_all_internal_checklist_items_in_order() -> None:
    """Catches a drive loop that exits before routine completion work is done."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
            continuation.CompletionItem("review", "review-correction", evidence="R1 corrected"),
            continuation.CompletionItem("state", "state-recording", evidence="state recorded"),
            continuation.CompletionItem("tasks", "task-promotion", evidence="T001 promoted"),
            continuation.CompletionItem("converge", "convergence", evidence="converge round 1 clean"),
        )
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("review", "tasks", "state", "converge", "verify")
    assert all(item.completed for item in result.state.checklist)


def test_template_shaped_checklist_drives_all_routine_kinds_to_completion() -> None:
    """Catches a sidecar that rejects routine item kinds required by the state template."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("verify", "final-verification"),
            continuation.CompletionItem("after", "after-hook"),
            continuation.CompletionItem("converge", "convergence"),
            continuation.CompletionItem("state", "state-recording"),
            continuation.CompletionItem("promote", "task-promotion"),
            continuation.CompletionItem("correct", "review-correction"),
            continuation.CompletionItem("review", "review"),
            continuation.CompletionItem("task", "task"),
        )
    )

    result = continuation.drive_terminal(
        state,
        action_results={
            "verify": "full suite passed",
            "after": "after hook applied",
            "converge": "converge round 1 clean",
            "state": "state recorded",
            "promote": "T001 promoted",
            "correct": "R1 corrected",
            "review": "review envelope accepted",
            "task": "slice implemented",
        },
    )

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == (
        "task",
        "review",
        "correct",
        "promote",
        "state",
        "converge",
        "after",
        "verify",
    )


def test_protected_path_is_requested_once_before_any_internal_mutation() -> None:
    """Catches a preflight regression that promotes tasks before authorization."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "tasks-output",
                "protected-path-authorization",
                category="specs/004/tasks.md",
            ),
            continuation.CompletionItem("tasks", "task-promotion"),
        )
    )

    first = continuation.drive_terminal(state)
    second = continuation.drive_terminal(first.state)

    assert first.verdict == "BLOCKED ON DECISION"
    assert first.completed_item_ids == ()
    assert first.authorization_requests == ("protected-path:specs/004/tasks.md",)
    assert first.state.blockers == (
        continuation.Blocker(
            "missing-authority",
            "missing protected-path authorization for: "
            "tasks-output (protected-path:specs/004/tasks.md)",
            ("tasks-output", "tasks"),
            derived=True,
        ),
    )
    assert second.authorization_requests == ()


def test_shared_preflight_category_emits_one_scoped_request() -> None:
    """Catches duplicate prompts when multiple gates need the same protected path."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "tasks-output",
                "protected-path-authorization",
                category="specs/004/tasks.md",
            ),
            continuation.CompletionItem(
                "state-output",
                "protected-path-authorization",
                category="specs/004/tasks.md",
            ),
        )
    )

    result = continuation.drive_terminal(state)

    assert result.authorization_requests == ("protected-path:specs/004/tasks.md",)


def test_granted_protected_path_resumes_and_completes_the_drive() -> None:
    """Catches a drive loop that remains blocked after its scoped approval arrives."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "tasks-output",
                "protected-path-authorization",
                category="specs/004/tasks.md",
            ),
            continuation.CompletionItem("tasks", "task-promotion", evidence="T001 promoted"),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        )
    )

    result = continuation.drive_terminal(
        state,
        granted_authorizations={"protected-path:specs/004/tasks.md"},
    )

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("tasks-output", "tasks", "verify")


def test_granted_protected_path_persists_when_a_later_validator_gate_blocks() -> None:
    """Catches a validator blocker discarding protected-path grants from the same drive."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "tasks-output",
                "protected-path-authorization",
                category="specs/004/tasks.md",
            ),
            continuation.CompletionItem(
                "validator",
                "validator-prerequisite",
                category="PyYAML",
            ),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        )
    )

    first = continuation.drive_terminal(
        state,
        granted_authorizations={"protected-path:specs/004/tasks.md"},
    )
    resolved = continuation.drive_terminal(first.state, available_validators={"PyYAML"})

    assert first.verdict == "BLOCKED ON VERIFICATION"
    assert first.completed_item_ids == ("tasks-output",)
    tasks_output_item = next(
        item for item in first.state.checklist if item.item_id == "tasks-output"
    )
    assert tasks_output_item.completed is True
    assert tasks_output_item.evidence == "authorization granted: protected-path:specs/004/tasks.md"
    assert resolved.verdict == "IMPLEMENTATION COMPLETE"
    assert resolved.completed_item_ids == ("validator", "verify")


def test_partial_protected_path_grants_persist_before_another_path_blocks() -> None:
    """Catches one missing path discarding another path's grant from the same drive."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "tasks-output",
                "protected-path-authorization",
                category="specs/004/tasks.md",
            ),
            continuation.CompletionItem(
                "state-output",
                "protected-path-authorization",
                category="specs/004/implementation-state.md",
            ),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        )
    )

    first = continuation.drive_terminal(
        state,
        granted_authorizations={"protected-path:specs/004/tasks.md"},
    )
    resumed = continuation.drive_terminal(
        first.state,
        granted_authorizations={"protected-path:specs/004/implementation-state.md"},
    )

    tasks_output_item = next(
        item for item in first.state.checklist if item.item_id == "tasks-output"
    )
    assert tasks_output_item.completed is True
    assert tasks_output_item.evidence == "authorization granted: protected-path:specs/004/tasks.md"
    assert first.completed_item_ids == ("tasks-output",)
    assert continuation.continuation_result_document(first)["completed_item_ids"] == ["tasks-output"]
    assert first.state.blockers[-1].affected_item_ids == ("state-output", "verify")
    assert resumed.verdict == "IMPLEMENTATION COMPLETE"


def test_missing_validator_is_an_external_blocker_with_one_remediation_request() -> None:
    """Catches validation being skipped or repeatedly requesting the same prerequisite."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "validator",
                "validator-prerequisite",
                category="PyYAML",
            ),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        )
    )

    first = continuation.drive_terminal(state)
    second = continuation.drive_terminal(first.state)
    resolved = continuation.drive_terminal(first.state, available_validators={"PyYAML"})

    assert first.verdict == "BLOCKED ON VERIFICATION"
    assert first.authorization_requests == ("validator:PyYAML",)
    assert first.state.blockers == (
        continuation.Blocker(
            "external-state",
            "missing validator prerequisite for: validator (validator:PyYAML)",
            ("validator", "verify"),
            derived=True,
        ),
    )
    assert second.authorization_requests == ()
    assert resolved.verdict == "IMPLEMENTATION COMPLETE"
    assert resolved.completed_item_ids == ("validator", "verify")


def test_equivalent_validation_evidence_completes_validator_prerequisite() -> None:
    """Catches a drive loop that blocks despite recorded equivalent validation evidence."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "validator",
                "validator-prerequisite",
                category="PyYAML",
            ),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        ),
        prerequisite_resolutions=(
            continuation.PrerequisiteResolution(
                "PyYAML",
                "equivalent-evidence",
                "validated schema with the locked JSON decoder",
            ),
        ),
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("validator", "verify")
    assert result.state.prerequisite_resolutions == state.prerequisite_resolutions


@pytest.mark.parametrize("outcome", ["exact-validator", "equivalent-evidence"])
def test_partial_validator_resolutions_persist_before_another_validator_blocks(
    outcome: str,
) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "available", "validator-prerequisite", category="available"
            ),
            continuation.CompletionItem(
                "missing", "validator-prerequisite", category="missing"
            ),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        ),
        prerequisite_resolutions=(
            (continuation.PrerequisiteResolution("available", outcome, "schema validated"),)
            if outcome == "equivalent-evidence"
            else ()
        ),
    )

    blocked = continuation.drive_terminal(
        state, available_validators={"available"} if outcome == "exact-validator" else ()
    )

    assert blocked.state.checklist[0].completed is True
    assert blocked.state.checklist[0].evidence.startswith(f"{outcome}: ")
    assert blocked.completed_item_ids == ("available",)
    assert continuation.continuation_result_document(blocked)["completed_item_ids"] == ["available"]
    assert blocked.state.blockers[-1].affected_item_ids == ("missing", "verify")
    continuation.validate_completion_checklist(blocked.state)
    resumed = continuation.drive_terminal(blocked.state, available_validators={"missing"})
    assert resumed.verdict == "IMPLEMENTATION COMPLETE"
    assert resumed.completed_item_ids == ("missing", "verify")


@pytest.mark.parametrize(
    ("kind", "evidence", "resolutions"),
    [
        ("protected-path-authorization", "denied", ()),
        (
            "protected-path-authorization",
            "authorization granted: protected-path:other",
            (),
        ),
        ("validator-prerequisite", "validated", ()),
        (
            "validator-prerequisite",
            "unavailable: not installed",
            (continuation.PrerequisiteResolution("scope", "unavailable", "not installed"),),
        ),
        (
            "validator-prerequisite",
            "exact-validator: validated",
            (continuation.PrerequisiteResolution("other", "exact-validator", "validated"),),
        ),
        (
            "validator-prerequisite",
            "denied",
            (continuation.PrerequisiteResolution("scope", "exact-validator", "validated"),),
        ),
    ],
)
@pytest.mark.parametrize("persisted_verdict", [None, "IMPLEMENTATION COMPLETE"])
@pytest.mark.parametrize("replay", [False, True])
def test_completed_preflight_requires_scoped_acceptance_evidence(
    kind: str,
    evidence: str,
    resolutions: tuple[continuation.PrerequisiteResolution, ...],
    persisted_verdict: str | None,
    replay: bool,
) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "preflight", kind, completed=True, category="scope", evidence=evidence
            ),
        ),
        prerequisite_resolutions=resolutions,
        terminal_verdict=persisted_verdict,
    )
    if replay:
        state = continuation.continuation_state_from_document(
            {
                "checklist": json.loads(json.dumps([asdict(item) for item in state.checklist])),
                "prerequisite_resolutions": [asdict(resolution) for resolution in resolutions],
                "terminal_verdict": persisted_verdict,
            }
        )

    for validate in (
        continuation.validate_completion_checklist,
        continuation.drive_terminal,
    ):
        with pytest.raises(ContractError, match="completed preflight"):
            validate(state)


@pytest.mark.parametrize("outcome", ["exact-validator", "equivalent-evidence"])
def test_completed_preflight_evidence_survives_replay_without_new_grants(outcome: str) -> None:
    state = continuation.continuation_state_from_document(
        {
            "checklist": [
                {
                    "item_id": "path",
                    "kind": "protected-path-authorization",
                    "category": "scope",
                    "completed": True,
                    "evidence": "authorization granted: protected-path:scope",
                },
                {
                    "item_id": "validator",
                    "kind": "validator-prerequisite",
                    "category": "scope",
                    "completed": True,
                    "evidence": f"{outcome}: schema validated",
                },
                {
                    "item_id": "verify",
                    "kind": "final-verification",
                    "completed": True,
                    "evidence": "full suite passed",
                },
            ],
            "prerequisite_resolutions": [
                {"category": "scope", "outcome": outcome, "evidence": "schema validated"}
            ],
            "terminal_verdict": "IMPLEMENTATION COMPLETE",
        }
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ()
    assert result.state == state


def test_shared_validator_category_preserves_accepted_resolution() -> None:
    resolution = continuation.PrerequisiteResolution(
        "schema", "equivalent-evidence", "schema validated"
    )
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "accepted",
                "validator-prerequisite",
                completed=True,
                category="schema",
                evidence="equivalent-evidence: schema validated",
            ),
            continuation.CompletionItem(
                "pending", "validator-prerequisite", category="schema"
            ),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        ),
        prerequisite_resolutions=(resolution,),
    )

    result = continuation.drive_terminal(state, available_validators={"schema"})

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.state.prerequisite_resolutions == (resolution,)
    continuation.validate_completion_checklist(result.state)


@pytest.mark.parametrize(
    ("category", "expected_verdict"),
    [
        ("missing-authority", "BLOCKED ON DECISION"),
        ("material-decision", "BLOCKED ON DECISION"),
        ("external-state", "BLOCKED ON VERIFICATION"),
    ],
)
def test_true_blockers_are_terminal_and_do_not_run_internal_work(
    category: str, expected_verdict: str
) -> None:
    """Catches a blocker classification that silently promotes pending internal work."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("tasks", "task-promotion"),),
        blockers=(continuation.Blocker(category, "recorded prerequisite", ("tasks",)),),
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == expected_verdict
    assert result.completed_item_ids == ()
    assert result.state.terminal_verdict == expected_verdict


def test_completion_checklist_rejects_nonterminal_actionable_internal_work() -> None:
    """Catches a state recorder accepting a non-terminal pause with routine work left."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("state", "state-recording"),),
    )

    with pytest.raises(StateError, match="actionable internal checklist"):
        continuation.validate_completion_checklist(state)


@pytest.mark.parametrize("terminal_verdict", ["", "IN PROGRESS", "UNKNOWN VERDICT"])
def test_completion_checklist_rejects_pending_work_for_nonterminal_verdicts(
    terminal_verdict: str,
) -> None:
    """Catches arbitrary stored verdicts bypassing the actionable-work guard."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("state", "state-recording"),),
        terminal_verdict=terminal_verdict,
    )

    with pytest.raises(StateError, match="actionable internal checklist"):
        continuation.validate_completion_checklist(state)


def test_completion_checklist_rejects_unknown_terminal_verdict() -> None:
    """Catches persisted terminal labels outside the sidecar's verdict contract."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="full suite passed"
            ),
        ),
        terminal_verdict="UNKNOWN VERDICT",
    )

    with pytest.raises(ContractError, match="unknown terminal verdict"):
        continuation.validate_completion_checklist(state)


def test_completion_checklist_rejects_missing_terminal_verdict() -> None:
    """Catches a completed checklist being accepted without a persisted verdict."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="full suite passed"
            ),
        ),
    )

    with pytest.raises(ContractError, match="requires a terminal verdict"):
        continuation.validate_completion_checklist(state)


def test_completion_checklist_rejects_blocked_verdict_without_blockers() -> None:
    """Catches a blocked terminal label being trusted without blocker evidence."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("state", "state-recording"),),
        terminal_verdict="BLOCKED ON VERIFICATION",
    )

    with pytest.raises(StateError, match="requires blocker records"):
        continuation.validate_completion_checklist(state)


def test_completion_checklist_rejects_blocked_verdict_blocker_mismatch() -> None:
    """Catches a blocked terminal label disagreeing with blocker categories."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("state", "state-recording"),),
        blockers=(
            continuation.Blocker("missing-authority", "state needs authority", ("state",)),
        ),
        terminal_verdict="BLOCKED ON VERIFICATION",
    )

    with pytest.raises(StateError, match="must match blocker categories"):
        continuation.validate_completion_checklist(state)


def test_completion_checklist_rejects_pending_item_without_matching_blocker() -> None:
    """Catches blocked states that do not identify affected checklist items."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("state", "state-recording"),
            continuation.CompletionItem(
                "verify",
                "final-verification",
                completed=True,
                evidence="full suite passed",
            ),
        ),
        blockers=(
            continuation.Blocker("external-state", "validator unavailable", ("verify",)),
        ),
        terminal_verdict="BLOCKED ON VERIFICATION",
    )

    with pytest.raises(StateError, match="requires blockers for every incomplete"):
        continuation.validate_completion_checklist(state)


@pytest.mark.parametrize(
    ("terminal_verdict", "blockers", "error"),
    [
        (
            "IMPLEMENTATION COMPLETE",
            (continuation.Blocker("external-state", "validator unavailable", ("verify",)),),
            "completion verdict cannot retain blocker records",
        ),
        (
            "BLOCKED ON VERIFICATION",
            (continuation.Blocker("external-state", "validator unavailable", ("verify",)),),
            "blocked terminal verdict requires incomplete checklist items",
        ),
    ],
)
def test_completion_checklist_rejects_verdicts_contradicting_completed_state(
    terminal_verdict: str,
    blockers: tuple[continuation.Blocker, ...],
    error: str,
) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="full suite passed"
            ),
        ),
        blockers=blockers,
        terminal_verdict=terminal_verdict,
    )

    with pytest.raises(StateError, match=error):
        continuation.validate_completion_checklist(state)


@pytest.mark.parametrize("terminal_verdict", ["", "IN PROGRESS"])
def test_completion_checklist_rejects_unsupported_verdict_on_a_complete_checklist(
    terminal_verdict: str,
) -> None:
    """Catches a falsey or unsupported verdict passing terminal-state validation."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="full suite passed"
            ),
        ),
        terminal_verdict=terminal_verdict,
    )

    with pytest.raises(ContractError, match="unknown terminal verdict"):
        continuation.validate_completion_checklist(state)


@pytest.mark.parametrize("terminal_verdict", ["", "IN PROGRESS", "UNKNOWN VERDICT"])
def test_drive_terminal_rejects_unknown_persisted_terminal_verdict(
    terminal_verdict: str,
) -> None:
    """Catches malformed replay verdicts being normalized into a fresh success."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="full suite passed"
            ),
        ),
        terminal_verdict=terminal_verdict,
    )

    with pytest.raises(ContractError, match="unknown terminal verdict"):
        continuation.drive_terminal(state)


def test_drive_terminal_rejects_complete_verdict_with_pending_items() -> None:
    """Catches a corrupt terminal state being silently re-driven into another result."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),),
        terminal_verdict="IMPLEMENTATION COMPLETE",
    )

    with pytest.raises(StateError, match="completion verdict requires every checklist item"):
        continuation.drive_terminal(state)


def test_empty_checklist_is_rejected() -> None:
    """Catches a missing replay checklist bypassing every completion gate."""
    state = continuation.ContinuationState(checklist=())

    with pytest.raises(ContractError, match="explicit completion checklist"):
        continuation.validate_completion_checklist(state)

    with pytest.raises(ContractError, match="explicit completion checklist"):
        continuation.drive_terminal(state)


def test_unknown_blocker_category_is_rejected() -> None:
    """Catches accidental expansion of the blocker taxonomy beyond authorized stops."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("tasks", "task-promotion"),),
        blockers=(
            continuation.Blocker("routine-pause", "not a genuine blocker", ("tasks",)),
        ),
    )

    with pytest.raises(ContractError, match="unknown blocker category"):
        continuation.drive_terminal(state)


def test_unevidenced_pending_work_blocks_instead_of_claiming_completion() -> None:
    """Catches a drive loop that completes gates without a recorded action result."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("tasks", "task-promotion", evidence="T001 promoted"),
            continuation.CompletionItem("verify", "final-verification"),
        )
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == "BLOCKED ON VERIFICATION"
    assert result.completed_item_ids == ("tasks",)
    assert continuation.continuation_result_document(result)["completed_item_ids"] == ["tasks"]
    assert result.state.blockers[-1].category == "external-state"
    assert "verify" in result.state.blockers[-1].detail


def test_missing_evidence_persists_completed_gates_and_resumes_when_evidence_arrives() -> None:
    """Catches a missing-evidence stop discarding transitions or blocking permanently."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("tasks", "task-promotion", evidence="T001 promoted"),
            continuation.CompletionItem("verify", "final-verification"),
        )
    )

    blocked = continuation.drive_terminal(state)
    tasks_item = next(item for item in blocked.state.checklist if item.item_id == "tasks")
    resumed = continuation.drive_terminal(
        blocked.state, action_results={"verify": "full suite passed"}
    )

    assert blocked.verdict == "BLOCKED ON VERIFICATION"
    assert tasks_item.completed is True
    assert tasks_item.evidence == "T001 promoted"
    assert blocked.state.blockers[-1].derived is True
    assert resumed.verdict == "IMPLEMENTATION COMPLETE"
    assert resumed.completed_item_ids == ("verify",)
    assert resumed.state.blockers == ()


def test_missing_evidence_stops_before_later_ordered_gates() -> None:
    """Catches final verification being accepted before earlier task evidence exists."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task", "task"),
            continuation.CompletionItem(
                "verify", "final-verification", evidence="old suite", dependencies=("task",)
            ),
        )
    )

    blocked = continuation.drive_terminal(state)
    resumed = continuation.drive_terminal(blocked.state, action_results={"task": "T001 done"})
    verified = continuation.drive_terminal(
        resumed.state, action_results={"verify": "fresh suite passed"}
    )

    verify_after_block = next(item for item in blocked.state.checklist if item.item_id == "verify")
    verify_after_resume = next(item for item in resumed.state.checklist if item.item_id == "verify")
    assert blocked.verdict == "BLOCKED ON VERIFICATION"
    assert blocked.state.blockers[-1].detail == "no recorded transition evidence for: task"
    assert verify_after_block.completed is False
    assert verify_after_block.evidence is None
    assert resumed.verdict == "BLOCKED ON VERIFICATION"
    assert resumed.state.blockers[-1].detail == "no recorded transition evidence for: verify"
    assert verify_after_resume.completed is False
    assert verified.verdict == "IMPLEMENTATION COMPLETE"
    assert verified.completed_item_ids == ("verify",)


@pytest.mark.parametrize("completed", [False, True])
def test_earlier_gate_invalidates_completed_later_gates_until_fresh_evidence(completed: bool) -> None:
    """Catches stale completed final verification surviving a newly completed task."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task", "task"),
            continuation.CompletionItem(
                "verify", "final-verification", completed=completed, evidence="old suite",
                dependencies=("task",),
            ),
        )
    )

    result = continuation.drive_terminal(state, action_results={"task": "T001 done"})

    verify_item = next(item for item in result.state.checklist if item.item_id == "verify")
    assert result.verdict == "BLOCKED ON VERIFICATION"
    assert result.state.blockers[-1].detail == "no recorded transition evidence for: verify"
    assert verify_item.completed is False
    assert verify_item.evidence is None


@pytest.mark.parametrize("completed_id", ["a", "z"])
@pytest.mark.parametrize("action_results", [None, {"pending": "task accepted"}])
def test_pending_task_preserves_independent_completed_task_evidence(
    completed_id: str, action_results: dict[str, str] | None,
) -> None:
    completed = continuation.CompletionItem(
        completed_id, "task", completed=True, evidence="independent task accepted"
    )
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("pending", "task"),
            completed,
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        )
    )

    result = continuation.drive_terminal(state, action_results=action_results)

    assert result.state.checklist[1] == completed
    assert result.verdict == (
        "IMPLEMENTATION COMPLETE" if action_results else "BLOCKED ON VERIFICATION"
    )
    continuation.validate_completion_checklist(result.state)


def test_missing_task_evidence_preserves_same_kind_pending_evidence() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("a", "task"),
            continuation.CompletionItem("b", "task", evidence="independent task accepted"),
            continuation.CompletionItem("verify", "final-verification", evidence="full suite passed"),
        )
    )

    blocked = continuation.drive_terminal(state)
    resumed = continuation.drive_terminal(blocked.state, action_results={"a": "task accepted"})

    assert blocked.state.checklist[1].evidence == "independent task accepted"
    assert resumed.verdict == "IMPLEMENTATION COMPLETE"


def test_recorded_blocker_is_not_re_evaluated_by_new_evidence() -> None:
    """Catches a user-recorded stop being cleared by routine action results."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),),
        blockers=(
            continuation.Blocker(
                "material-decision", "Choose retention policy", ("verify",)
            ),
        ),
    )

    result = continuation.drive_terminal(
        state, action_results={"verify": "full suite passed"}
    )

    assert result.verdict == "BLOCKED ON DECISION"
    assert result.state.blockers == state.blockers
    assert result.completed_item_ids == ()


def test_recorded_blocker_does_not_stop_unaffected_actionable_work() -> None:
    """Catches a scoped blocker halting unrelated actionable checklist items."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("decision", "task"),
            continuation.CompletionItem("verify", "final-verification"),
        ),
        blockers=(
            continuation.Blocker(
                "material-decision", "Choose retention policy", ("decision",)
            ),
        ),
    )

    result = continuation.drive_terminal(
        state, action_results={"verify": "full suite passed"}
    )

    assert result.verdict == "BLOCKED ON DECISION"
    assert result.completed_item_ids == ("verify",)
    assert result.state.checklist[1].completed is True


def test_validator_blocker_preserves_decision_verdict_precedence() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("decision", "task"),
            continuation.CompletionItem(
                "validator", "validator-prerequisite", category="PyYAML"
            ),
        ),
        blockers=(
            continuation.Blocker(
                "material-decision", "Choose retention policy", ("decision",)
            ),
        ),
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == "BLOCKED ON DECISION"
    continuation.validate_completion_checklist(result.state)


def test_unevidenced_item_preserves_decision_verdict_precedence() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("decision", "task"),
            continuation.CompletionItem("verify", "final-verification"),
        ),
        blockers=(
            continuation.Blocker(
                "material-decision", "Choose retention policy", ("decision",)
            ),
        ),
    )

    result = continuation.drive_terminal(state)

    assert result.verdict == "BLOCKED ON DECISION"
    continuation.validate_completion_checklist(result.state)


def test_blocker_requires_explicit_affected_item_ids() -> None:
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),),
        blockers=(continuation.Blocker("external-state", "validator unavailable", ()),),
    )

    with pytest.raises(ContractError, match="explicit affected checklist item ids"):
        continuation.drive_terminal(state)


def test_action_result_evidence_completes_a_previously_unevidenced_gate() -> None:
    """Catches executed action results being ignored by the completion transition."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),)
    )

    result = continuation.drive_terminal(state, action_results={"verify": "full suite passed"})

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("verify",)
    assert result.state.checklist[0].evidence == "full suite passed"


def test_completed_item_without_evidence_is_rejected() -> None:
    """Catches a persisted checklist that claims completion without evidence."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification", completed=True),)
    )

    with pytest.raises(ContractError, match="require recorded acceptance evidence"):
        continuation.validate_completion_checklist(state)


def test_duplicate_item_ids_are_rejected() -> None:
    """Catches two gates sharing an item id, which would let evidence for one complete both."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("verify", "task"),
            continuation.CompletionItem("verify", "final-verification"),
        )
    )

    with pytest.raises(ContractError, match="completion checklist item ids must be unique"):
        continuation.validate_completion_checklist(state)


def test_empty_item_id_is_rejected() -> None:
    """Catches a direct-state checklist item with an empty item id."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("", "task", evidence="done"),)
    )

    with pytest.raises(ContractError, match="item_id must be a non-empty string"):
        continuation.validate_completion_checklist(state)


def test_direct_state_rejects_non_string_completion_kind() -> None:
    """Catches direct construction raising raw TypeError for unhashable kinds."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("task", ["task"], evidence="done"),)
    )

    with pytest.raises(ContractError, match="kind must be a non-empty string"):
        continuation.validate_completion_checklist(state)


@pytest.mark.parametrize("verdict", [[], {}, 0, False])
@pytest.mark.parametrize("completed", [True, False])
def test_direct_state_rejects_non_string_terminal_verdict(
    verdict: object, completed: bool,
) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "verify", "final-verification", completed=completed, evidence="suite passed"
            ),
        ),
        terminal_verdict=verdict,
    )

    for validate in (
        continuation.validate_completion_checklist,
        continuation.drive_terminal,
    ):
        with pytest.raises(ContractError) as caught:
            validate(state)
        assert caught.value.code == "unknown-terminal-verdict"


def test_direct_state_rejects_non_string_prerequisite_outcome() -> None:
    """Catches direct construction raising raw TypeError for unhashable outcomes."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "validator",
                "validator-prerequisite",
                category="PyYAML",
            ),
        ),
        prerequisite_resolutions=(
            continuation.PrerequisiteResolution("PyYAML", ["exact-validator"], "available"),
        ),
    )

    with pytest.raises(ContractError, match="requires category, outcome, and evidence"):
        continuation.drive_terminal(state)


def test_duplicate_prerequisite_resolution_categories_are_rejected() -> None:
    """Catches order-dependent last-one-wins prerequisite resolution collapse."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "validator",
                "validator-prerequisite",
                category="PyYAML",
            ),
        ),
        prerequisite_resolutions=(
            continuation.PrerequisiteResolution(
                "PyYAML",
                "exact-validator",
                "available validator: PyYAML",
            ),
            continuation.PrerequisiteResolution(
                "PyYAML",
                "unavailable",
                "no exact validator or equivalent evidence available",
            ),
        ),
    )

    with pytest.raises(ContractError, match="resolution categories must be unique"):
        continuation.drive_terminal(state)


@pytest.mark.parametrize("action_results", [{"verify": ""}, {"": "evidence"}, {"verify": 7}])
def test_malformed_action_results_are_rejected(action_results: object) -> None:
    """Catches malformed action results being treated as completion evidence."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),)
    )

    with pytest.raises(ContractError, match="action result requires"):
        continuation.drive_terminal(state, action_results=action_results)


@pytest.mark.parametrize("replay", [False, True])
@pytest.mark.parametrize("persisted_verdict", [None, "IMPLEMENTATION COMPLETE"])
@pytest.mark.parametrize("completed", [False, True])
def test_completion_requires_final_verification(
    replay: bool, persisted_verdict: str | None, completed: bool,
) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "task", "task", completed=completed, evidence="task accepted"
            ),
        ),
        terminal_verdict=persisted_verdict,
    )
    if replay:
        state = continuation.continuation_state_from_document(json.loads(json.dumps(asdict(state), default=list)))

    with pytest.raises(ContractError, match="final-verification"):
        continuation.drive_terminal(state)
    if persisted_verdict is not None:
        with pytest.raises(ContractError, match="final-verification"):
            continuation.validate_completion_checklist(state)


@pytest.mark.parametrize("replay", [False, True])
def test_derived_material_decision_is_not_discarded(replay: bool) -> None:
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),),
        blockers=(
            continuation.Blocker("material-decision", "Choose retention policy", ("verify",), True),
        ),
    )
    if replay:
        state = continuation.continuation_state_from_document(json.loads(json.dumps(asdict(state), default=list)))

    result = continuation.drive_terminal(state, action_results={"verify": "suite passed"})

    assert result.verdict == "BLOCKED ON DECISION"
    assert result.completed_item_ids == ()
    assert result.state.blockers == state.blockers
    continuation.validate_completion_checklist(result.state)


@pytest.mark.parametrize("completed", [False, True])
@pytest.mark.parametrize("action_results", [None, {"task-b": "slice B accepted"}])
@pytest.mark.parametrize("replay", [False, True])
def test_pending_slice_preserves_independent_review(
    completed: bool, action_results: dict[str, str] | None, replay: bool,
) -> None:
    review = continuation.CompletionItem(
        "review-a", "review", completed=completed, evidence="slice A reviewed",
        dependencies=("task-a",),
    )
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task-a", "task", completed=True, evidence="slice A accepted"),
            continuation.CompletionItem("task-b", "task"),
            review,
            continuation.CompletionItem("verify", "final-verification", dependencies=("review-a", "task-b")),
        ),
    )
    if replay:
        state = continuation.continuation_state_from_document(json.loads(json.dumps(asdict(state), default=list)))

    result = continuation.drive_terminal(state, action_results=action_results)

    assert result.state.checklist[2].evidence == review.evidence
    assert result.state.checklist[2].dependencies == review.dependencies
    assert result.state.checklist[2].completed is (completed or action_results is not None)
    continuation.validate_completion_checklist(result.state)


@pytest.mark.parametrize("completed", [False, True])
def test_pending_gate_invalidates_only_transitive_dependents(completed: bool) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("z", "task"),
            continuation.CompletionItem(
                "a", "task", completed=completed, evidence="old dependent task",
                dependencies=("z",),
            ),
            continuation.CompletionItem(
                "verify", "final-verification", completed=completed, evidence="old suite",
                dependencies=("a",),
            ),
        )
    )

    blocked = continuation.drive_terminal(state)

    assert all(item.evidence is None for item in blocked.state.checklist)
    continuation.validate_completion_checklist(blocked.state)
    resumed = continuation.drive_terminal(
        blocked.state, action_results={"z": "prerequisite accepted", "a": "dependent accepted", "verify": "fresh suite"},
    )
    assert resumed.completed_item_ids == ("z", "a", "verify")
    assert resumed.verdict == "IMPLEMENTATION COMPLETE"


@pytest.mark.parametrize(
    ("dependencies", "code"),
    [
        ("task", "completion-dependencies-invalid"),
        ((7,), "completion-dependencies-invalid"),
        (("missing",), "completion-dependency-unknown"),
        (("verify",), "completion-dependency-cycle"),
    ],
)
def test_invalid_dependencies_are_rejected(dependencies: object, code: str) -> None:
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification", dependencies=dependencies),)
    )

    with pytest.raises(ContractError) as caught:
        continuation.drive_terminal(state)
    assert caught.value.code == code


def test_dependency_cycle_is_rejected() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task", "task", dependencies=("verify",)),
            continuation.CompletionItem("verify", "final-verification", dependencies=("task",)),
        )
    )

    with pytest.raises(ContractError) as caught:
        continuation.drive_terminal(state)
    assert caught.value.code == "completion-dependency-cycle"


def test_recorded_blocker_covers_transitive_dependents_but_not_independent_work() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task", "task"),
            continuation.CompletionItem("review", "review", dependencies=("task",)),
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="old suite",
                dependencies=("review",),
            ),
            continuation.CompletionItem("independent", "task"),
        ),
        blockers=(continuation.Blocker("material-decision", "Choose policy", ("task",)),),
    )

    result = continuation.drive_terminal(
        state, action_results={item.item_id: "accepted" for item in state.checklist}
    )

    assert result.verdict == "BLOCKED ON DECISION"
    assert result.completed_item_ids == ("independent",)
    assert not result.state.checklist[2].completed
    assert set(result.state.blockers[0].affected_item_ids) == {"task", "review", "verify"}
    continuation.validate_completion_checklist(result.state)


@pytest.mark.parametrize("kind", ["protected-path-authorization", "validator-prerequisite"])
@pytest.mark.parametrize("prerequisite_available", [False, True])
def test_partial_preflight_progress_respects_dependencies(
    kind: str, prerequisite_available: bool,
) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("a-dependent", kind, category="dependent", dependencies=("z-prerequisite",)),
            continuation.CompletionItem("z-prerequisite", kind, category="prerequisite"),
            continuation.CompletionItem("missing", kind, category="missing"),
            continuation.CompletionItem("verify", "final-verification"),
        ),
    )
    available = {"dependent"}
    if prerequisite_available:
        available.add("prerequisite")

    result = continuation.drive_terminal(
        state,
        granted_authorizations={f"protected-path:{category}" for category in available},
        available_validators=available,
    )

    assert result.completed_item_ids == (
        ("z-prerequisite", "a-dependent") if prerequisite_available else ()
    )
    assert result.state.checklist[0].completed is prerequisite_available
    continuation.validate_completion_checklist(result.state)


def test_fresh_action_results_can_replace_stale_dependent_evidence() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task", "task"),
            continuation.CompletionItem(
                "verify", "final-verification", evidence="old suite", dependencies=("task",),
            ),
        ),
    )

    result = continuation.drive_terminal(
        state, action_results={"task": "task accepted", "verify": "fresh suite"},
    )

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("task", "verify")
    assert result.state.checklist[1].evidence == "fresh suite"


@pytest.mark.parametrize("field", ["granted_authorizations", "available_validators"])
@pytest.mark.parametrize(
    "value",
    [{"protected-path:scope": False}, "protected-path:scope", b"scope", True, 7, None, [""]],
)
def test_authorization_inputs_reject_malformed_collections(field: str, value: object) -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("path", "protected-path-authorization", category="scope"),
            continuation.CompletionItem("verify", "final-verification"),
        ),
    )

    with pytest.raises(ContractError) as caught:
        continuation.drive_terminal(state, **{field: value})
    assert caught.value.code == field.replace("_", "-") + "-invalid"


@pytest.mark.parametrize("value", [{"protected-path:scope": False}, "scope", True, [None], [" "]])
def test_persisted_grants_reject_malformed_collections(value: object) -> None:
    document = {
        "checklist": [{"item_id": "verify", "kind": "final-verification"}],
        "granted_authorizations": value,
    }

    with pytest.raises(ContractError) as caught:
        continuation.continuation_state_from_document(document)
    assert caught.value.code == "granted-authorizations-invalid"

    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),),
        granted_authorizations=value,
    )
    with pytest.raises(ContractError) as caught:
        continuation.drive_terminal(state)
    assert caught.value.code == "granted-authorizations-invalid"


def test_grant_survives_blocked_dependency_and_replay_resume() -> None:
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("validator", "validator-prerequisite", category="schema"),
            continuation.CompletionItem(
                "path", "protected-path-authorization", category="scope", dependencies=("validator",),
            ),
            continuation.CompletionItem("verify", "final-verification", dependencies=("path",)),
        ),
    )
    requested = continuation.drive_terminal(state)
    assert requested.authorization_requests == ("protected-path:scope",)

    blocked = continuation.drive_terminal(
        requested.state, granted_authorizations={"protected-path:scope"},
    )
    assert blocked.verdict == "BLOCKED ON VERIFICATION"
    assert not blocked.state.checklist[1].completed
    assert blocked.state.granted_authorizations == frozenset({"protected-path:scope"})
    continuation.validate_completion_checklist(blocked.state)

    restored = continuation.continuation_state_from_document(
        json.loads(json.dumps(asdict(blocked.state), default=list))
    )
    resumed = continuation.drive_terminal(
        restored, available_validators={"schema"}, action_results={"verify": "fresh suite"},
    )
    assert resumed.authorization_requests == ()
    assert resumed.completed_item_ids == ("validator", "path", "verify")
    assert resumed.verdict == "IMPLEMENTATION COMPLETE"


@pytest.mark.parametrize(
    "kind",
    ["task", "review", "review-correction", "task-promotion", "state-recording", "convergence", "after-hook"],
)
@pytest.mark.parametrize("completed", [False, True])
@pytest.mark.parametrize("transitive", [False, True])
def test_routine_work_cannot_depend_on_final_verification(
    kind: str, completed: bool, transitive: bool,
) -> None:
    checklist = (
        continuation.CompletionItem(
            "verify", "final-verification", completed=completed,
            evidence="old suite" if completed else None,
        ),
        continuation.CompletionItem(
            "work", kind, dependencies=("path" if transitive else "verify",),
        ),
    )
    if transitive:
        checklist += (
            continuation.CompletionItem(
                "path", "protected-path-authorization", category="scope", dependencies=("verify",),
            ),
        )
    state = continuation.ContinuationState(checklist=checklist)

    with pytest.raises(ContractError) as caught:
        continuation.drive_terminal(state, action_results={"work": "mutation accepted"})
    assert caught.value.code == "completion-final-verification-dependency-invalid"
