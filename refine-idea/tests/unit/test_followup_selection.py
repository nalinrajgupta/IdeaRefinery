from __future__ import annotations

from idea_refinery.coverage import (
    CoverageMatrix,
    RoleAvailability,
    derive_coverage_taxonomy,
    select_followup,
)
from idea_refinery.synthesis import Disposition, evaluate_readiness


def _blind_spot_matrix(*areas: str) -> CoverageMatrix:
    items = [item for item in derive_coverage_taxonomy([]) if item.area in areas]
    matrix = CoverageMatrix.from_items(items)
    for item in items:
        matrix.apply_attestation(
            {
                "coverage_id": item.coverage_id,
                "applicable": True,
                "reviewed": False,
                "evidence": [],
                "finding_ids": [],
            },
            reviewer=item.primary_role,
        )
    return matrix


def test_primary_owner_receives_exactly_one_high_risk_followup() -> None:
    matrix = _blind_spot_matrix("security", "reliability")

    request = select_followup(
        matrix,
        {
            "architect": RoleAvailability(),
            "product": RoleAvailability(),
            "ceo": RoleAvailability(),
        },
    )

    assert request is not None
    assert request.role == "architect"
    assert request.coverage_ids == ("COV-004",)
    assert request.rationale == "primary owner available"
    assert len(matrix.followups) == 1
    assert select_followup(matrix, {}) is None


def test_failed_primary_falls_back_to_secondary_owner() -> None:
    matrix = _blind_spot_matrix("security")

    request = select_followup(
        matrix,
        {
            "architect": RoleAvailability(failed=True),
            "product": RoleAvailability(),
        },
    )

    assert request is not None
    assert request.role == "product"
    assert request.rationale == "primary unavailable; secondary owner available"


def test_tie_break_prefers_first_nondegraded_role_with_declared_scope() -> None:
    matrix = _blind_spot_matrix("security")

    request = select_followup(
        matrix,
        {
            "architect": RoleAvailability(failed=True),
            "product": RoleAvailability(failed=True),
            "ceo": RoleAvailability(scopes=frozenset({"security"}), degraded=True),
            "eval": RoleAvailability(scopes=frozenset({"security"})),
        },
    )

    assert request is not None
    assert request.role == "eval"
    assert request.rationale == "scope tie-break selected first non-degraded role"


def test_readiness_requires_dispositions_for_findings_and_blind_spots() -> None:
    matrix = _blind_spot_matrix("security")

    blocked = evaluate_readiness(matrix, finding_dispositions={"ROOT-1": None})
    assert blocked.verdict == "BLOCKED ON DECISION"
    assert blocked.undispositioned == ("COV-005", "ROOT-1")

    ready = evaluate_readiness(
        matrix,
        finding_dispositions={"ROOT-1": Disposition.ACCEPTED},
        blind_spot_dispositions={
            "COV-005": Disposition.DEFERRED,
        },
    )
    assert ready.verdict == "READY FOR IMPLEMENTATION"
    assert ready.undispositioned == ()
