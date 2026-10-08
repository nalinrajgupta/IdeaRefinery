from __future__ import annotations

import pytest

from idea_refinery.findings import (
    canonicalize_findings,
    completion_criterion_identity,
    validate_lineage,
)


def _finding(
    local_id: str,
    reviewer: str,
    summary: str,
    criterion: str,
    *,
    evidence: str,
    caused_by: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "local_id": local_id,
        "reviewer": reviewer,
        "severity": "high",
        "summary": summary,
        "evidence": [evidence],
        "coverage_ids": ["COV-004"],
        "affected_requirement_ids": ["FR-017"],
        "artifact_paths": ["spec.md"],
        "completion_criterion": criterion,
        "caused_by": list(caused_by),
        "supersedes": [],
    }


def test_semantic_duplicates_merge_without_losing_attribution_or_evidence() -> None:
    findings = [
        _finding(
            "P-1",
            "product",
            "Duplicate issues get separate budgets",
            "Aliases retain the same repair budget",
            evidence="spec.md:210",
        ),
        _finding(
            "A-7",
            "architect",
            "Rewording can reset repair count",
            "alias findings keep one repair budget",
            evidence="data-model.md:91",
        ),
    ]

    roots = canonicalize_findings(
        findings,
        criterion_aliases={
            "alias findings keep one repair budget": "aliases retain the same repair budget"
        },
    )

    assert len(roots) == 1
    root = roots[0]
    assert root.aliases == ("A-7", "P-1")
    assert root.reviewers == ("architect", "product")
    assert root.evidence == ("data-model.md:91", "spec.md:210")
    assert root.coverage_ids == ("COV-004",)


def test_root_identity_uses_requirements_artifacts_and_completion_criterion() -> None:
    first = completion_criterion_identity(
        ["FR-017", "FR-016"],
        ["./spec.md", "contracts/../spec.md"],
        "  Preserve   ALL aliases. ",
    )
    same = completion_criterion_identity(
        ["FR-016", "FR-017"],
        ["spec.md"],
        "preserve all aliases",
    )
    changed = completion_criterion_identity(
        ["FR-016", "FR-017"],
        ["spec.md"],
        "preserve evidence",
    )

    assert first == same
    assert first.startswith("ROOT-")
    assert changed != first


def test_aliases_do_not_create_additional_roots() -> None:
    original = _finding(
        "A-1", "architect", "Missing proof", "record proof", evidence="one"
    )
    alias = dict(original, local_id="A-2", summary="No evidence", evidence=["two"])

    roots = canonicalize_findings([original, alias])

    assert len(roots) == 1
    assert roots[0].aliases == ("A-1", "A-2")


def test_lineage_accepts_acyclic_edges_and_rejects_cycles() -> None:
    roots = canonicalize_findings(
        [
            _finding("A-1", "architect", "first", "criterion one", evidence="one"),
            _finding("A-2", "architect", "second", "criterion two", evidence="two"),
        ]
    )
    first, second = roots
    acyclic = [first, second.with_lineage(caused_by=(first.root_id,))]
    validate_lineage(acyclic)

    cyclic = [
        first.with_lineage(caused_by=(second.root_id,)),
        second.with_lineage(caused_by=(first.root_id,)),
    ]
    with pytest.raises(ValueError, match="cycle"):
        validate_lineage(cyclic)
