from __future__ import annotations

import json
from pathlib import Path

import pytest

from idea_refinery.coverage import (
    CoverageMatrix,
    CoverageState,
    derive_coverage_taxonomy,
)


def test_taxonomy_derivation_is_stable_and_maps_requirements() -> None:
    requirements = [
        {"id": "FR-015", "areas": ["requirements", "tests"]},
        {"id": "FR-019", "areas": ["reliability", "tests"]},
        {"id": "FR-020", "areas": ["operations"]},
    ]

    forward = derive_coverage_taxonomy(requirements)
    reverse = derive_coverage_taxonomy(reversed(requirements))

    assert [item.coverage_id for item in forward] == [
        "COV-001",
        "COV-002",
        "COV-003",
        "COV-004",
        "COV-005",
        "COV-006",
        "COV-007",
        "COV-008",
        "COV-009",
    ]
    assert forward == reverse
    tests = next(item for item in forward if item.area == "tests")
    assert tests.requirement_ids == ("FR-015", "FR-019")
    assert tests.primary_role == "architect"
    assert tests.secondary_role == "product"


def test_matrix_requires_evidence_for_applicable_high_risk_items() -> None:
    item = next(
        item
        for item in derive_coverage_taxonomy([])
        if item.area == "reliability"
    )
    matrix = CoverageMatrix.from_items([item])

    matrix.apply_attestation(
        {
            "coverage_id": item.coverage_id,
            "applicable": True,
            "reviewed": True,
            "evidence": [],
            "finding_ids": [],
        },
        reviewer="architect",
    )

    entry = matrix[item.coverage_id]
    assert entry.state is CoverageState.BLIND_SPOT
    assert not entry.is_successful


def test_matrix_distinguishes_inapplicable_no_finding_and_finding_states() -> None:
    journeys, requirements, interfaces = derive_coverage_taxonomy([])[:3]
    matrix = CoverageMatrix.from_items([journeys, requirements, interfaces])

    matrix.apply_attestation(
        {
            "coverage_id": journeys.coverage_id,
            "applicable": False,
            "reviewed": False,
            "evidence": [],
            "finding_ids": [],
        },
        reviewer="product",
    )
    matrix.apply_attestation(
        {
            "coverage_id": requirements.coverage_id,
            "applicable": True,
            "reviewed": True,
            "evidence": ["spec.md#FR-015"],
            "finding_ids": [],
        },
        reviewer="product",
    )
    matrix.apply_attestation(
        {
            "coverage_id": interfaces.coverage_id,
            "applicable": True,
            "reviewed": True,
            "evidence": ["contracts/review-result.schema.json"],
            "finding_ids": ["A-1"],
        },
        reviewer="architect",
    )

    assert matrix[journeys.coverage_id].state is CoverageState.INAPPLICABLE
    assert matrix[requirements.coverage_id].state is CoverageState.REVIEWED_NO_FINDING
    assert matrix[interfaces.coverage_id].state is CoverageState.FINDING_RAISED
    assert matrix[interfaces.coverage_id].finding_ids == ("A-1",)


def test_invalid_transition_and_unknown_coverage_are_rejected() -> None:
    item = derive_coverage_taxonomy([])[0]
    matrix = CoverageMatrix.from_items([item])
    matrix.apply_attestation(
        {
            "coverage_id": item.coverage_id,
            "applicable": False,
            "reviewed": False,
            "evidence": [],
            "finding_ids": [],
        },
        reviewer="product",
    )

    with pytest.raises(ValueError, match="terminal"):
        matrix.apply_attestation(
            {
                "coverage_id": item.coverage_id,
                "applicable": True,
                "reviewed": True,
                "evidence": ["later evidence"],
                "finding_ids": [],
            },
            reviewer="product",
        )
    with pytest.raises(KeyError, match="COV-999"):
        matrix.apply_attestation(
            {
                "coverage_id": "COV-999",
                "applicable": True,
                "reviewed": True,
                "evidence": ["evidence"],
                "finding_ids": [],
            },
            reviewer="product",
        )


def test_seeded_coverage_gap_replay_matches_expected_matrix() -> None:
    fixture = (
        Path(__file__).parents[1]
        / "fixtures"
        / "replay"
        / "coverage-gap"
    )
    source = json.loads((fixture / "input.json").read_text(encoding="utf-8"))
    expected = json.loads((fixture / "expected-matrix.json").read_text(encoding="utf-8"))
    items = derive_coverage_taxonomy(source["requirements"])
    matrix = CoverageMatrix.from_items(items)
    for envelope in source["envelopes"]:
        matrix.aggregate(envelope["coverage_attestations"], envelope["role"])

    assert matrix.as_dict() == expected
