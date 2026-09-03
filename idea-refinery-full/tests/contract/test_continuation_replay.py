from __future__ import annotations

from pathlib import Path

import pytest

from idea_refinery import continuation
from idea_refinery.errors import ContractError


REPLAY_ROOT = Path(__file__).parents[1] / "fixtures" / "replay"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "continuation-review-finding",
        "continuation-pending-work",
        "continuation-protected-path",
        "continuation-missing-validator",
        "continuation-equivalent-evidence",
        "continuation-true-blocker",
    ],
)
def test_continuation_replay_fixtures_match_terminal_drive_contract(fixture_name: str) -> None:
    """Catches replay drift in a listed continuity pause cause."""
    result = continuation.replay_continuation_fixture(REPLAY_ROOT / fixture_name)

    assert result["passed"] is True


@pytest.mark.parametrize("kind", ["protected-path-authorization", "validator-prerequisite"])
def test_preflight_gate_requires_a_scoped_category(kind: str) -> None:
    """Catches a preflight request that would ask for authority without a target."""
    state = continuation.ContinuationState(
        checklist=(continuation.CompletionItem("preflight", kind),),
    )

    with pytest.raises(ContractError, match="completion category is required"):
        continuation.drive_terminal(state)


@pytest.mark.parametrize(
    ("document", "code"),
    [
        (
            {
                "checklist": [
                    {
                        "item_id": "path",
                        "kind": "protected-path-authorization",
                        "category": "specs/004/tasks.md",
                        "completed": "false",
                    }
                ]
            },
            "completion-completed-invalid",
        ),
        (
            {
                "checklist": [
                    {
                        "item_id": "validator",
                        "kind": "validator-prerequisite",
                        "category": "PyYAML",
                        "completed": "false",
                    }
                ]
            },
            "completion-completed-invalid",
        ),
        (
            {"checklist": [{"item_id": "", "kind": "task-promotion"}]},
            "completion-item-id-invalid",
        ),
        (
            {"checklist": [{"item_id": "tasks", "kind": ""}]},
            "completion-kind-invalid",
        ),
        (
            {
                "checklist": [
                    {
                        "item_id": "path",
                        "kind": "protected-path-authorization",
                        "category": "",
                    }
                ]
            },
            "completion-category-invalid",
        ),
    ],
)
def test_replay_document_rejects_malformed_completion_fields(
    document: dict[str, object], code: str
) -> None:
    """Catches replay parsing that turns malformed gates into skipped work."""
    with pytest.raises(ContractError) as caught:
        continuation.continuation_state_from_document(document)

    assert caught.value.code == code


@pytest.mark.parametrize(
    "resolution",
    [
        {"category": "", "outcome": "equivalent-evidence", "evidence": "recorded"},
        {"category": "PyYAML", "outcome": "equivalent-evidence", "evidence": 7},
        {"category": "PyYAML", "outcome": "not-a-resolution", "evidence": "recorded"},
    ],
)
def test_replay_document_rejects_malformed_prerequisite_resolution(
    resolution: dict[str, object],
) -> None:
    """Catches malformed evidence records being accepted as validator remediation."""
    document = {"prerequisite_resolutions": [resolution]}

    with pytest.raises(ContractError):
        continuation.continuation_state_from_document(document)


def test_replay_document_rejects_non_string_terminal_verdict() -> None:
    """Catches a falsey non-string verdict bypassing terminal-state validation."""
    with pytest.raises(ContractError, match="terminal verdict must be a string"):
        continuation.continuation_state_from_document({"terminal_verdict": []})


@pytest.mark.parametrize(
    ("blockers", "code"),
    [
        ("bad", "blockers-invalid"),
        ([{}], "blocker-category-invalid"),
        ([{"category": "", "detail": "missing authority"}], "blocker-category-invalid"),
        ([{"category": "missing-authority", "detail": ""}], "blocker-detail-invalid"),
        ([{"category": "routine-pause", "detail": "not a real blocker"}], "unknown-blocker-category"),
    ],
)
def test_replay_document_rejects_malformed_or_unsupported_blockers(
    blockers: object, code: str
) -> None:
    """Catches JSON parsing errors and arbitrary stop categories at the blocker boundary."""
    with pytest.raises(ContractError) as caught:
        continuation.continuation_state_from_document({"blockers": blockers})

    assert caught.value.code == code
