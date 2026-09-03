"""Contract tests for generated Copilot and Hermes skill distributions."""

from __future__ import annotations

import subprocess
import sys
import importlib.util
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPT = REPOSITORY_ROOT / "tools" / "sync_host_skills.py"
SKILLS = ("idea-refinery-full", "idea-refinery-implement")


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_host_skills", SYNC_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_host_skill_distribution_is_in_sync() -> None:
    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--check"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout


def test_host_distributions_are_self_contained_and_preserve_safety_contract() -> None:
    required_phrases = (
        "Host capability contract",
        "local-fallback",
        "sequential execution",
    )
    for skill_name in SKILLS:
        canonical = (REPOSITORY_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
        generated_root = REPOSITORY_ROOT / ".agents" / "skills" / skill_name
        generated = (generated_root / "SKILL.md").read_text(encoding="utf-8")

        marker = f"<!-- Generated from {skill_name}/SKILL.md; do not edit this copy. -->\n"
        assert marker in generated
        assert canonical == generated.replace(marker, "")
        assert (generated_root / "references").is_dir()
        for phrase in required_phrases:
            assert phrase in canonical


def test_workflow_contracts_and_host_documentation_are_present() -> None:
    full = (REPOSITORY_ROOT / "idea-refinery-full" / "SKILL.md").read_text(encoding="utf-8")
    implementation = (REPOSITORY_ROOT / "idea-refinery-implement" / "SKILL.md").read_text(encoding="utf-8")
    documentation = (REPOSITORY_ROOT / "docs" / "host-compatibility.md").read_text(encoding="utf-8")

    assert full.startswith("---\nname: idea-refinery-full\n")
    for phrase in ("explicit-only workflow", "Do not implement application code", "READY FOR IMPLEMENTATION"):
        assert phrase in full
    assert implementation.startswith("---\nname: idea-refinery-implement\n")
    for phrase in ("The controller is the only writer", "TDD slice", "read-only reviewer", "$speckit-converge", "IMPLEMENTATION COMPLETE"):
        assert phrase in implementation
    for phrase in ("Codex", "GitHub Copilot", "Hermes", "Detect before initialization", "sequential execution"):
        assert phrase in documentation


def test_missing_relative_reference_is_rejected(tmp_path: Path) -> None:
    module = load_sync_module()
    skill_root = tmp_path / "skill"
    skill_root.mkdir()
    (skill_root / "SKILL.md").write_text("[missing](references/nope.md)\n", encoding="utf-8")

    try:
        module.validate_relative_links(skill_root)
    except ValueError as error:
        assert "missing local reference" in str(error)
    else:
        raise AssertionError("missing reference was accepted")
