"""Review result envelope validation and trust-boundary checks."""

from __future__ import annotations

from typing import Any

from .errors import ContractError
from .schemas import validate_document


def _reject(code: str, message: str, **details: Any) -> None:
    raise ContractError(code, message, details or None)


def validate_review_envelope(
    envelope: dict[str, Any],
    *,
    dispatch: dict[str, Any],
    assigned_coverage: set[str],
    protected_hashes: dict[str, str],
) -> None:
    validate_document("review-result", envelope)
    for field in ("role", "model", "reasoning_effort", "brief_id"):
        if envelope.get(field) != dispatch.get(field):
            _reject("dispatch-mismatch", f"envelope {field} does not match dispatch", field=field)
    if envelope["protected_artifact_hashes"] != protected_hashes:
        _reject("protected-artifact-drift", "protected artifacts changed during review")
    attestation_ids = [item["coverage_id"] for item in envelope["coverage_attestations"]]
    if len(attestation_ids) != len(set(attestation_ids)) or set(attestation_ids) != assigned_coverage:
        _reject(
            "coverage-incomplete",
            "coverage attestations must match assigned coverage exactly",
            expected=sorted(assigned_coverage),
            actual=sorted(set(attestation_ids)),
        )
    finding_ids = {finding["local_id"] for finding in envelope["findings"]}
    linked_ids = {finding_id for item in envelope["coverage_attestations"] for finding_id in item["finding_ids"]}
    if not linked_ids <= finding_ids:
        _reject("finding-link-invalid", "coverage attestation references an unknown finding")
    for item in envelope["coverage_attestations"]:
        if item["applicable"] and item["reviewed"] and not item["evidence"]:
            _reject("coverage-evidence-missing", f"{item['coverage_id']} lacks review evidence")
    status = envelope["status"]
    if status == "completed" and envelope.get("failure"):
        _reject("completion-failure-conflict", "completed envelope cannot contain failure details")
    if status == "failed" and not envelope.get("failure"):
        _reject("failure-details-missing", "failed envelope requires failure details")


def execution_batches(roles: list[str], capacity: int) -> list[tuple[str, ...]]:
    if capacity < 1:
        raise ValueError("capacity must be positive")
    return [tuple(roles[index : index + capacity]) for index in range(0, len(roles), capacity)]


def aggregate_envelopes(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    role_order = {"ceo": 0, "product": 1, "architect": 2}
    return sorted(envelopes, key=lambda envelope: (role_order.get(envelope.get("role", ""), 99), envelope.get("envelope_id", "")))
