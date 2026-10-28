"""Explicit promotion of reviewed live bundles into immutable replay cases."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..errors import RefineryError


def promote_live_bundle(source: Path, golden_root: Path, *, approved: bool, approved_by: str | None) -> Path:
    if not approved or not approved_by:
        raise RefineryError("PROMOTION_APPROVAL_REQUIRED", "explicit maintainer approval is required")
    bundle = json.loads((source / "bundle.json").read_text(encoding="utf-8"))
    case_id = bundle["case_id"]
    destination = golden_root / f"{case_id}-v1"
    if destination.exists():
        raise RefineryError("PROMOTION_DESTINATION_EXISTS", f"promotion destination exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    (destination / "provenance.json").write_text(json.dumps({"approved_by": approved_by, "source": str(source)}, indent=2), encoding="utf-8")
    return destination
