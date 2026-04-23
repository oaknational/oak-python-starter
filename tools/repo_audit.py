#!/usr/bin/env python3
"""Audit tracked repo state using filesystem and text inspection."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    ".pre-commit-config.yaml",
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
    "src/oaknational/python_repo_template/py.typed",
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


def _object_mapping(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    mapping: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            return None
        mapping[key] = item
    return mapping


def _string_mapping(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    mapping: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            return None
        mapping[key] = item
    return mapping


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            return None
        items.append(item)
    return items


def _requirement_name(requirement: str) -> str:
    name = requirement
    for separator in ("[", "<", ">", "=", "!", "~", " "):
        name = name.split(separator, maxsplit=1)[0]
    return name.strip()


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
    project_table = _object_mapping(data.get("project"))
    scripts = _string_mapping(project_table.get("scripts")) if project_table is not None else None
    require(
        failures,
        check,
        scripts is not None,
        "pyproject.toml must define [project.scripts]",
    )
    if scripts is None:
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


def audit_packaging_contract(root: Path) -> list[str]:
    check = "packaging-contract"
    failures: list[str] = []
    pyproject_path = root / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except OSError as exc:
        failures.append(f"{check}: could not read pyproject.toml: {exc}")
        return failures

    tool_table = _object_mapping(data.get("tool"))
    hatch_table = _object_mapping(tool_table.get("hatch")) if tool_table is not None else None
    build_table = _object_mapping(hatch_table.get("build")) if hatch_table is not None else None
    targets_table = _object_mapping(build_table.get("targets")) if build_table is not None else None
    wheel_table = _object_mapping(targets_table.get("wheel")) if targets_table is not None else None
    only_include = (
        _string_list(wheel_table.get("only-include")) if wheel_table is not None else None
    )
    sources = _string_list(wheel_table.get("sources")) if wheel_table is not None else None

    require(
        failures,
        check,
        only_include == ["src/oaknational/python_repo_template"],
        "pyproject.toml must package the Oak namespace directory without collapsing it",
    )
    require(
        failures,
        check,
        sources == ["src"],
        "pyproject.toml must strip the src/ prefix while preserving the oaknational namespace path",
    )
    return failures


def audit_typing_contract(root: Path) -> list[str]:
    check = "typing-contract"
    failures: list[str] = []
    pyproject_path = root / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except OSError as exc:
        failures.append(f"{check}: could not read pyproject.toml: {exc}")
        return failures

    tool_table = _object_mapping(data.get("tool"))
    pyright_table = _object_mapping(tool_table.get("pyright")) if tool_table is not None else None
    include = _string_list(pyright_table.get("include")) if pyright_table is not None else None
    type_checking_mode = (
        pyright_table.get("typeCheckingMode") if pyright_table is not None else None
    )
    python_version = pyright_table.get("pythonVersion") if pyright_table is not None else None
    hatch_table = _object_mapping(tool_table.get("hatch")) if tool_table is not None else None
    build_table = _object_mapping(hatch_table.get("build")) if hatch_table is not None else None
    targets_table = _object_mapping(build_table.get("targets")) if build_table is not None else None
    wheel_table = _object_mapping(targets_table.get("wheel")) if targets_table is not None else None
    force_include = (
        _string_mapping(wheel_table.get("force-include")) if wheel_table is not None else None
    )

    require(
        failures,
        check,
        include == ["src", "tests", "tools"],
        "pyproject.toml must configure pyright to cover src, tests, and tools explicitly",
    )
    require(
        failures,
        check,
        type_checking_mode == "strict",
        "pyproject.toml must configure pyright with strict type checking",
    )
    require(
        failures,
        check,
        python_version == "3.14",
        "pyproject.toml must configure pyright for Python 3.14",
    )
    require(
        failures,
        check,
        force_include is not None
        and force_include.get("src/oaknational/python_repo_template/py.typed")
        == "oaknational/python_repo_template/py.typed",
        "pyproject.toml must force-include py.typed in the wheel build",
    )
    return failures


def audit_commit_workflow(root: Path) -> list[str]:
    check = "commit-workflow"
    failures: list[str] = []
    pyproject_path = root / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except OSError as exc:
        failures.append(f"{check}: could not read pyproject.toml: {exc}")
        return failures

    dependency_groups = _object_mapping(data.get("dependency-groups"))
    dev_dependencies = (
        _string_list(dependency_groups.get("dev")) if dependency_groups is not None else None
    )
    tool_table = _object_mapping(data.get("tool"))
    commitizen_table = (
        _object_mapping(tool_table.get("commitizen")) if tool_table is not None else None
    )

    require(
        failures,
        check,
        dev_dependencies is not None
        and any(_requirement_name(requirement) == "commitizen" for requirement in dev_dependencies),
        "pyproject.toml must add commitizen to the dev dependency group",
    )
    require(
        failures,
        check,
        commitizen_table is not None and commitizen_table.get("name") == "cz_conventional_commits",
        "pyproject.toml must configure Commitizen for Conventional Commits",
    )
    require(
        failures,
        check,
        commitizen_table is not None and commitizen_table.get("version_provider") == "uv",
        "pyproject.toml must configure Commitizen to use the uv version provider",
    )

    pre_commit_config = read_text(root / ".pre-commit-config.yaml", failures, check)
    if pre_commit_config is not None:
        require(
            failures,
            check,
            "default_install_hook_types:" in pre_commit_config
            and "- commit-msg" in pre_commit_config,
            ".pre-commit-config.yaml must install commit-msg hooks by default",
        )
        require(
            failures,
            check,
            "id: commitizen-commit-msg" in pre_commit_config
            and "entry: uv run cz check --allow-abort --commit-msg-file" in pre_commit_config
            and "stages: [commit-msg]" in pre_commit_config,
            ".pre-commit-config.yaml must enforce commit messages with Commitizen at commit-msg",
        )

    readme = read_text(root / "README.md", failures, check)
    if readme is not None:
        require(
            failures,
            check,
            "uv run pre-commit install" in readme
            and "uv run cz commit" in readme
            and "uv run cz check" in readme,
            "README must document hook installation plus Commitizen commit creation and validation",
        )

    tooling_doc = read_text(root / "docs/dev-tooling.md", failures, check)
    if tooling_doc is not None:
        require(
            failures,
            check,
            "commitizen" in tooling_doc
            and "uv run cz commit" in tooling_doc
            and "uv run cz check" in tooling_doc,
            "docs/dev-tooling.md must document the Commitizen workflow",
        )

    commit_command = read_text(root / ".agent/commands/commit.md", failures, check)
    if commit_command is not None:
        require(
            failures,
            check,
            "uv run cz commit" in commit_command and "uv run cz check" in commit_command,
            (
                ".agent/commands/commit.md must direct commit creation and validation "
                "through Commitizen"
            ),
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
        audit_packaging_contract,
        audit_typing_contract,
        audit_commit_workflow,
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
