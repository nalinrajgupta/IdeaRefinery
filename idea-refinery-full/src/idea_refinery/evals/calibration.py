"""Calibration gates for model-judge metrics."""

from __future__ import annotations

from .scoring import _ratio
from ..errors import RefineryError


def calibration_status(labels: list[dict[str, str]], *, threshold: float = 0.9, policy_approved: bool = False) -> dict[str, object]:
    agreement = _ratio(sum(1 for item in labels if item.get("human") == item.get("judge")), len(labels))
    return {
        "agreement": agreement,
        "sample_size": len(labels),
        "threshold": threshold,
        "calibrated": agreement >= threshold,
        "policy_approved": policy_approved,
        "blocking": agreement >= threshold and policy_approved,
    }


def enforce_blocking_policy(metric: str, *, passed: bool, calibration: dict[str, object]) -> dict[str, object]:
    blocking = bool(calibration.get("blocking"))
    result = {"metric": metric, "passed": passed, "blocking": blocking, "reported": True}
    if blocking and not passed:
        raise RefineryError("EVAL_METRIC_FAILED", f"blocking metric failed: {metric}")
    return result
