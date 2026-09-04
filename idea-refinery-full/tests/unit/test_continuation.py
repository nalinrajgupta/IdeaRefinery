from __future__ import annotations

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
        )
    )

    result = continuation.drive_terminal(
        state,
        granted_authorizations={"protected-path:specs/004/tasks.md"},
    )

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("tasks-output", "tasks")


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
        )
    )

    first = continuation.drive_terminal(
        state,
        granted_authorizations={"protected-path:specs/004/tasks.md"},
    )
    resolved = continuation.drive_terminal(first.state, available_validators={"PyYAML"})

    assert first.verdict == "BLOCKED ON VERIFICATION"
    tasks_output_item = next(
        item for item in first.state.checklist if item.item_id == "tasks-output"
    )
    assert tasks_output_item.completed is True
    assert tasks_output_item.evidence == "authorization granted: protected-path:specs/004/tasks.md"
    assert resolved.verdict == "IMPLEMENTATION COMPLETE"
    assert resolved.completed_item_ids == ("validator",)


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
        blockers=(continuation.Blocker(category, "recorded prerequisite"),),
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
        blockers=(continuation.Blocker("missing-authority", "state needs authority"),),
        terminal_verdict="BLOCKED ON VERIFICATION",
    )

    with pytest.raises(StateError, match="must match blocker categories"):
        continuation.validate_completion_checklist(state)


def test_completion_checklist_rejects_pending_item_without_matching_blocker() -> None:
    """Catches blocked states that do not identify affected checklist items."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("state", "state-recording"),),
        blockers=(continuation.Blocker("external-state", "validator unavailable"),),
        terminal_verdict="BLOCKED ON VERIFICATION",
    )

    with pytest.raises(StateError, match="requires blockers for every incomplete"):
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
        blockers=(continuation.Blocker("routine-pause", "not a genuine blocker"),),
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
    assert result.completed_item_ids == ()
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
            continuation.CompletionItem("verify", "final-verification", evidence="old suite"),
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


def test_earlier_gate_invalidates_completed_later_gates_until_fresh_evidence() -> None:
    """Catches stale completed final verification surviving a newly completed task."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("task", "task"),
            continuation.CompletionItem(
                "verify", "final-verification", completed=True, evidence="old suite"
            ),
        )
    )

    result = continuation.drive_terminal(state, action_results={"task": "T001 done"})

    verify_item = next(item for item in result.state.checklist if item.item_id == "verify")
    assert result.verdict == "BLOCKED ON VERIFICATION"
    assert result.state.blockers[-1].detail == "no recorded transition evidence for: verify"
    assert verify_item.completed is False
    assert verify_item.evidence is None


def test_recorded_blocker_is_not_re_evaluated_by_new_evidence() -> None:
    """Catches a user-recorded stop being cleared by routine action results."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("verify", "final-verification"),),
        blockers=(continuation.Blocker("material-decision", "Choose retention policy"),),
    )

    result = continuation.drive_terminal(
        state, action_results={"verify": "full suite passed"}
    )

    assert result.verdict == "BLOCKED ON DECISION"
    assert result.state.blockers == state.blockers
    assert result.completed_item_ids == ()


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
