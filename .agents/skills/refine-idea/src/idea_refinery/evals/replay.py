"""Load and validate deterministic replay fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def replay_fixture(path: Path) -> dict[str, Any]:
    expected = json.loads((path / "expected.json").read_text(encoding="utf-8"))
    actual = json.loads((path / "actual.json").read_text(encoding="utf-8"))
    return {"passed": expected == actual, "expected": expected, "actual": actual}
