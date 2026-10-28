from __future__ import annotations

import pytest

from idea_refinery.errors import RefineryError
from idea_refinery.evals.calibration import calibration_status, enforce_blocking_policy


def test_ninety_percent_human_agreement_requires_explicit_policy_approval() -> None:
    labels = [
        {"human": "pass", "judge": "pass"} for _ in range(9)
    ] + [{"human": "fail", "judge": "pass"}]

    status = calibration_status(labels, threshold=0.9, policy_approved=False)

    assert status == {
        "agreement": 0.9,
        "sample_size": 10,
        "threshold": 0.9,
        "calibrated": True,
        "policy_approved": False,
        "blocking": False,
    }


def test_approved_calibrated_metric_can_block() -> None:
    labels = [{"human": "pass", "judge": "pass"} for _ in range(10)]
    status = calibration_status(labels, policy_approved=True)

    with pytest.raises(RefineryError, match="EVAL_METRIC_FAILED"):
        enforce_blocking_policy("coverage_quality", passed=False, calibration=status)


def test_uncalibrated_judge_failure_remains_visible_and_non_blocking() -> None:
    labels = [{"human": "pass", "judge": "fail"}]
    status = calibration_status(labels, policy_approved=True)

    assert enforce_blocking_policy("judge_quality", passed=False, calibration=status) == {
        "metric": "judge_quality",
        "passed": False,
        "blocking": False,
        "reported": True,
    }
