from __future__ import annotations

import pytest

from idea_refinery import continuation
from idea_refinery.errors import ContractError, StateError


def test_drive_terminal_completes_all_internal_checklist_items_in_order() -> None:
    """Catches a drive loop that exits before routine completion work is done."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem("verify", "final-verification"),
            continuation.CompletionItem("review", "review-correction"),
            continuation.CompletionItem("state", "state-recording"),
            continuation.CompletionItem("tasks", "task-promotion"),
            continuation.CompletionItem("converge", "convergence"),
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

    result = continuation.drive_terminal(state)

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
            continuation.CompletionItem("tasks", "task-promotion"),
        )
    )

    result = continuation.drive_terminal(
        state,
        granted_authorizations={"protected-path:specs/004/tasks.md"},
    )

    assert result.verdict == "IMPLEMENTATION COMPLETE"
    assert result.completed_item_ids == ("tasks-output", "tasks")


def test_missing_validator_is_an_external_blocker_with_one_remediation_request() -> None:
    """Catches validation being skipped or repeatedly requesting the same prerequisite."""
    state = continuation.ContinuationState(
        checklist=(
            continuation.CompletionItem(
                "validator",
                "validator-prerequisite",
                category="PyYAML",
            ),
            continuation.CompletionItem("verify", "final-verification"),
        )
    )

    first = continuation.drive_terminal(state)
    second = continuation.drive_terminal(first.state)
    resolved = continuation.drive_terminal(first.state, available_validators={"PyYAML"})

    assert first.verdict == "BLOCKED ON VERIFICATION"
    assert first.authorization_requests == ("validator:PyYAML",)
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
            continuation.CompletionItem("verify", "final-verification"),
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
    state = continuation.ContinuationState(checklist=(), terminal_verdict="UNKNOWN VERDICT")

    with pytest.raises(ContractError, match="unknown terminal verdict"):
        continuation.validate_completion_checklist(state)


def test_unknown_blocker_category_is_rejected() -> None:
    """Catches accidental expansion of the blocker taxonomy beyond authorized stops."""
    state = continuation.ContinuationState(
        checklist=(),
        blockers=(continuation.Blocker("routine-pause", "not a genuine blocker"),),
    )

    with pytest.raises(ContractError, match="unknown blocker category"):
        continuation.drive_terminal(state)
