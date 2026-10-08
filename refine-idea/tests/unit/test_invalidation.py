from __future__ import annotations

import pytest

from idea_refinery.invalidation import (
    ChangeKind,
    artifact_key,
    calculate_invalidation,
    classify_change,
)


def test_spec_change_invalidates_complete_downstream_dag() -> None:
    assert calculate_invalidation({"spec.md"}) == {
        "spec",
        "plan",
        "research",
        "data-model",
        "contracts",
        "quickstart",
        "tasks",
        "analysis",
    }


def test_supporting_artifact_only_invalidates_tasks_and_analysis() -> None:
    assert calculate_invalidation({"contracts/review-result.schema.json"}) == {
        "contracts",
        "tasks",
        "analysis",
    }


def test_tasks_change_does_not_invalidate_upstream_artifacts() -> None:
    assert calculate_invalidation({"tasks.md"}) == {"tasks", "analysis"}


def test_multiple_changes_are_deduplicated_and_deterministic() -> None:
    expected = calculate_invalidation({"plan.md", "data-model.md"})
    assert expected == {"plan", "data-model", "tasks", "analysis"}
    assert calculate_invalidation({"data-model", "plan"}) == expected


def test_artifact_paths_are_normalized() -> None:
    assert artifact_key("contracts/config.schema.json") == "contracts"
    assert artifact_key("analysis/report.md") == "analysis"
    with pytest.raises(ValueError, match="unknown Spec Kit artifact"):
        artifact_key("README.md")


def test_accepted_clarification_is_a_spec_change_not_a_repair() -> None:
    change = classify_change("accepted-clarification", {"spec.md"})
    assert change.kind is ChangeKind.SPEC_UPDATE
    assert change.repair_eligible is False
    assert change.invalidated == calculate_invalidation({"spec.md"})


def test_constitution_change_requires_separate_decision() -> None:
    change = classify_change("analysis-finding", {"constitution.md"})
    assert change.kind is ChangeKind.SEPARATE_USER_DECISION
    assert change.repair_eligible is False


def test_analysis_finding_is_repair_eligible_for_regular_artifact() -> None:
    change = classify_change("analysis-finding", {"plan.md"})
    assert change.kind is ChangeKind.REPAIR
    assert change.repair_eligible is True

