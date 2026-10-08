"""Bounded repair policy, packet validation, and staged artifact promotion."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .errors import ContractError, StateError
from .invalidation import calculate_invalidation
from .io import content_hash
from .schemas import validate_document


MAX_REPAIR_CYCLES = 2
EXCLUDED_DECISION_CLASSES = frozenset(
    {"constitution", "scope-expansion", "product-priority", "risk-tolerance"}
)
_SEVERITY_RANK = {"high": 1, "critical": 2, "blocker": 3}


def canonical_root_id(
    requirement_ids: Iterable[str], artifact_paths: Iterable[str], completion_criterion: str
) -> str:
    """Derive stable root identity from semantic inputs, not finding wording."""

    identity = {
        "requirement_ids": sorted(set(requirement_ids)),
        "artifact_paths": sorted(set(artifact_paths)),
        "completion_criterion": " ".join(completion_criterion.split()),
    }
    return f"ROOT-{content_hash(identity)[:24]}"


def classify_authorization(
    decision_classes: Iterable[str], *, correction_within_packet: bool = True
) -> str:
    classes = frozenset(decision_classes)
    if classes & EXCLUDED_DECISION_CLASSES or not correction_within_packet:
        return "separate-user-decision"
    return "bounded"


@dataclass(frozen=True)
class RepairPolicyInput:
    authorized: bool
    decision_classes: frozenset[str] = frozenset()
    correction_within_packet: bool = True
    new_high_severity_contradiction: bool = False
    risk_delta: str = "not-measured"


@dataclass(frozen=True)
class RepairDecision:
    allowed: bool
    reason: str


def evaluate_repair(value: RepairPolicyInput) -> RepairDecision:
    """Apply ordered stop conditions for one bounded repair attempt."""

    if not value.authorized:
        return RepairDecision(False, "bounded-authorization-required")
    if value.decision_classes & EXCLUDED_DECISION_CLASSES:
        return RepairDecision(False, "separate-user-decision-required")
    if not value.correction_within_packet:
        return RepairDecision(False, "correction-exceeds-packet")
    if value.new_high_severity_contradiction:
        return RepairDecision(False, "new-high-severity-contradiction")
    if value.risk_delta not in {"decreased", "not-measured"}:
        return RepairDecision(False, "material-risk-did-not-decrease")
    return RepairDecision(True, "bounded-repair-allowed")


class RepairLedger:
    """Track repair budgets by canonical root while retaining local aliases."""

    def __init__(
        self,
        *,
        cycle_limit: int = MAX_REPAIR_CYCLES,
        counts: Mapping[str, int] | None = None,
        aliases: Mapping[str, str] | None = None,
        evidence_hashes: Mapping[str, Iterable[str]] | None = None,
    ) -> None:
        if not 0 <= cycle_limit <= MAX_REPAIR_CYCLES:
            raise ValueError(f"cycle_limit must be between 0 and {MAX_REPAIR_CYCLES}")
        self.cycle_limit = cycle_limit
        self._counts = dict(counts or {})
        self._aliases = dict(aliases or {})
        self._evidence_hashes = {
            root: set(values) for root, values in (evidence_hashes or {}).items()
        }

    def canonical(self, identifier: str) -> str:
        seen: set[str] = set()
        current = identifier
        while current in self._aliases:
            if current in seen:
                raise StateError("repair-alias-cycle", "repair root alias lineage is cyclic")
            seen.add(current)
            current = self._aliases[current]
        return current

    def register_alias(self, alias: str, root_id: str) -> None:
        root = self.canonical(root_id)
        if alias == root:
            return
        existing = self._aliases.get(alias)
        if existing is not None and self.canonical(existing) != root:
            raise StateError(
                "repair-alias-conflict",
                f"alias {alias} already belongs to a different root finding",
            )
        if self.canonical(root) == alias:
            raise StateError("repair-alias-cycle", "repair root alias lineage is cyclic")
        self._aliases[alias] = root

    def cycles(self, identifier: str) -> int:
        return self._counts.get(self.canonical(identifier), 0)

    def reserve_cycle(self, identifier: str, evidence: Iterable[str]) -> int:
        root = self.canonical(identifier)
        current = self._counts.get(root, 0)
        if current >= self.cycle_limit:
            raise StateError(
                "repair-cycle-limit-reached",
                f"repair cycle limit reached for {root}",
                {"root_finding_id": root, "cycles": current},
            )
        evidence_items = sorted(set(evidence))
        if not evidence_items:
            raise StateError("repair-evidence-required", "repair evidence must not be empty")
        fingerprint = content_hash(evidence_items)
        prior = self._evidence_hashes.setdefault(root, set())
        if fingerprint in prior:
            raise StateError(
                "repair-recurring-without-evidence",
                f"root finding {root} recurred without new evidence",
            )
        prior.add(fingerprint)
        self._counts[root] = current + 1
        return current + 1

    def snapshot(self) -> dict[str, object]:
        return {
            "counts": dict(sorted(self._counts.items())),
            "aliases": dict(sorted(self._aliases.items())),
            "evidence_hashes": {
                root: sorted(values) for root, values in sorted(self._evidence_hashes.items())
            },
        }


def validate_repair_packet(
    packet: Mapping[str, Any], *, previous_severity: str | None = None
) -> dict[str, Any]:
    """Validate the versioned packet plus cross-field repair invariants."""

    document = dict(packet)
    validate_document("repair-packet", document)
    if previous_severity is not None:
        if previous_severity not in _SEVERITY_RANK:
            raise ContractError("repair-severity-invalid", f"unknown previous severity: {previous_severity}")
        if _SEVERITY_RANK[document["severity"]] < _SEVERITY_RANK[previous_severity]:
            raise ContractError(
                "repair-severity-decreased",
                "repair finding severity may not decrease without evidence-backed disposition",
            )

    expected = calculate_invalidation(document["affected_artifacts"])
    actual = frozenset(document["invalidated_artifacts"])
    if actual != expected:
        raise ContractError(
            "repair-invalidation-mismatch",
            "invalidated_artifacts must equal the affected artifact DAG closure",
            {"expected": sorted(expected), "actual": sorted(actual)},
        )

    expected_authorization = classify_authorization(set())
    if document["authorization_class"] != expected_authorization:
        if document["authorization_status"] == "authorized":
            raise ContractError(
                "repair-authorization-invalid",
                "a separate-user-decision repair cannot use bounded authorization",
            )
    return document


@dataclass(frozen=True)
class TransactionResult:
    status: str
    errors: tuple[str, ...] = ()


class RepairTransaction:
    """Stage a complete artifact tree and promote it with rename rollback safety."""

    def __init__(self, active_root: Path, transaction_root: Path):
        self.active_root = active_root.resolve()
        self.transaction_root = transaction_root.resolve()
        self.staged_root = self.transaction_root / "staged"
        self.checkpoint_root = self.transaction_root / "checkpoint"
        self.discarded_root = self.transaction_root / "discarded"
        self._promoted = False

    @classmethod
    def begin(cls, active_root: Path, transaction_root: Path) -> "RepairTransaction":
        active = active_root.resolve()
        transaction = transaction_root.resolve()
        if not active.is_dir():
            raise StateError("repair-active-missing", f"active artifact tree is missing: {active}")
        if active == transaction or active in transaction.parents:
            raise StateError(
                "repair-staging-unsafe", "transaction root must not be inside the active artifact tree"
            )
        if transaction.exists():
            raise StateError("repair-transaction-exists", f"transaction already exists: {transaction}")
        transaction.mkdir(parents=True)
        instance = cls(active, transaction)
        shutil.copytree(active, instance.staged_root)
        if os.stat(active).st_dev != os.stat(transaction).st_dev:
            raise StateError(
                "repair-cross-device", "active and staged artifact trees must share a filesystem"
            )
        return instance

    @classmethod
    def resume(cls, active_root: Path, transaction_root: Path) -> "RepairTransaction":
        """Re-open a promoted transaction so an explicit rollback can restore it."""
        instance = cls(active_root.resolve(), transaction_root.resolve())
        instance._promoted = instance.checkpoint_root.is_dir()
        if not instance._promoted and not instance.staged_root.is_dir():
            raise StateError("repair-transaction-missing", "no staged or checkpoint transaction exists")
        return instance

    def promote(self, validator: Callable[[Path], Iterable[str]]) -> TransactionResult:
        if not self.staged_root.is_dir():
            raise StateError("repair-stage-missing", "staged artifact tree is missing")
        errors = tuple(str(item) for item in validator(self.staged_root))
        if errors:
            return TransactionResult("rolled-back", errors)
        if self.checkpoint_root.exists():
            raise StateError("repair-checkpoint-exists", "repair checkpoint already exists")

        os.replace(self.active_root, self.checkpoint_root)
        try:
            os.replace(self.staged_root, self.active_root)
        except BaseException:
            os.replace(self.checkpoint_root, self.active_root)
            raise
        self._promoted = True
        return TransactionResult("promoted")

    def rollback(self) -> TransactionResult:
        if not self._promoted or not self.checkpoint_root.is_dir():
            return TransactionResult("rolled-back")
        if self.discarded_root.exists():
            raise StateError("repair-discarded-exists", "discarded artifact tree already exists")
        os.replace(self.active_root, self.discarded_root)
        try:
            os.replace(self.checkpoint_root, self.active_root)
        except BaseException:
            os.replace(self.discarded_root, self.active_root)
            raise
        self._promoted = False
        return TransactionResult("rolled-back")


__all__ = [
    "EXCLUDED_DECISION_CLASSES",
    "MAX_REPAIR_CYCLES",
    "RepairDecision",
    "RepairLedger",
    "RepairPolicyInput",
    "RepairTransaction",
    "TransactionResult",
    "canonical_root_id",
    "classify_authorization",
    "evaluate_repair",
    "validate_repair_packet",
]
