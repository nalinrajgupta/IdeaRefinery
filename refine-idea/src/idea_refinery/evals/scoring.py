"""Offline scoring for orchestration result bundles."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def score_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    seeded = set(bundle.get("seeded_findings", []))
    findings = bundle.get("findings", [])
    found_seeded = {item.get("seed_id") for item in findings if item.get("seed_id") in seeded}
    unsupported = sum(1 for item in findings if not item.get("supported", True))
    reviewers = {item.get("reviewer") for item in findings}
    coverage = [item for item in bundle.get("coverage_items", []) if item.get("applicable")]
    covered = sum(1 for item in coverage if item.get("reviewed") and item.get("evidence"))
    questions = bundle.get("questions", [])
    unnecessary = sum(1 for item in questions if not item.get("necessary", True))
    repairs = bundle.get("repairs", [])
    converged = sum(1 for item in repairs if item.get("risk_delta") == "decreased" and item.get("status") == "promoted")
    traceability = bundle.get("traceability", {})
    return {
        "seeded_finding_recall": _ratio(len(found_seeded), len(seeded)),
        "unsupported_claim_rate": _ratio(unsupported, len(findings)),
        "reviewer_diversity": _ratio(len(reviewers), 3),
        "coverage_completeness": _ratio(covered, len(coverage)),
        "unnecessary_question_rate": _ratio(unnecessary, len(questions)),
        "repair_convergence": _ratio(converged, len(repairs)),
        "requirement_task_traceability": _ratio(traceability.get("mapped_requirements", 0) + traceability.get("mapped_tasks", 0), traceability.get("total_requirements", 0) + traceability.get("total_tasks", 0)),
        "latency_seconds": bundle.get("latency_seconds", 0),
        "effort": bundle.get("effort", {}),
        "downstream_material_decisions": bundle.get("downstream_material_decisions", 0),
    }


def compare_profiles(multi: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    recall_delta = (multi["seeded_finding_recall"] - baseline["seeded_finding_recall"]) * 100
    unsupported_delta = (multi["unsupported_claim_rate"] - baseline["unsupported_claim_rate"]) * 100
    baseline_latency = baseline.get("latency_seconds", 0)
    latency_improvement = (baseline_latency - multi.get("latency_seconds", 0)) / baseline_latency if baseline_latency else 0.0
    return {
        "seeded_recall_delta_points": round(recall_delta, 10),
        "unsupported_claim_delta_points": round(unsupported_delta, 10),
        "latency_improvement": round(latency_improvement, 10),
        "meets_quality_target": recall_delta >= 15 and unsupported_delta <= 5,
    }
