"""Contract tests for generated Copilot and Hermes skill distributions."""

from __future__ import annotations

import subprocess
import sys
import importlib.util
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPT = REPOSITORY_ROOT / "tools" / "sync_host_skills.py"
SKILLS = ("idea-refinery-full", "idea-refinery-implement")


def read_repository_text(*parts: str) -> str:
    return (REPOSITORY_ROOT.joinpath(*parts)).read_text(encoding="utf-8")


def assert_contains_all(text: str, phrases: tuple[str, ...]) -> None:
    for phrase in phrases:
        assert phrase in text


def section(text: str, start_heading: str, end_heading: str | None = None) -> str:
    start = text.index(start_heading)
    end = text.index(end_heading, start) if end_heading else len(text)
    return text[start:end]


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
    full = read_repository_text("idea-refinery-full", "SKILL.md")
    implementation = read_repository_text("idea-refinery-implement", "SKILL.md")
    documentation = read_repository_text("docs", "host-compatibility.md")

    assert full.startswith("---\nname: idea-refinery-full\n")
    assert_contains_all(
        full,
        ("explicit-only workflow", "Do not implement application code", "READY FOR IMPLEMENTATION"),
    )
    assert implementation.startswith("---\nname: idea-refinery-implement\n")
    assert_contains_all(
        implementation,
        (
            "The controller is the only writer",
            "TDD slice",
            "read-only reviewer",
            "$speckit-converge",
            "IMPLEMENTATION COMPLETE",
        ),
    )
    assert_contains_all(
        documentation,
        ("Codex", "GitHub Copilot", "Hermes", "Detect before initialization", "sequential execution"),
    )


def test_primary_documentation_changes_trigger_host_validation() -> None:
    workflow = read_repository_text(".github", "workflows", "refinery-evals.yml")

    assert workflow.count('- "README.md"') == 2
    assert workflow.count('- "setup.md"') == 2


def test_copilot_readme_has_first_class_quick_start() -> None:
    readme = read_repository_text("README.md")
    overview = section(readme, "# Idea Refinery", "## End-to-end lifecycle")
    lifecycle = section(readme, "## End-to-end lifecycle", "## Prerequisites")
    prerequisites = section(readme, "## Prerequisites", "## GitHub Copilot quick start")
    quick_start = section(readme, "## GitHub Copilot quick start", "## Try refinement")
    troubleshooting = section(readme, "## Troubleshooting")

    assert_contains_all(
        overview,
        ("GitHub Copilot", "`idea-refinery-full`", "`idea-refinery-implement`", "host-specific"),
    )
    assert "$idea-refinery-full" not in lifecycle
    assert "$idea-refinery-implement" not in lifecycle
    assert_contains_all(
        prerequisites,
        ("GitHub Copilot CLI", "specify init --here --integration copilot", "Preserve"),
    )
    assert_contains_all(
        quick_start,
        (
            "## GitHub Copilot quick start",
            ".agents/skills/idea-refinery-full",
            ".agents/skills/idea-refinery-implement",
            "/idea-refinery-full <idea>",
            "/skills reload",
            "spec.md",
            "plan.md",
            "tasks.md",
            "refinery-state.md",
            "READY FOR IMPLEMENTATION",
            "/idea-refinery-implement",
            "dollar-prefixed",
            "[Setup and tryout](setup.md)",
            "[Host compatibility and installation](docs/host-compatibility.md)",
        ),
    )
    assert "```text\n/idea-refinery-implement\n```" in quick_start
    assert_contains_all(
        troubleshooting,
        (
            "Copilot skill name is not recognized",
            "/skills reload",
            "project-local",
            "dollar-prefixed",
        ),
    )


def test_copilot_setup_documents_safe_complete_lifecycle() -> None:
    setup = read_repository_text("setup.md")
    copilot = section(setup, "## GitHub Copilot", "## Codex")
    powershell = section(
        copilot,
        "### Personal installation on Windows PowerShell",
        "### Personal installation on POSIX shells",
    )
    posix = section(copilot, "### Personal installation on POSIX shells")

    assert_contains_all(
        copilot,
        (
            "## GitHub Copilot",
            "### Repository-local skills",
            "### Personal installation on Windows PowerShell",
            "### Personal installation on POSIX shells",
            ".agents\\skills",
            ".agents/skills/idea-refinery-full",
            ".copilot\\skills",
            "~/.copilot/skills",
            "Test-Path",
            "staging",
            "Get-FileHash",
            "-ErrorAction Stop",
            "Remove-Item -LiteralPath",
            "rm -rf --",
            'if mv "$STAGING_ROOT/$skill" "$TARGET_ROOT/$skill"; then',
            "transaction_ok=false",
            "backup preserved",
            "/skills reload",
            "/skills",
            "project-local",
            "personal",
            "/idea-refinery-full <idea>",
            "/idea-refinery-implement",
        ),
    )
    assert powershell.count('$TargetRoot = Join-Path $HOME ".copilot\\skills"') >= 3
    assert powershell.count('$Skills = @("idea-refinery-full", "idea-refinery-implement")') >= 3
    assert powershell.count("function Get-TreeManifest") >= 2
    assert posix.count('REFINERY_REPO="/absolute/path/to/IdeaRefinery"') >= 2
    assert posix.count('SOURCE_ROOT="$REFINERY_REPO/.agents/skills"') >= 2
    assert posix.count('SKILLS="idea-refinery-full idea-refinery-implement"') >= 2
    assert posix.index('test -f "$SOURCE_ROOT/$skill/SKILL.md"') < posix.index("STAGING_ROOT=")
    assert "[host compatibility](docs/host-compatibility.md)" in setup


def test_copilot_docs_preserve_spec_kit_and_label_shells() -> None:
    readme = read_repository_text("README.md")
    setup = read_repository_text("setup.md")
    compatibility = read_repository_text("docs", "host-compatibility.md")
    setup_prerequisites = section(setup, "## Prerequisites", "## GitHub Copilot")
    setup_troubleshooting = section(setup, "## Troubleshooting", "## Related documentation")

    assert_contains_all(
        setup_prerequisites,
        (
            "specify init --here --integration copilot",
            "If `.specify/` already exists",
            "Only when `.specify/` is absent",
            "approve the mutation",
            "Never use `--force`",
        ),
    )
    assert_contains_all(
        setup_troubleshooting,
        ("If `.specify/` already exists", "Only when `.specify/` is absent", "Never use `--force`"),
    )
    assert "[Host compatibility and installation](docs/host-compatibility.md)" in readme
    assert "[host compatibility](docs/host-compatibility.md)" in setup
    assert_contains_all(
        compatibility,
        (
            "`~/.copilot/skills/`",
            "[setup guide](../setup.md)",
            "## PowerShell",
            "## POSIX shell",
            "preserve",
            "Never use `--force`",
        ),
    )


def test_implementation_preflight_supports_bash_and_powershell() -> None:
    implementation = read_repository_text("idea-refinery-implement", "SKILL.md")

    assert_contains_all(
        implementation,
        (
            ".specify/scripts/bash/check-prerequisites.sh",
            ".specify/scripts/powershell/check-prerequisites.ps1",
            "--json --require-tasks --include-tasks",
            "-Json -RequireTasks -IncludeTasks",
            "Prefer the host-native",
            "If neither supported prerequisite script can be executed",
            "Bash and PowerShell are the supported prerequisite script families",
            "repair the repository's Spec Kit initialization or script distribution",
        ),
    )


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
