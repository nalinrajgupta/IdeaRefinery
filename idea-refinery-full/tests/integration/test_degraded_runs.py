from __future__ import annotations

from idea_refinery.readiness import assess_readiness


def _gates() -> dict[str, object]:
    return {
        "coverage_items": [{"id": "COV-1", "risk": "high", "applicable": True, "disposition": "reviewed-no-finding", "evidence": ["spec:1"]}],
        "findings": [],
        "repair_history": [],
        "traceability_passed": True,
    }


def test_fallback_completion_is_ready_but_reported_as_degraded() -> None:
    result = assess_readiness(
        roles={"ceo": "completed", "product": "degraded-fallback", "architect": "completed"},
        **_gates(),
    )

    assert result["verdict"] == "READY FOR IMPLEMENTATION"
    assert result["degraded_roles"] == ["product"]


def test_exhausted_role_blocks_until_matching_explicit_waiver() -> None:
    blocked = assess_readiness(
        roles={"ceo": "completed", "product": "failed-role", "architect": "completed"},
        **_gates(),
    )
    assert blocked["verdict"] == "BLOCKED ON DECISION"
    assert blocked["failed_roles"] == ["product"]

    waived = assess_readiness(
        roles={"ceo": "completed", "product": "failed-role", "architect": "completed"},
        waiver={"missing_role": "product", "affected_coverage_ids": ["COV-2"], "owner": "Nalin", "rationale": "Accepted for this bounded run"},
        **_gates(),
    )
    assert waived["verdict"] == "READY FOR IMPLEMENTATION — DEGRADED"
    assert waived["waived_perspective"]["owner"] == "Nalin"


def test_drift_abort_or_exhausted_retry_is_never_silently_ready() -> None:
    for status in ("rejected-drift", "retrying", "timed-out"):
        result = assess_readiness(
            roles={"ceo": status, "product": "completed", "architect": "completed"},
            **_gates(),
        )
        assert result["verdict"] == "BLOCKED ON DECISION"
