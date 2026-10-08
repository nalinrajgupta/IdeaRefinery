from __future__ import annotations

import time

import pytest

from idea_refinery.config import resolve_config
from idea_refinery.envelopes import validate_review_envelope


@pytest.mark.performance
def test_representative_validation_stays_under_250ms(full_roster) -> None:
    envelope = {
        "schema_version": "1.0", "envelope_id": "ENV-perf", "run_id": "run-1", "brief_id": "brief-1",
        "role": "ceo", "model": "gpt-5.5", "reasoning_effort": "high", "attempt": 1,
        "status": "completed", "input_hashes": {"spec": "a" * 64},
        "protected_artifact_hashes": {"spec.md": "a" * 64}, "findings": [],
        "coverage_attestations": [{"coverage_id": "COV-001", "applicable": True, "reviewed": True, "evidence": ["spec.md"], "finding_ids": []}],
    }
    resolved = resolve_config(full_roster)
    assignment = resolved["roles"]["ceo"]
    envelope["model"] = assignment["selected_model"]
    envelope["reasoning_effort"] = assignment["selected_reasoning_effort"]
    dispatch = {
        "role": "ceo",
        "model": envelope["model"],
        "reasoning_effort": envelope["reasoning_effort"],
        "brief_id": "brief-1",
    }

    start = time.perf_counter()
    for _ in range(50):
        validate_review_envelope(envelope, dispatch=dispatch, assigned_coverage={"COV-001"}, protected_hashes={"spec.md": "a" * 64})
    assert (time.perf_counter() - start) < 0.25
