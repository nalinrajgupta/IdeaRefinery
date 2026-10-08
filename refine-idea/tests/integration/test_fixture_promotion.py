from __future__ import annotations

import json
from pathlib import Path

import pytest

from idea_refinery.errors import RefineryError
from idea_refinery.evals.promotion import promote_live_bundle
from idea_refinery.evals.replay import replay_fixture


def _live_bundle(path: Path) -> Path:
    path.mkdir()
    (path / "bundle.json").write_text(
        json.dumps({"schema_version": "1.0", "case_id": "edge-001", "promotion_status": "reviewed"}),
        encoding="utf-8",
    )
    (path / "expected.json").write_text(json.dumps({"verdict": "ready"}), encoding="utf-8")
    (path / "actual.json").write_text(json.dumps({"verdict": "ready"}), encoding="utf-8")
    return path


def test_promotion_requires_approval_and_never_overwrites(tmp_path: Path) -> None:
    source = _live_bundle(tmp_path / "live")
    golden = tmp_path / "golden"

    with pytest.raises(RefineryError, match="PROMOTION_APPROVAL_REQUIRED"):
        promote_live_bundle(source, golden, approved=False, approved_by=None)

    promoted = promote_live_bundle(source, golden, approved=True, approved_by="maintainer")
    assert promoted == golden / "edge-001-v1"
    provenance = json.loads((promoted / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["approved_by"] == "maintainer"
    assert replay_fixture(promoted)["passed"] is True

    with pytest.raises(RefineryError, match="PROMOTION_DESTINATION_EXISTS"):
        promote_live_bundle(source, golden, approved=True, approved_by="maintainer")
