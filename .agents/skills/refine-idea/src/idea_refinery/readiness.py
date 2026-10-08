"""Readiness verdicts for complete and degraded runs."""

from __future__ import annotations

from typing import Any


REQUIRED_ROLES = ("ceo", "product", "architect")


def assess_readiness(
    *,
    roles: dict[str, str],
    coverage_items: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    repair_history: list[dict[str, Any]],
    traceability_passed: bool,
    waiver: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failed = sorted(role for role in REQUIRED_ROLES if roles.get(role) in {"failed-role", "rejected-drift", "retrying", "timed-out"})
    degraded = sorted(role for role, status in roles.items() if status == "degraded-fallback")
    coverage_gaps = sorted(item["id"] for item in coverage_items if item.get("applicable") and (not item.get("evidence") or item.get("disposition") in {"blind-spot", "unresolved", "decision-needed"}))
    finding_gaps = sorted(item.get("id", item.get("root_id", "unknown")) for item in findings if item.get("disposition") in {None, "unresolved", "decision-needed"})
    problems = sorted(set(failed + coverage_gaps + finding_gaps))
    result: dict[str, Any] = {
        "verdict": "BLOCKED ON DECISION" if problems or not traceability_passed else "READY FOR IMPLEMENTATION",
        "failed_roles": failed,
        "degraded_roles": degraded,
        "unresolved_coverage": coverage_gaps,
        "undispositioned_findings": finding_gaps,
    }
    if failed and waiver and waiver.get("missing_role") in failed:
        affected = set(waiver.get("affected_coverage_ids", []))
        if affected and waiver.get("owner") and waiver.get("rationale"):
            remaining = set(problems) - set(failed)
            result["verdict"] = "READY FOR IMPLEMENTATION — DEGRADED" if not remaining and traceability_passed else "BLOCKED ON DECISION"
            result["waived_perspective"] = waiver
    return result
