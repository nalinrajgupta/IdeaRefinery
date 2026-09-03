"""Immutable worker stage brief construction."""

from __future__ import annotations

from typing import Any

from .io import content_hash


def prepare_stage_brief(
    *,
    run_id: str,
    stage: str,
    role: str,
    objective: str,
    coverage_assignments: list[str],
    artifact_hashes: dict[str, str],
    non_goals: list[str] | None = None,
    effort_budget: str = "bounded",
    settled_decision_ids: list[str] | None = None,
    answered_question_ids: list[str] | None = None,
    open_decision_ids: list[str] | None = None,
    schema_versions: dict[str, str] | None = None,
) -> dict[str, Any]:
    body = {
        "run_id": run_id,
        "stage": stage,
        "role": role,
        "objective": objective,
        "non_goals": non_goals or [],
        "effort_budget": effort_budget,
        "settled_decision_ids": settled_decision_ids or [],
        "answered_question_ids": answered_question_ids or [],
        "open_decision_ids": open_decision_ids or [],
        "coverage_assignments": sorted(set(coverage_assignments)),
        "artifact_hashes": dict(sorted(artifact_hashes.items())),
        "schema_versions": schema_versions or {"review-result": "1.0"},
    }
    body["brief_id"] = f"BRIEF-{content_hash(body)[:24]}"
    return body
