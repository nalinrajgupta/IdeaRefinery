from __future__ import annotations

import copy

import pytest

from idea_refinery.envelopes import validate_review_envelope
from idea_refinery.errors import ContractError


def valid_envelope() -> dict:
    return {
        "schema_version": "1.0",
        "envelope_id": "ENV-ceo-1",
        "run_id": "run-1",
        "brief_id": "brief-1",
        "role": "ceo",
        "model": "gpt-5.5",
        "reasoning_effort": "high",
        "attempt": 1,
        "status": "completed",
        "input_hashes": {"spec": "a" * 64},
        "protected_artifact_hashes": {"spec.md": "a" * 64},
        "findings": [],
        "coverage_attestations": [
            {
                "coverage_id": "COV-001",
                "applicable": True,
                "reviewed": True,
                "evidence": ["spec.md#user-value"],
                "finding_ids": [],
            }
        ],
    }


def test_completed_envelope_matches_dispatch_and_assigned_coverage() -> None:
    envelope = valid_envelope()
    validate_review_envelope(
        envelope,
        dispatch={"role": "ceo", "model": "gpt-5.5", "reasoning_effort": "high", "brief_id": "brief-1"},
        assigned_coverage={"COV-001"},
        protected_hashes={"spec.md": "a" * 64},
    )


@pytest.mark.parametrize("mutation,code", [
    (lambda value: value["coverage_attestations"].clear(), "coverage-incomplete"),
    (lambda value: value.update(model="wrong"), "dispatch-mismatch"),
    (lambda value: value["protected_artifact_hashes"].update({"spec.md": "b" * 64}), "protected-artifact-drift"),
])
def test_invalid_envelopes_are_rejected(mutation, code) -> None:
    envelope = copy.deepcopy(valid_envelope())
    mutation(envelope)
    with pytest.raises(ContractError) as caught:
        validate_review_envelope(
            envelope,
            dispatch={"role": "ceo", "model": "gpt-5.5", "reasoning_effort": "high", "brief_id": "brief-1"},
            assigned_coverage={"COV-001"},
            protected_hashes={"spec.md": "a" * 64},
        )
    assert caught.value.code == code
