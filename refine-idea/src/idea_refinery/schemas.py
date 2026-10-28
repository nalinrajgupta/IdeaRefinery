"""JSON Schema loading and validation."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, RefResolver

from .errors import ContractError

SemanticValidator = Callable[[dict[str, Any]], None]
_SEMANTIC_VALIDATORS: dict[str, list[SemanticValidator]] = {}


def bundled_schema_path(name: str) -> Path:
    candidates = (
        Path(__file__).resolve().parent / "schemas" / f"{name}.schema.json",
        Path(__file__).resolve().parents[2] / "schemas" / f"{name}.schema.json",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise ContractError("schema-not-found", f"unknown contract schema: {name}")


def load_schema(name: str) -> dict[str, Any]:
    return json.loads(bundled_schema_path(name).read_text(encoding="utf-8"))


def register_semantic_validator(name: str, validator: SemanticValidator) -> None:
    _SEMANTIC_VALIDATORS.setdefault(name, []).append(validator)


def validate_document(name: str, document: dict[str, Any]) -> None:
    schema_path = bundled_schema_path(name)
    schema = load_schema(name)
    store: dict[str, dict[str, Any]] = {}
    for candidate in schema_path.parent.glob("*.schema.json"):
        loaded = json.loads(candidate.read_text(encoding="utf-8"))
        store[candidate.as_uri()] = loaded
        if identifier := loaded.get("$id"):
            store[identifier] = loaded
    resolver = RefResolver(
        base_uri=schema_path.parent.as_uri() + "/", referrer=schema, store=store
    )
    errors = sorted(
        Draft202012Validator(schema, resolver=resolver).iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = [
            {"path": "/".join(map(str, error.absolute_path)), "message": error.message}
            for error in errors
        ]
        raise ContractError("contract-invalid", f"{name} contract validation failed", {"errors": details})
    for validator in _SEMANTIC_VALIDATORS.get(name, []):
        validator(document)
