from __future__ import annotations

import pytest

from idea_refinery.config import load_yaml
from idea_refinery.io import ensure_within


def test_paths_cannot_escape_run_root(tmp_path) -> None:
    with pytest.raises(ValueError, match="escapes root"):
        ensure_within(tmp_path / "run", tmp_path / "run" / ".." / "outside")


def test_yaml_loader_rejects_non_mapping(tmp_path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("- not-a-mapping\n", encoding="utf-8")
    with pytest.raises(Exception, match="must be a mapping"):
        load_yaml(path)
