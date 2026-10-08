from __future__ import annotations

from idea_refinery.briefs import prepare_stage_brief
from idea_refinery.config import resolve_config
from idea_refinery.envelopes import validate_review_envelope


def test_three_roles_receive_independent_frozen_briefs(full_roster) -> None:
    resolved = resolve_config(full_roster)
    briefs = {
        role: prepare_stage_brief(
            run_id="run-1",
            stage="review",
            role=role,
            objective=f"Review as {role}",
            coverage_assignments=[f"COV-00{index}"],
            artifact_hashes={"spec.md": "a" * 64},
        )
        for index, role in enumerate(("ceo", "product", "architect"), 1)
    }
    assert len({brief["brief_id"] for brief in briefs.values()}) == 3
    assert all("findings" not in brief for brief in briefs.values())
    for index, role in enumerate(("ceo", "product", "architect"), 1):
        assignment = resolved["roles"][role]
        envelope = {
            "schema_version": "1.0",
            "envelope_id": f"ENV-{role}-1",
            "run_id": "run-1",
            "brief_id": briefs[role]["brief_id"],
            "role": role,
            "model": assignment["selected_model"],
            "reasoning_effort": assignment["selected_reasoning_effort"],
            "attempt": 1,
            "status": "completed",
            "input_hashes": {"spec": "a" * 64},
            "protected_artifact_hashes": {"spec.md": "a" * 64},
            "findings": [],
            "coverage_attestations": [{"coverage_id": f"COV-00{index}", "applicable": True, "reviewed": True, "evidence": ["spec.md"], "finding_ids": []}],
        }
        validate_review_envelope(
            envelope,
            dispatch={"role": role, "model": assignment["selected_model"], "reasoning_effort": assignment["selected_reasoning_effort"], "brief_id": briefs[role]["brief_id"]},
            assigned_coverage={f"COV-00{index}"},
            protected_hashes={"spec.md": "a" * 64},
        )
