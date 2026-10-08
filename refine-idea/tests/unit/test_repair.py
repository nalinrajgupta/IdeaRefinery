from __future__ import annotations

import pytest

from idea_refinery.errors import ContractError, StateError
from idea_refinery.repair import (
    RepairLedger,
    RepairPolicyInput,
    canonical_root_id,
    classify_authorization,
    evaluate_repair,
    validate_repair_packet,
)


def packet(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "1.0",
        "packet_id": "RP-one",
        "run_id": "run-one",
        "root_finding_id": "ROOT-one",
        "cycle": 1,
        "severity": "high",
        "evidence": ["spec.md:20 conflicts with plan.md:40"],
        "affected_requirements": ["FR-024"],
        "affected_artifacts": ["plan.md"],
        "smallest_correction": "Align plan wording with FR-024.",
        "completion_checks": ["cross-artifact analysis passes"],
        "invalidated_artifacts": ["plan", "tasks", "analysis"],
        "authorization_class": "bounded",
        "authorization_status": "authorized",
        "pre_repair_hashes": {"plan.md": "a" * 64},
        "status": "proposed",
    }
    value.update(changes)
    return value


@pytest.mark.parametrize(
    "decision_class",
    ["constitution", "scope-expansion", "product-priority", "risk-tolerance"],
)
def test_excluded_decision_classes_require_separate_authorization(decision_class: str) -> None:
    assert classify_authorization({decision_class}) == "separate-user-decision"


def test_correction_beyond_packet_requires_separate_authorization() -> None:
    assert classify_authorization(set(), correction_within_packet=False) == "separate-user-decision"


def test_root_identity_is_semantic_and_order_independent() -> None:
    first = canonical_root_id(["FR-025", "FR-024"], ["tasks.md", "plan.md"], "No stale tasks")
    second = canonical_root_id(["FR-024", "FR-025"], ["plan.md", "tasks.md"], " No stale tasks ")
    assert first == second
    assert first.startswith("ROOT-")


def test_alias_does_not_reset_root_cycle_budget() -> None:
    ledger = RepairLedger(cycle_limit=2)
    ledger.register_alias("local-finding-a", "ROOT-stable")
    assert ledger.reserve_cycle("local-finding-a", ["evidence-a"]) == 1
    ledger.register_alias("rephrased-finding-b", "ROOT-stable")
    assert ledger.reserve_cycle("rephrased-finding-b", ["evidence-b"]) == 2
    with pytest.raises(StateError, match="cycle limit"):
        ledger.reserve_cycle("ROOT-stable", ["evidence-c"])


def test_same_root_recurring_without_new_evidence_stops_early() -> None:
    ledger = RepairLedger(cycle_limit=2)
    ledger.reserve_cycle("ROOT-stable", ["same evidence"])
    with pytest.raises(StateError, match="without new evidence"):
        ledger.reserve_cycle("ROOT-stable", ["same evidence"])
    assert ledger.cycles("ROOT-stable") == 1


def test_policy_stops_without_bounded_consent() -> None:
    decision = evaluate_repair(RepairPolicyInput(authorized=False))
    assert not decision.allowed
    assert decision.reason == "bounded-authorization-required"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"decision_classes": frozenset({"scope-expansion"})}, "separate-user-decision-required"),
        ({"correction_within_packet": False}, "correction-exceeds-packet"),
        ({"new_high_severity_contradiction": True}, "new-high-severity-contradiction"),
        ({"risk_delta": "increased"}, "material-risk-did-not-decrease"),
        ({"risk_delta": "unchanged"}, "material-risk-did-not-decrease"),
    ],
)
def test_policy_stops_on_unsafe_convergence(changes: dict[str, object], reason: str) -> None:
    base: dict[str, object] = {"authorized": True, "risk_delta": "decreased"}
    base.update(changes)
    decision = evaluate_repair(RepairPolicyInput(**base))
    assert not decision.allowed
    assert decision.reason == reason


def test_valid_bounded_repair_is_allowed() -> None:
    decision = evaluate_repair(RepairPolicyInput(authorized=True, risk_delta="decreased"))
    assert decision.allowed
    assert decision.reason == "bounded-repair-allowed"


def test_packet_validation_rejects_silent_severity_reduction() -> None:
    with pytest.raises(ContractError, match="severity may not decrease"):
        validate_repair_packet(packet(severity="high"), previous_severity="critical")


def test_packet_validation_rejects_incorrect_invalidation() -> None:
    with pytest.raises(ContractError, match="invalidated_artifacts"):
        validate_repair_packet(packet(invalidated_artifacts=["plan"]))


def test_packet_validation_accepts_complete_packet() -> None:
    assert validate_repair_packet(packet()) == packet()

