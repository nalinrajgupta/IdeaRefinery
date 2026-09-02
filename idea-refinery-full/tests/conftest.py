from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def feature_dir(tmp_path: Path) -> Path:
    path = tmp_path / "specs" / "001-example"
    path.mkdir(parents=True)
    return path


@pytest.fixture
def full_roster() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "models": {
            "gpt-5.5": ["low", "medium", "high", "xhigh"],
            "gpt-5.6-sol": ["low", "medium", "high", "xhigh", "max", "ultra"],
            "gpt-5.6-terra": ["low", "medium", "high", "xhigh", "max", "ultra"],
            "gpt-5.6-luna": ["low", "medium", "high", "xhigh", "max"],
            "gpt-5.4": ["low", "medium", "high", "xhigh"],
        },
    }


@pytest.fixture
def reduced_roster() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "models": {
            "gpt-5.6-sol": ["low", "medium", "high", "xhigh", "max", "ultra"],
            "gpt-5.6-terra": ["low", "medium"],
        },
    }


@pytest.fixture
def write_json():
    def _write(path: Path, value: object) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    return _write
