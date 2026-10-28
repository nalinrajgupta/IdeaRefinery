from __future__ import annotations

from idea_refinery.evals.scoring import compare_profiles, score_bundle
from idea_refinery.evals.traceability import check_traceability


def test_scores_all_required_quality_dimensions() -> None:
    bundle = {
        "seeded_findings": ["seed-a", "seed-b"],
        "findings": [
            {"seed_id": "seed-a", "supported": True, "reviewer": "ceo"},
            {"seed_id": "seed-b", "supported": True, "reviewer": "architect"},
            {"supported": False, "reviewer": "product"},
        ],
        "coverage_items": [
            {"applicable": True, "reviewed": True, "evidence": ["spec:10"]},
            {"applicable": True, "reviewed": False, "evidence": []},
            {"applicable": False, "reviewed": False, "evidence": []},
        ],
        "questions": [
            {"canonical_id": "Q-1", "necessary": True},
            {"canonical_id": "Q-1", "necessary": False},
            {"canonical_id": "Q-2", "necessary": True},
        ],
        "repairs": [
            {"root_id": "ROOT-1", "risk_delta": "decreased", "status": "promoted"},
            {"root_id": "ROOT-2", "risk_delta": "unchanged", "status": "stopped"},
        ],
        "traceability": {"mapped_requirements": 4, "total_requirements": 5, "mapped_tasks": 8, "total_tasks": 10},
        "latency_seconds": 12.5,
        "effort": {"tokens": 1200, "worker_seconds": 24.0},
        "downstream_material_decisions": 1,
    }

    result = score_bundle(bundle)

    assert result["seeded_finding_recall"] == 1.0
    assert result["unsupported_claim_rate"] == 1 / 3
    assert result["reviewer_diversity"] == 1.0
    assert result["coverage_completeness"] == 0.5
    assert result["unnecessary_question_rate"] == 1 / 3
    assert result["repair_convergence"] == 0.5
    assert result["requirement_task_traceability"] == 0.8
    assert result["latency_seconds"] == 12.5
    assert result["effort"] == {"tokens": 1200, "worker_seconds": 24.0}
    assert result["downstream_material_decisions"] == 1


def test_profile_comparison_uses_percentage_point_deltas() -> None:
    comparison = compare_profiles(
        {"seeded_finding_recall": 0.8, "unsupported_claim_rate": 0.1, "latency_seconds": 7},
        {"seeded_finding_recall": 0.6, "unsupported_claim_rate": 0.07, "latency_seconds": 10},
    )

    assert comparison["seeded_recall_delta_points"] == 20.0
    assert comparison["unsupported_claim_delta_points"] == 3.0
    assert comparison["latency_improvement"] == 0.3
    assert comparison["meets_quality_target"] is True


def test_traceability_reports_both_directions_with_stable_evidence() -> None:
    result = check_traceability(
        requirements={"FR-001", "FR-002"},
        tasks={
            "T001": {"requirement_ids": ["FR-001"]},
            "T002": {"requirement_ids": [], "operational_need": "package setup"},
        },
    )

    assert result["passed"] is False
    assert result["unmapped_requirements"] == ["FR-002"]
    assert result["unmapped_tasks"] == []
    assert result["evidence"] == ["requirement FR-002 has no implementation task"]
