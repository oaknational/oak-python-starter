#!/usr/bin/env python3
"""Audit tracked repo state using filesystem and text inspection."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "pyproject.toml",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".agent/directives/AGENT.md",
    ".agent/directives/orientation.md",
    ".agent/directives/principles.md",
    ".agent/directives/testing-strategy.md",
    ".agent/practice-index.md",
    ".agent/VISION.md",
    ".agent/memory/README.md",
    ".agent/memory/active/distilled.md",
    ".agent/memory/active/napkin.md",
    ".agent/memory/active/patterns/README.md",
    ".agent/memory/operational/README.md",
    ".agent/memory/operational/repo-continuity.md",
    ".agent/memory/operational/threads/README.md",
    ".agent/memory/executive/README.md",
    ".agent/memory/executive/artefact-inventory.md",
    ".agent/memory/executive/invoke-code-reviewers.md",
    ".agent/memory/executive/cross-platform-agent-surface-matrix.md",
    ".agent/research/README.md",
    ".agent/analysis/README.md",
    ".agent/reports/README.md",
    ".agent/reference/README.md",
    ".agent/experience/README.md",
    ".agent/practice-core/practice-verification.md",
    ".agent/practice-core/decision-records/README.md",
    ".agent/practice-core/patterns/README.md",
    ".agent/plans/README.md",
    ".agent/plans/high-level-plan.md",
    ".agent/plans/completed-plans.md",
    ".agent/plans/roadmap.md",
    ".agent/plans/templates/README.md",
    ".agent/plans/agentic-engineering/README.md",
    ".agent/plans/agentic-engineering/roadmap.md",
    ".agent/plans/agentic-engineering/documentation-sync-log.md",
    ".agent/plans/runtime-infrastructure/README.md",
    ".agent/plans/runtime-infrastructure/roadmap.md",
    ".agent/plans/runtime-infrastructure/documentation-sync-log.md",
    ".agent/plans/demo-application/README.md",
    ".agent/plans/demo-application/roadmap.md",
    ".agent/plans/demo-application/documentation-sync-log.md",
    ".agent/commands/ephemeral-to-permanent-homing.md",
    ".agent/commands/session-handoff.md",
    ".agent/skills/commit/SKILL.md",
    ".agent/skills/tsdoc/SKILL.md",
    ".agent/hooks/policy.json",
    "src/oaknational/python_repo_template/__main__.py",
    "src/oaknational/python_repo_template/devtools.py",
    "src/oaknational/python_repo_template/data/activity_store.py",
    "src/oaknational/python_repo_template/demo/activity_report.py",
    "tools/__init__.py",
    "tools/agent_hooks.py",
    "tools/repo_audit.py",
    "tests/test_agent_hooks.py",
    "tests/test_activity_store.py",
    "tests/test_activity_report.py",
    "tests/test_devtools.py",
    "tests/test_package_entrypoint.py",
    "data/fixtures/activity_log.csv",
    "data/fixtures/activity_log.metadata.yaml",
    "docs/architecture-decision-records/ADR-0001-cross-platform-practice-surface-contract.md",
    "docs/explorations/README.md",
    "docs/dev-tooling.md",
]
CANONICAL_GATE_SCRIPTS = {
    "clean": "oaknational.python_repo_template.devtools:clean",
    "build": "oaknational.python_repo_template.devtools:build",
    "dev": "oaknational.python_repo_template.devtools:dev",
    "format": "oaknational.python_repo_template.devtools:format_gate",
    "format-fix": "oaknational.python_repo_template.devtools:format_fix",
    "lint": "oaknational.python_repo_template.devtools:lint",
    "lint-fix": "oaknational.python_repo_template.devtools:lint_fix",
    "typecheck": "oaknational.python_repo_template.devtools:typecheck",
    "repo-audit": "oaknational.python_repo_template.devtools:repo_audit",
    "test": "oaknational.python_repo_template.devtools:test",
    "coverage": "oaknational.python_repo_template.devtools:coverage",
    "fix": "oaknational.python_repo_template.devtools:fix",
    "check": "oaknational.python_repo_template.devtools:check",
    "check-ci": "oaknational.python_repo_template.devtools:check_ci",
}
LEGACY_GATE_SCRIPTS = {
    "format-check",
}


def read_text(path: Path, failures: list[str], check: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        failures.append(f"{check}: could not read {path.relative_to(REPO_ROOT)}: {exc}")
        return None


def require(failures: list[str], check: str, condition: bool, message: str) -> None:
    if not condition:
        failures.append(f"{check}: {message}")


def audit_required_paths(root: Path) -> list[str]:
    check = "required-paths"
    failures: list[str] = []
    for relative_path in REQUIRED_PATHS:
        require(
            failures,
            check,
            (root / relative_path).exists(),
            f"missing required path {relative_path}",
        )
    return failures


def audit_entry_surfaces(root: Path) -> list[str]:
    check = "entry-surfaces"
    failures: list[str] = []
    expected = "Read `.agent/directives/AGENT.md` and follow it."
    for relative_path in ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]:
        text = read_text(root / relative_path, failures, check)
        if text is None:
            continue
        require(
            failures,
            check,
            expected in text,
            f"{relative_path} must delegate to .agent/directives/AGENT.md",
        )
    return failures


def audit_identity(root: Path) -> list[str]:
    check = "repo-identity"
    failures: list[str] = []
    readme = read_text(root / "README.md", failures, check)
    pyproject = read_text(root / "pyproject.toml", failures, check)
    agent = read_text(root / ".agent/directives/AGENT.md", failures, check)
    if readme is not None:
        require(
            failures,
            check,
            "# Oak Python Repo Template" in readme and "activity-report" in readme,
            "README must describe the template identity and demo CLI",
        )
    if pyproject is not None:
        require(
            failures,
            check,
            'name = "oaknational-python-repo-template"' in pyproject,
            "pyproject must expose the template package name",
        )
        require(
            failures,
            check,
            'activity-report = "oaknational.python_repo_template.demo.activity_report:main"'
            in pyproject,
            "pyproject must expose the activity-report script",
        )
    if agent is not None:
        require(
            failures,
            check,
            "runtime infrastructure" in agent and "demo application" in agent,
            "AGENT.md must describe the three repo strands",
        )
    practice_index = read_text(root / ".agent/practice-index.md", failures, check)
    if practice_index is not None:
        require(
            failures,
            check,
            "practice-core/practice-verification.md" in practice_index
            and "memory/operational/repo-continuity.md" in practice_index
            and "plans/high-level-plan.md" in practice_index
            and "docs/dev-tooling.md" in practice_index,
            "Practice Index must expose verification, continuity, planning, and tooling surfaces",
        )
    return failures


def audit_gate_scripts(root: Path) -> list[str]:
    check = "gate-scripts"
    failures: list[str] = []
    pyproject_path = root / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except OSError as exc:
        failures.append(f"{check}: could not read pyproject.toml: {exc}")
        return failures
    scripts = data.get("project", {}).get("scripts")
    require(
        failures,
        check,
        isinstance(scripts, dict),
        "pyproject.toml must define [project.scripts]",
    )
    if not isinstance(scripts, dict):
        return failures
    for name, target in CANONICAL_GATE_SCRIPTS.items():
        require(
            failures,
            check,
            scripts.get(name) == target,
            f"pyproject.toml must expose {name!r} -> {target!r}",
        )
    for name in LEGACY_GATE_SCRIPTS:
        require(
            failures,
            check,
            name not in scripts,
            f"pyproject.toml must not expose legacy gate script {name!r}",
        )
    return failures


def audit_adapter_parity(root: Path) -> list[str]:
    failures: list[str] = []
    failures.extend(_audit_skill_parity(root))
    failures.extend(_audit_command_parity(root))
    failures.extend(_audit_rule_parity(root))
    failures.extend(_audit_reviewer_parity(root))
    return failures


def _audit_skill_parity(root: Path) -> list[str]:
    check = "skill-parity"
    failures: list[str] = []
    canonical = {
        path.parent.name for path in (root / ".agent/skills").glob("*/SKILL.md") if path.is_file()
    }
    families = [
        (".agents/skills", "", "/SKILL.md"),
        (".claude/skills", "", "/SKILL.md"),
        (".cursor/skills", "", "/SKILL.md"),
        (".gemini/skills", "", "/SKILL.md"),
        (".github/skills", "", "/SKILL.md"),
    ]
    for directory, prefix, suffix in families:
        for name in canonical:
            path = root / directory / f"{prefix}{name}{suffix}"
            require(
                failures,
                check,
                path.exists(),
                f"missing skill adapter {path.relative_to(root)}",
            )
    return failures


def _audit_command_parity(root: Path) -> list[str]:
    check = "command-parity"
    failures: list[str] = []
    canonical = {path.stem for path in (root / ".agent/commands").glob("*.md") if path.is_file()}
    for name in canonical:
        require(
            failures,
            check,
            (root / ".agents/skills" / f"jc-{name}" / "SKILL.md").exists(),
            f"missing Codex command adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".claude/commands" / f"jc-{name}.md").exists(),
            f"missing Claude command adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".cursor/commands" / f"jc-{name}.md").exists(),
            f"missing Cursor command adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".gemini/commands" / f"jc-{name}.toml").exists(),
            f"missing Gemini command adapter for {name}",
        )
    return failures


def _audit_rule_parity(root: Path) -> list[str]:
    check = "rule-parity"
    failures: list[str] = []
    canonical = {path.stem for path in (root / ".agent/rules").glob("*.md") if path.is_file()}
    for name in canonical:
        require(
            failures,
            check,
            (root / ".claude/rules" / f"{name}.md").exists(),
            f"missing Claude rule adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".cursor/rules" / f"{name}.mdc").exists(),
            f"missing Cursor rule adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".github/instructions" / f"{name}.instructions.md").exists(),
            f"missing GitHub instruction adapter for {name}",
        )
    return failures


def _audit_reviewer_parity(root: Path) -> list[str]:
    check = "reviewer-parity"
    failures: list[str] = []
    canonical = {
        path.stem for path in (root / ".agent/sub-agents/templates").glob("*.md") if path.is_file()
    }
    for name in canonical:
        require(
            failures,
            check,
            (root / ".claude/agents" / f"{name}.md").exists(),
            f"missing Claude reviewer adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".cursor/agents" / f"{name}.md").exists(),
            f"missing Cursor reviewer adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".gemini/agents" / f"{name}.md").exists(),
            f"missing Gemini reviewer adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".github/agents" / f"{name}.agent.md").exists(),
            f"missing GitHub reviewer adapter for {name}",
        )
        require(
            failures,
            check,
            (root / ".codex/agents" / f"{name}.toml").exists(),
            f"missing Codex reviewer adapter for {name}",
        )
    return failures


def main() -> None:
    failures: list[str] = []
    checks = [
        audit_required_paths,
        audit_entry_surfaces,
        audit_identity,
        audit_gate_scripts,
        audit_adapter_parity,
    ]
    for check in checks:
        failures.extend(check(REPO_ROOT))
    if failures:
        for failure in failures:
            print(failure)
        raise SystemExit(1)
    print("repo audit passed")


if __name__ == "__main__":
    main()
