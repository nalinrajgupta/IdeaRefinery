from __future__ import annotations

import json
from pathlib import Path

from idea_refinery.schemas import bundled_schema_path, validate_document


CONTRACTS = {
    "config",
    "invocation",
    "repair-packet",
    "review-result",
    "run-manifest",
    "trace-event",
}


def test_bundled_schemas_match_feature_contracts() -> None:
    repository = Path(__file__).resolve().parents[3]
    feature_contracts = repository / "specs/001-refinery-quality-orchestration/contracts"
    for name in CONTRACTS:
        expected = json.loads((feature_contracts / f"{name}.schema.json").read_text())
        actual = json.loads(bundled_schema_path(name).read_text())
        assert actual == expected


def test_config_schema_accepts_partial_repository_config() -> None:
    validate_document(
        "config",
        {"schema_version": "1.0", "roles": {"product": {"model": "m", "reasoning_effort": "high"}}},
    )


def test_invocation_requires_overrides_wrapper() -> None:
    validate_document(
        "invocation",
        {
            "schema_version": "1.0",
            "overrides": {"roles": {"ceo": {"model": "m", "reasoning_effort": "high"}}},
        },
    )
