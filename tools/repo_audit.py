#!/usr/bin/env python3
"""Audit tracked repo state using structural contract validation."""

from __future__ import annotations

import ast
import json
import sys
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TextIO, cast

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS_MODULE = "oaknational.python_repo_template.devtools"
ACTIVITY_REPORT_TARGET = "oaknational.python_repo_template.demo.activity_report:main"
REPO_LOCAL_DEVTOOLS_COMMAND = "uv run python -m oaknational.python_repo_template.devtools"
REPO_AUDIT_CONTRACT_PATH = REPO_ROOT / "tools" / "repo_audit_contract.toml"
HOOK_RUNTIME_COMMAND = "uv run python tools/agent_hooks.py"
QUALITY_GATES_ENTRY = f"{REPO_LOCAL_DEVTOOLS_COMMAND} check-ci"
CHECK_COMMAND = f"{REPO_LOCAL_DEVTOOLS_COMMAND} check"
CURSOR_SESSION_START_COMMAND = f"{HOOK_RUNTIME_COMMAND} --platform cursor --event session-start"
CURSOR_PRE_TOOL_COMMAND = f"{HOOK_RUNTIME_COMMAND} --platform cursor --event pre-tool"
CLAUDE_SESSION_START_COMMAND = (
    f'cd "$CLAUDE_PROJECT_DIR" && {HOOK_RUNTIME_COMMAND} --platform claude --event session-start'
)
CLAUDE_PRE_TOOL_COMMAND = (
    f'cd "$CLAUDE_PROJECT_DIR" && {HOOK_RUNTIME_COMMAND} --platform claude --event pre-tool'
)
GEMINI_SESSION_START_COMMAND = (
    f'cd "$GEMINI_PROJECT_DIR" && {HOOK_RUNTIME_COMMAND} --platform gemini --event session-start'
)
GEMINI_PRE_TOOL_COMMAND = (
    f'cd "$GEMINI_PROJECT_DIR" && {HOOK_RUNTIME_COMMAND} --platform gemini --event pre-tool'
)
GITHUB_PRE_TOOL_COMMAND = f"{HOOK_RUNTIME_COMMAND} --platform github --event pre-tool"
REQUIRED_HOOK_POLICY_PATTERNS = {
    "(^|\\s)git\\s+stash(\\s|$)": (
        "git stash is prohibited here because it can lose uncommitted work."
    ),
    "(^|\\s)git\\s+reset(\\s|$)": (
        "git reset is prohibited here because it can discard commits or changes."
    ),
    "(^|\\s)git\\s+checkout\\s+--(\\s|$)": (
        "git checkout -- is prohibited here because it discards uncommitted changes."
    ),
    "(^|\\s)git\\s+clean(\\s|$)": (
        "git clean is prohibited here because it deletes untracked files."
    ),
    "(^|\\s)git\\s+rebase(\\s|$)": ("git rebase is prohibited here because it rewrites history."),
    "(^|\\s)--no-verify(\\s|$)": ("--no-verify is prohibited here because it bypasses git hooks."),
    "(^|\\s)git\\s+push\\b[^\\n]*\\s(--force(?:-with-lease)?|-f)(\\s|$)": (
        "Force push is prohibited here because it overwrites remote history."
    ),
}
REQUIRED_HOOK_BYPASS_FLAGS = {
    "--no-pre-commit": ("--no-pre-commit is prohibited here because it bypasses pre-commit hooks."),
}
REQUIRED_HOOK_BYPASS_ENV_VARS = {
    ("HUSKY", "0"): "HUSKY=0 is prohibited here because it disables git hooks.",
    ("SKIP_HOOKS", "1"): ("SKIP_HOOKS=1 is prohibited here because it disables git hooks."),
}
REQUIRED_HOOK_GIT_CONFIG_OVERRIDES = {
    "core.hooksPath": (
        "core.hooksPath overrides are prohibited here because they bypass repo git hooks."
    ),
}
REQUIRED_HOOK_BYPASS_ENV_VAR_PREFIXES = {
    "GIT_CONFIG_": (
        "GIT_CONFIG_* is prohibited here because it can hide hook bypasses or force pushes."
    ),
}
REQUIRED_HOOK_GIT_CONFIG_PREFIXES = {
    "alias.": (
        "Git alias overrides are prohibited here because they can hide hook "
        "bypasses or force pushes."
    ),
}
REQUIRED_PRE_COMMIT_SKIP_IDS = ("quality-gates", "commitizen-commit-msg")
REQUIRED_PRE_COMMIT_SKIP_REASON = (
    "SKIP is prohibited here when it bypasses the repo's quality-gates or "
    "commitizen-commit-msg hooks."
)
REQUIRED_DYNAMIC_GIT_CONFIG_REASON = (
    "Dynamic git config is prohibited here for git commit and git push because "
    "it can hide hook bypasses or force pushes."
)
EXPECTED_HOOK_SUPPORT = {
    "Cursor": "portable",
    "Codex": "unsupported",
    "Claude": "portable",
    "Gemini": "portable",
    "GitHub": "portable",
}
AuditFunction = Callable[[Path], list[str]]
REQUIRED_PATHS = [
    "README.md",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    "pyrightconfig.json",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".agent/directives/AGENT.md",
    ".agent/directives/orientation.md",
    ".agent/directives/principles.md",
    ".agent/directives/testing-strategy.md",
    ".agent/practice-index.md",
    ".agent/VISION.md",
    ".agent/rules/no-monkeypatching-in-python-tests.md",
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
    "src/oaknational/python_repo_template/gate_contract.toml",
    "src/oaknational/python_repo_template/gate_registry.py",
    "src/oaknational/python_repo_template/data/activity_store.py",
    "src/oaknational/python_repo_template/demo/activity_report.py",
    "tools/__init__.py",
    "tools/agent_hooks.py",
    "tools/repo_audit_contract.toml",
    "tools/repo_audit.py",
    "tests/test_agent_hooks.py",
    "tests/test_activity_store.py",
    "tests/test_activity_report.py",
    "tests/test_devtools.py",
    "tests/test_gate_registry.py",
    "tests/test_package_entrypoint.py",
    "tests/test_repo_audit.py",
    "data/fixtures/activity_log.csv",
    "data/fixtures/activity_log.metadata.yaml",
    "docs/architecture-decision-records/ADR-0001-cross-platform-practice-surface-contract.md",
    "docs/explorations/README.md",
    "docs/dev-tooling.md",
]


def _object_mapping(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    mapping: dict[str, object] = {}
    for key, item in cast(dict[object, object], value).items():
        if not isinstance(key, str):
            return None
        mapping[key] = item
    return mapping


def _string_mapping(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    mapping: dict[str, str] = {}
    for key, item in cast(dict[object, object], value).items():
        if not isinstance(key, str) or not isinstance(item, str):
            return None
        mapping[key] = item
    return mapping


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    items: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str):
            return None
        items.append(item)
    return items


def _string_tuple(value: object) -> tuple[str, ...] | None:
    items = _string_list(value)
    return None if items is None else tuple(items)


def _string_list_mapping(value: object) -> dict[str, tuple[str, ...]] | None:
    if not isinstance(value, dict):
        return None
    mapping: dict[str, tuple[str, ...]] = {}
    for key, item in cast(dict[object, object], value).items():
        if not isinstance(key, str):
            return None
        items = _string_tuple(item)
        if items is None:
            return None
        mapping[key] = items
    return mapping


def _object_list(value: object) -> list[dict[str, object]] | None:
    if not isinstance(value, list):
        return None
    items: list[dict[str, object]] = []
    for item in cast(list[object], value):
        mapping = _object_mapping(item)
        if mapping is None:
            return None
        items.append(mapping)
    return items


def _load_toml(path: Path, failures: list[str], check: str) -> dict[str, object] | None:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        failures.append(f"{check}: invalid TOML in {_relative_path(path)}: {exc}")
        return None
    except OSError as exc:
        failures.append(f"{check}: could not read {_relative_path(path)}: {exc}")
        return None


def _load_json(path: Path, failures: list[str], check: str) -> dict[str, object] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{check}: invalid JSON in {_relative_path(path)}: {exc}")
        return None
    except OSError as exc:
        failures.append(f"{check}: could not read {_relative_path(path)}: {exc}")
        return None
    mapping = _object_mapping(raw)
    if mapping is None:
        failures.append(f"{check}: {_relative_path(path)} must define a top-level JSON object")
        return None
    return mapping


def _load_yaml(path: Path, failures: list[str], check: str) -> object | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        failures.append(f"{check}: invalid YAML in {_relative_path(path)}: {exc}")
        return None
    except OSError as exc:
        failures.append(f"{check}: could not read {_relative_path(path)}: {exc}")
        return None


def _load_pyproject(root: Path, failures: list[str], check: str) -> dict[str, object] | None:
    return _load_toml(root / "pyproject.toml", failures, check)


def _load_gate_contract(root: Path, failures: list[str], check: str) -> dict[str, object] | None:
    contract_path = root / "src" / "oaknational" / "python_repo_template" / "gate_contract.toml"
    if not contract_path.exists() and root != REPO_ROOT:
        contract_path = (
            REPO_ROOT / "src" / "oaknational" / "python_repo_template" / "gate_contract.toml"
        )
    return _load_toml(contract_path, failures, check)


def _load_repo_audit_contract(
    root: Path, failures: list[str], check: str
) -> dict[str, object] | None:
    contract_path = root / "tools" / "repo_audit_contract.toml"
    if not contract_path.exists() and root != REPO_ROOT:
        contract_path = REPO_AUDIT_CONTRACT_PATH
    return _load_toml(contract_path, failures, check)


def _gate_contract_repo_local_commands(
    contract: dict[str, object],
    failures: list[str],
    check: str,
) -> dict[str, str] | None:
    repo_local_commands = _string_mapping(contract.get("repo_local_commands"))
    require(
        failures,
        check,
        repo_local_commands is not None,
        "gate contract must define [repo_local_commands] with string targets",
    )
    if repo_local_commands is None:
        return None
    return {
        name: f"{DEVTOOLS_MODULE}:{handler_name}"
        for name, handler_name in repo_local_commands.items()
    }


def _legacy_public_commands(
    contract: dict[str, object],
    failures: list[str],
    check: str,
) -> tuple[str, ...] | None:
    legacy_commands = _string_tuple(contract.get("legacy_public_commands"))
    require(
        failures,
        check,
        legacy_commands is not None,
        "repo audit contract must define legacy_public_commands as a string list",
    )
    return legacy_commands


def _published_entry_points(
    contract: dict[str, object],
    failures: list[str],
    check: str,
) -> dict[str, str] | None:
    published_entry_points = _string_mapping(contract.get("published_entry_points"))
    require(
        failures,
        check,
        published_entry_points is not None,
        "repo audit contract must define [published_entry_points] with string targets",
    )
    return published_entry_points


def _documentation_commands(
    contract: dict[str, object],
    failures: list[str],
    check: str,
) -> dict[str, tuple[str, ...]] | None:
    documentation_commands = _string_list_mapping(contract.get("documentation_commands"))
    require(
        failures,
        check,
        documentation_commands is not None,
        "repo audit contract must define [documentation_commands] with string-list values",
    )
    return documentation_commands


def _gate_sequences(
    contract: dict[str, object],
    failures: list[str],
    check: str,
) -> dict[str, tuple[str, ...]] | None:
    raw_sequences = _object_mapping(contract.get("gate_sequences"))
    require(
        failures,
        check,
        raw_sequences is not None,
        "gate contract must define [gate_sequences]",
    )
    if raw_sequences is None:
        return None

    sequences: dict[str, tuple[str, ...]] = {}
    for name, value in raw_sequences.items():
        sequence = _string_tuple(value)
        require(
            failures,
            check,
            sequence is not None,
            f"gate contract sequence {name!r} must be a string list",
        )
        if sequence is not None:
            sequences[name] = sequence
    return sequences


def _relative_path(path: Path) -> Path | str:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def _requirement_name(requirement: str) -> str:
    name = requirement
    for separator in ("[", "<", ">", "=", "!", "~", " "):
        name = name.split(separator, maxsplit=1)[0]
    return name.strip()


def read_text(path: Path, failures: list[str], check: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        failures.append(f"{check}: could not read {_relative_path(path)}: {exc}")
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
    pyproject = _load_pyproject(root, failures, check)
    agent = read_text(root / ".agent/directives/AGENT.md", failures, check)
    if readme is not None:
        require(
            failures,
            check,
            "# Oak Python Repo Template" in readme and "activity-report" in readme,
            "README must describe the template identity and demo CLI",
        )
    if pyproject is not None:
        project_table = _object_mapping(pyproject.get("project"))
        scripts = (
            _string_mapping(project_table.get("scripts")) if project_table is not None else None
        )
        require(
            failures,
            check,
            project_table is not None
            and project_table.get("name") == "oaknational-python-repo-template",
            "pyproject must expose the template package name",
        )
        require(
            failures,
            check,
            scripts is not None and scripts.get("activity-report") == ACTIVITY_REPORT_TARGET,
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
    gate_contract = _load_gate_contract(root, failures, check)
    repo_audit_contract = _load_repo_audit_contract(root, failures, check)
    data = _load_pyproject(root, failures, check)
    if gate_contract is None or repo_audit_contract is None or data is None:
        return failures

    repo_local_commands = _gate_contract_repo_local_commands(gate_contract, failures, check)
    legacy_commands = _legacy_public_commands(repo_audit_contract, failures, check)
    published_entry_points = _published_entry_points(repo_audit_contract, failures, check)
    if repo_local_commands is None or legacy_commands is None or published_entry_points is None:
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

    for name, target in published_entry_points.items():
        require(
            failures,
            check,
            scripts.get(name) == target,
            f"pyproject.toml must expose {name!r} -> {target!r}",
        )
    for name in sorted(set((*legacy_commands, *repo_local_commands))):
        require(
            failures,
            check,
            name not in scripts,
            f"pyproject.toml must not expose repo-local devtools command {name!r}",
        )

    unexpected_scripts = sorted(name for name in scripts if name not in published_entry_points)
    require(
        failures,
        check,
        not unexpected_scripts,
        f"pyproject.toml must not expose unexpected public scripts: {unexpected_scripts}",
    )
    return failures


def audit_packaging_contract(root: Path) -> list[str]:
    check = "packaging-contract"
    failures: list[str] = []
    data = _load_pyproject(root, failures, check)
    if data is None:
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
    data = _load_pyproject(root, failures, check)
    pyright_config = _load_json(root / "pyrightconfig.json", failures, check)
    if data is None or pyright_config is None:
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
    config_include = _string_list(pyright_config.get("include"))
    config_type_checking_mode = pyright_config.get("typeCheckingMode")
    config_python_version = pyright_config.get("pythonVersion")

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
    require(
        failures,
        check,
        config_include == ["src", "tests", "tools"],
        "pyrightconfig.json must configure pyright to cover src, tests, and tools explicitly",
    )
    require(
        failures,
        check,
        config_type_checking_mode == "strict",
        "pyrightconfig.json must configure pyright with strict type checking",
    )
    require(
        failures,
        check,
        config_python_version == "3.14",
        "pyrightconfig.json must configure pyright for Python 3.14",
    )
    return failures


def audit_commit_workflow(root: Path) -> list[str]:
    check = "commit-workflow"
    failures: list[str] = []
    data = _load_pyproject(root, failures, check)
    if data is None:
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

    pre_commit_config = _load_yaml(root / ".pre-commit-config.yaml", failures, check)
    pre_commit_mapping = _object_mapping(pre_commit_config)
    require(
        failures,
        check,
        pre_commit_mapping is not None,
        ".pre-commit-config.yaml must define a top-level mapping",
    )
    if pre_commit_mapping is not None:
        default_install_hook_types = _string_list(
            pre_commit_mapping.get("default_install_hook_types")
        )
        repos = _object_list(pre_commit_mapping.get("repos"))
        local_repo = None
        if repos is not None:
            for repo_entry in repos:
                if repo_entry.get("repo") == "local":
                    local_repo = repo_entry
                    break
        hooks = _object_list(local_repo.get("hooks")) if local_repo is not None else None
        hook_by_id = {
            hook_id: hook
            for hook in hooks or []
            for hook_id in [hook.get("id")]
            if isinstance(hook_id, str)
        }
        require(
            failures,
            check,
            default_install_hook_types == ["pre-commit", "pre-push", "commit-msg"],
            ".pre-commit-config.yaml must install commit-msg hooks by default",
        )
        quality_gates_hook = hook_by_id.get("quality-gates")
        require(
            failures,
            check,
            quality_gates_hook is not None
            and quality_gates_hook.get("entry") == QUALITY_GATES_ENTRY
            and quality_gates_hook.get("language") == "system"
            and _string_list(quality_gates_hook.get("stages")) == ["pre-commit", "pre-push"]
            and quality_gates_hook.get("pass_filenames") is False,
            (
                ".pre-commit-config.yaml must enforce quality gates with the repo-local "
                "check-ci command at pre-commit and pre-push"
            ),
        )
        commitizen_hook = hook_by_id.get("commitizen-commit-msg")
        require(
            failures,
            check,
            commitizen_hook is not None
            and commitizen_hook.get("entry") == "uv run cz check --allow-abort --commit-msg-file"
            and commitizen_hook.get("language") == "system"
            and _string_list(commitizen_hook.get("stages")) == ["commit-msg"],
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


def audit_hook_contract(root: Path) -> list[str]:
    check = "hook-contract"
    failures: list[str] = []

    policy = _load_json(root / ".agent/hooks/policy.json", failures, check)
    if policy is not None:
        require(
            failures,
            check,
            policy.get("session_start_message")
            == "Read .agent/commands/start-right-quick.md before substantive work.",
            ".agent/hooks/policy.json must keep the canonical session-start grounding message",
        )
        require(
            failures,
            check,
            policy.get("quality_gate_message")
            == (
                "If Python or tooling files change, run uv run python -m "
                "oaknational.python_repo_template.devtools check before you stop."
            ),
            ".agent/hooks/policy.json must keep the repo-local quality-gate reminder",
        )
        blocked_patterns = _object_list(policy.get("blocked_shell_patterns"))
        require(
            failures,
            check,
            blocked_patterns is not None,
            ".agent/hooks/policy.json must define blocked_shell_patterns as an object list",
        )
        if blocked_patterns is not None:
            actual_patterns = {
                pattern.get("pattern"): pattern.get("reason") for pattern in blocked_patterns
            }
            for pattern, reason in REQUIRED_HOOK_POLICY_PATTERNS.items():
                require(
                    failures,
                    check,
                    actual_patterns.get(pattern) == reason,
                    f".agent/hooks/policy.json must block {pattern!r} with the canonical reason",
                )
        blocked_flags = _object_list(policy.get("blocked_hook_bypass_flags"))
        require(
            failures,
            check,
            blocked_flags is not None,
            ".agent/hooks/policy.json must define blocked_hook_bypass_flags as an object list",
        )
        if blocked_flags is not None:
            actual_flags = {flag.get("token"): flag.get("reason") for flag in blocked_flags}
            for token, reason in REQUIRED_HOOK_BYPASS_FLAGS.items():
                require(
                    failures,
                    check,
                    actual_flags.get(token) == reason,
                    f".agent/hooks/policy.json must block hook-bypass flag {token!r}",
                )
        blocked_envs = _object_list(policy.get("blocked_hook_bypass_env_vars"))
        require(
            failures,
            check,
            blocked_envs is not None,
            (".agent/hooks/policy.json must define blocked_hook_bypass_env_vars as an object list"),
        )
        if blocked_envs is not None:
            actual_envs = {
                (env.get("name"), env.get("value")): env.get("reason") for env in blocked_envs
            }
            for assignment, reason in REQUIRED_HOOK_BYPASS_ENV_VARS.items():
                require(
                    failures,
                    check,
                    actual_envs.get(assignment) == reason,
                    (
                        ".agent/hooks/policy.json must block hook-bypass env assignment "
                        f"{assignment[0]}={assignment[1]}"
                    ),
                )
        blocked_git_configs = _object_list(policy.get("blocked_git_config_overrides"))
        require(
            failures,
            check,
            blocked_git_configs is not None,
            ".agent/hooks/policy.json must define blocked_git_config_overrides as an object list",
        )
        if blocked_git_configs is not None:
            actual_git_configs = {
                config_override.get("name"): config_override.get("reason")
                for config_override in blocked_git_configs
            }
            for name, reason in REQUIRED_HOOK_GIT_CONFIG_OVERRIDES.items():
                require(
                    failures,
                    check,
                    actual_git_configs.get(name) == reason,
                    (
                        ".agent/hooks/policy.json must block git config override "
                        f"{name!r} with the canonical reason"
                    ),
                )
        blocked_env_prefixes = _object_list(policy.get("blocked_hook_bypass_env_var_prefixes"))
        require(
            failures,
            check,
            blocked_env_prefixes is not None,
            (
                ".agent/hooks/policy.json must define blocked_hook_bypass_env_var_prefixes "
                "as an object list"
            ),
        )
        if blocked_env_prefixes is not None:
            actual_env_prefixes = {
                prefix.get("prefix"): prefix.get("reason") for prefix in blocked_env_prefixes
            }
            for prefix, reason in REQUIRED_HOOK_BYPASS_ENV_VAR_PREFIXES.items():
                require(
                    failures,
                    check,
                    actual_env_prefixes.get(prefix) == reason,
                    f".agent/hooks/policy.json must block env prefix {prefix!r}",
                )
        blocked_git_prefixes = _object_list(policy.get("blocked_git_config_prefixes"))
        require(
            failures,
            check,
            blocked_git_prefixes is not None,
            ".agent/hooks/policy.json must define blocked_git_config_prefixes as an object list",
        )
        if blocked_git_prefixes is not None:
            actual_git_prefixes = {
                prefix.get("prefix"): prefix.get("reason") for prefix in blocked_git_prefixes
            }
            for prefix, reason in REQUIRED_HOOK_GIT_CONFIG_PREFIXES.items():
                require(
                    failures,
                    check,
                    actual_git_prefixes.get(prefix) == reason,
                    f".agent/hooks/policy.json must block git config prefix {prefix!r}",
                )
        require(
            failures,
            check,
            _string_tuple(policy.get("blocked_pre_commit_skip_ids"))
            == REQUIRED_PRE_COMMIT_SKIP_IDS,
            ".agent/hooks/policy.json must list the canonical blocked pre-commit skip ids",
        )
        require(
            failures,
            check,
            policy.get("blocked_pre_commit_skip_reason") == REQUIRED_PRE_COMMIT_SKIP_REASON,
            ".agent/hooks/policy.json must define the canonical pre-commit skip reason",
        )
        require(
            failures,
            check,
            policy.get("blocked_dynamic_git_config_reason") == REQUIRED_DYNAMIC_GIT_CONFIG_REASON,
            ".agent/hooks/policy.json must define the canonical dynamic git-config reason",
        )

    cursor_hooks = _load_json(root / ".cursor/hooks.json", failures, check)
    if cursor_hooks is not None:
        cursor_hook_mapping = _object_mapping(cursor_hooks.get("hooks"))
        session_start = (
            _object_list(cursor_hook_mapping.get("sessionStart"))
            if cursor_hook_mapping is not None
            else None
        )
        pre_tool_use = (
            _object_list(cursor_hook_mapping.get("preToolUse"))
            if cursor_hook_mapping is not None
            else None
        )
        require(
            failures,
            check,
            session_start is not None
            and len(session_start) == 1
            and session_start[0].get("command") == CURSOR_SESSION_START_COMMAND
            and session_start[0].get("timeout") == 30,
            ".cursor/hooks.json must wire the canonical session-start hook runtime",
        )
        require(
            failures,
            check,
            pre_tool_use is not None
            and len(pre_tool_use) == 1
            and pre_tool_use[0].get("command") == CURSOR_PRE_TOOL_COMMAND
            and pre_tool_use[0].get("timeout") == 30
            and pre_tool_use[0].get("matcher") == "Shell",
            ".cursor/hooks.json must wire the canonical pre-tool hook runtime",
        )

    claude_settings = _load_json(root / ".claude/settings.json", failures, check)
    if claude_settings is not None:
        claude_hook_mapping = _object_mapping(claude_settings.get("hooks"))
        session_start = (
            _object_list(claude_hook_mapping.get("SessionStart"))
            if claude_hook_mapping is not None
            else None
        )
        pre_tool_use = (
            _object_list(claude_hook_mapping.get("PreToolUse"))
            if claude_hook_mapping is not None
            else None
        )
        claude_session_hooks = (
            _object_list(session_start[0].get("hooks"))
            if session_start is not None and len(session_start) == 1
            else None
        )
        claude_pre_tool_hooks = (
            _object_list(pre_tool_use[0].get("hooks"))
            if pre_tool_use is not None and len(pre_tool_use) == 1
            else None
        )
        require(
            failures,
            check,
            session_start is not None
            and len(session_start) == 1
            and session_start[0].get("matcher") == ""
            and claude_session_hooks is not None
            and claude_session_hooks[0].get("type") == "command"
            and claude_session_hooks[0].get("command") == CLAUDE_SESSION_START_COMMAND,
            ".claude/settings.json must wire the canonical session-start hook runtime",
        )
        require(
            failures,
            check,
            pre_tool_use is not None
            and len(pre_tool_use) == 1
            and pre_tool_use[0].get("matcher") == "Bash"
            and claude_pre_tool_hooks is not None
            and claude_pre_tool_hooks[0].get("type") == "command"
            and claude_pre_tool_hooks[0].get("command") == CLAUDE_PRE_TOOL_COMMAND,
            ".claude/settings.json must wire the canonical pre-tool hook runtime",
        )

    gemini_settings = _load_json(root / ".gemini/settings.json", failures, check)
    if gemini_settings is not None:
        gemini_hook_mapping = _object_mapping(gemini_settings.get("hooks"))
        gemini_experimental = _object_mapping(gemini_settings.get("experimental"))
        session_start = (
            _object_list(gemini_hook_mapping.get("SessionStart"))
            if gemini_hook_mapping is not None
            else None
        )
        before_tool = (
            _object_list(gemini_hook_mapping.get("BeforeTool"))
            if gemini_hook_mapping is not None
            else None
        )
        gemini_session_hooks = (
            _object_list(session_start[0].get("hooks"))
            if session_start is not None and len(session_start) == 1
            else None
        )
        gemini_pre_tool_hooks = (
            _object_list(before_tool[0].get("hooks"))
            if before_tool is not None and len(before_tool) == 1
            else None
        )
        require(
            failures,
            check,
            gemini_experimental is not None and gemini_experimental.get("enableAgents") is True,
            ".gemini/settings.json must keep Gemini agents enabled for the repo's adapter surface",
        )
        require(
            failures,
            check,
            session_start is not None
            and len(session_start) == 1
            and session_start[0].get("matcher") == ""
            and gemini_session_hooks is not None
            and gemini_session_hooks[0].get("type") == "command"
            and gemini_session_hooks[0].get("name") == "repo-grounding"
            and gemini_session_hooks[0].get("command") == GEMINI_SESSION_START_COMMAND
            and gemini_session_hooks[0].get("timeout") == 5000,
            ".gemini/settings.json must wire the canonical session-start hook runtime",
        )
        require(
            failures,
            check,
            before_tool is not None
            and len(before_tool) == 1
            and before_tool[0].get("matcher") == "^run_shell_command$"
            and gemini_pre_tool_hooks is not None
            and gemini_pre_tool_hooks[0].get("type") == "command"
            and gemini_pre_tool_hooks[0].get("name") == "repo-shell-guardrails"
            and gemini_pre_tool_hooks[0].get("command") == GEMINI_PRE_TOOL_COMMAND
            and gemini_pre_tool_hooks[0].get("timeout") == 5000,
            ".gemini/settings.json must wire the canonical pre-tool hook runtime",
        )

    github_guardrails = _load_json(root / ".github/hooks/guardrails.json", failures, check)
    if github_guardrails is not None:
        github_hook_mapping = _object_mapping(github_guardrails.get("hooks"))
        pre_tool_use = (
            _object_list(github_hook_mapping.get("preToolUse"))
            if github_hook_mapping is not None
            else None
        )
        require(
            failures,
            check,
            pre_tool_use is not None
            and len(pre_tool_use) == 1
            and pre_tool_use[0].get("type") == "command"
            and pre_tool_use[0].get("bash") == GITHUB_PRE_TOOL_COMMAND
            and pre_tool_use[0].get("timeoutSec") == 30,
            ".github/hooks/guardrails.json must wire the canonical GitHub pre-tool hook runtime",
        )

    matrix_text = read_text(
        root / ".agent/memory/executive/cross-platform-agent-surface-matrix.md",
        failures,
        check,
    )
    if matrix_text is not None:
        matrix = _parse_support_matrix(matrix_text)
        require(
            failures,
            check,
            matrix is not None,
            "cross-platform-agent-surface-matrix.md must contain a parseable table",
        )
        if matrix is not None:
            hooks_row = matrix.get("hooks")
            require(
                failures,
                check,
                hooks_row is not None,
                "cross-platform-agent-surface-matrix.md must define a hooks row",
            )
            if hooks_row is not None:
                for platform, expected in EXPECTED_HOOK_SUPPORT.items():
                    require(
                        failures,
                        check,
                        hooks_row.get(platform) == expected,
                        (
                            "cross-platform-agent-surface-matrix.md must record "
                            f"{platform} hooks as {expected}"
                        ),
                    )

    adr_text = read_text(
        root
        / "docs/architecture-decision-records"
        / "ADR-0001-cross-platform-practice-surface-contract.md",
        failures,
        check,
    )
    if adr_text is not None:
        require(
            failures,
            check,
            "The live support contract is the operational matrix." in adr_text
            and "including Gemini hook support" in adr_text,
            "ADR-0001 must keep the matrix as the hook-support source of truth",
        )

    return failures


def audit_repo_local_command_surface(root: Path) -> list[str]:
    check = "repo-local-command-surface"
    failures: list[str] = []
    gate_contract = _load_gate_contract(root, failures, check)
    repo_audit_contract = _load_repo_audit_contract(root, failures, check)
    if gate_contract is None or repo_audit_contract is None:
        return failures
    repo_local_commands = _gate_contract_repo_local_commands(gate_contract, failures, check)
    documentation_commands = _documentation_commands(repo_audit_contract, failures, check)
    if repo_local_commands is None or documentation_commands is None:
        return failures
    for relative_path, commands in documentation_commands.items():
        text = read_text(root / relative_path, failures, check)
        if text is None:
            continue
        for command in commands:
            require(
                failures,
                check,
                command in repo_local_commands,
                (
                    f"{relative_path} must only document repo-local commands defined "
                    f"in gate_contract.toml; {command!r} is unknown"
                ),
            )
            if command not in repo_local_commands:
                continue
            require(
                failures,
                check,
                f"{REPO_LOCAL_DEVTOOLS_COMMAND} {command}" in text,
                f"{relative_path} must document the repo-local {command!r} command",
            )
            require(
                failures,
                check,
                f"uv run {command}" not in text,
                f"{relative_path} must not document the published-wheel form uv run {command}",
            )
    return failures


def audit_dependency_hygiene(root: Path) -> list[str]:
    check = "dependency-hygiene"
    failures: list[str] = []
    contract = _load_gate_contract(root, failures, check)
    pyproject_path = root / "pyproject.toml"
    data = _load_toml(pyproject_path, failures, check)
    if contract is None or data is None:
        return failures

    gate_sequences = _gate_sequences(contract, failures, check)
    dependency_groups = _object_mapping(data.get("dependency-groups"))
    dev_dependencies = (
        _string_list(dependency_groups.get("dev")) if dependency_groups is not None else None
    )
    tool_table = _object_mapping(data.get("tool"))
    deptry_table = _object_mapping(tool_table.get("deptry")) if tool_table is not None else None
    deptry_keys = set(deptry_table) if deptry_table is not None else None
    known_first_party = (
        _string_list(deptry_table.get("known_first_party")) if deptry_table is not None else None
    )
    per_rule_ignores = (
        _object_mapping(deptry_table.get("per_rule_ignores")) if deptry_table is not None else None
    )
    per_rule_ignore_keys = set(per_rule_ignores) if per_rule_ignores is not None else None
    dep002_ignores = (
        _string_list(per_rule_ignores.get("DEP002")) if per_rule_ignores is not None else None
    )

    require(
        failures,
        check,
        dev_dependencies is not None
        and any(_requirement_name(requirement) == "deptry" for requirement in dev_dependencies),
        "pyproject.toml must add deptry to the dev dependency group",
    )
    require(
        failures,
        check,
        deptry_keys == {"known_first_party", "per_rule_ignores"},
        "pyproject.toml must keep [tool.deptry] small and explicit",
    )
    require(
        failures,
        check,
        known_first_party == ["oaknational"],
        "pyproject.toml must configure deptry to treat the Oak namespace as first party",
    )
    require(
        failures,
        check,
        per_rule_ignore_keys == {"DEP002"},
        "pyproject.toml must limit deptry per-rule ignores to the single DEP002 exception",
    )
    require(
        failures,
        check,
        dep002_ignores == ["pyarrow"],
        "pyproject.toml must document the single DEP002 ignore for pyarrow",
    )

    readme = read_text(root / "README.md", failures, check)
    if readme is not None:
        require(
            failures,
            check,
            "uv run deptry ." in readme and "dependency hygiene" in readme.lower(),
            "README must document the direct deptry command and aggregate dependency-hygiene gate",
        )
        require(
            failures,
            check,
            "not vulnerability scanning" in readme.lower(),
            "README must explain that deptry is not vulnerability scanning",
        )

    tooling_doc = read_text(root / "docs/dev-tooling.md", failures, check)
    if tooling_doc is not None:
        require(
            failures,
            check,
            "deptry" in tooling_doc and "uv run deptry ." in tooling_doc,
            "docs/dev-tooling.md must document deptry and its direct command surface",
        )
        require(
            failures,
            check,
            "not vulnerability scanning" in tooling_doc.lower(),
            "docs/dev-tooling.md must explain that deptry is not vulnerability scanning",
        )

    gates_command = read_text(root / ".agent/commands/gates.md", failures, check)
    if gates_command is not None:
        require(
            failures,
            check,
            "dependency hygiene" in gates_command.lower() and "uv run deptry ." in gates_command,
            ".agent/commands/gates.md must document the dependency-hygiene gate",
        )

    start_right_skill = read_text(
        root / ".agent/skills/start-right-quick/SKILL.md", failures, check
    )
    check_ci_sequence = gate_sequences.get("check-ci") if gate_sequences is not None else None
    if start_right_skill is not None and check_ci_sequence is not None:
        require(
            failures,
            check,
            " -> ".join(check_ci_sequence) in start_right_skill,
            (
                ".agent/skills/start-right-quick/SKILL.md must document the exact "
                "check-ci gate sequence"
            ),
        )

    return failures


def audit_python_test_practice(root: Path) -> list[str]:
    check = "python-test-practice"
    failures: list[str] = []
    for path in sorted((root / "tests").rglob("*.py")):
        text = read_text(path, failures, check)
        if text is None:
            continue
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{check}: could not parse {path.relative_to(root)}: {exc}")
            continue
        violations = _test_patch_helper_violations(tree)
        if violations:
            detail = ", ".join(sorted(set(violations)))
            failures.append(
                f"{check}: {path.relative_to(root)} must not use runtime patch helpers ({detail})"
            )
    return failures


def _test_patch_helper_violations(tree: ast.AST) -> list[str]:
    visitor = _TestPatchHelperVisitor()
    visitor.visit(tree)
    return visitor.violations


class _TestPatchHelperVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[str] = []
        self.pytest_module_names = {"pytest"}
        self.unittest_module_names = {"unittest"}
        self.unittest_mock_module_names = {"unittest.mock"}
        self.monkeypatch_type_names: set[str] = set()
        self.patch_names: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            bound_name = alias.asname or alias.name
            if alias.name == "pytest":
                self.pytest_module_names.add(bound_name)
            if alias.name == "unittest":
                self.unittest_module_names.add(bound_name)
            if alias.name == "unittest.mock":
                self.unittest_mock_module_names.add(bound_name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function_arguments(node.args)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function_arguments(node.args)
        self.generic_visit(node)

    def _record_function_arguments(self, arguments: ast.arguments) -> None:
        argument_names = [argument.arg for argument in arguments.args]
        argument_names.extend(argument.arg for argument in arguments.kwonlyargs)
        if arguments.vararg is not None:
            argument_names.append(arguments.vararg.arg)
        if arguments.kwarg is not None:
            argument_names.append(arguments.kwarg.arg)
        if "monkeypatch" in argument_names:
            self.violations.append("monkeypatch fixture")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "pytest":
            for alias in node.names:
                if alias.name == "MonkeyPatch":
                    self.monkeypatch_type_names.add(alias.asname or alias.name)
                    self.violations.append("pytest.MonkeyPatch")
        if node.module == "unittest.mock":
            for alias in node.names:
                if alias.name == "patch":
                    self.patch_names.add(alias.asname or alias.name)
                    self.violations.append("unittest.mock.patch")
        if node.module == "unittest":
            for alias in node.names:
                if alias.name == "mock":
                    self.unittest_mock_module_names.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        attribute_path = _attribute_path(node)
        if _matches_attribute_path(
            attribute_path,
            module_names=self.pytest_module_names,
            attribute_name="MonkeyPatch",
        ):
            self.violations.append("pytest.MonkeyPatch")
        if _matches_attribute_path(
            attribute_path,
            module_names=self.unittest_mock_module_names,
            attribute_name="patch",
        ):
            self.violations.append("unittest.mock.patch")
        if any(
            attribute_path == f"{module_name}.mock.patch"
            for module_name in self.unittest_module_names
        ):
            self.violations.append("unittest.mock.patch")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.monkeypatch_type_names:
            self.violations.append("pytest.MonkeyPatch")
        if node.id in self.patch_names:
            self.violations.append("unittest.mock.patch")
        self.generic_visit(node)


def _attribute_path(node: ast.Attribute) -> str:
    parts = [node.attr]
    current: ast.expr = node.value
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _matches_attribute_path(
    attribute_path: str,
    *,
    module_names: set[str],
    attribute_name: str,
) -> bool:
    return any(attribute_path == f"{module_name}.{attribute_name}" for module_name in module_names)


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
            if path.exists():
                _require_thin_adapter(
                    root,
                    path,
                    f".agent/skills/{name}/SKILL.md",
                    failures,
                    check,
                    max_nonempty_lines=12,
                )
    return failures


def _audit_command_parity(root: Path) -> list[str]:
    check = "command-parity"
    failures: list[str] = []
    canonical = {path.stem for path in (root / ".agent/commands").glob("*.md") if path.is_file()}
    for name in canonical:
        adapters = [
            (root / ".agents/skills" / f"jc-{name}" / "SKILL.md", 12),
            (root / ".claude/commands" / f"jc-{name}.md", 10),
            (root / ".cursor/commands" / f"jc-{name}.md", 10),
            (root / ".gemini/commands" / f"jc-{name}.toml", 8),
        ]
        for path, max_nonempty_lines in adapters:
            require(
                failures,
                check,
                path.exists(),
                f"missing command adapter {path.relative_to(root)}",
            )
            if path.exists():
                _require_thin_adapter(
                    root,
                    path,
                    f".agent/commands/{name}.md",
                    failures,
                    check,
                    max_nonempty_lines=max_nonempty_lines,
                )
    return failures


def _audit_rule_parity(root: Path) -> list[str]:
    check = "rule-parity"
    failures: list[str] = []
    canonical = {path.stem for path in (root / ".agent/rules").glob("*.md") if path.is_file()}
    for name in canonical:
        adapters = [
            (root / ".claude/rules" / f"{name}.md", 6),
            (root / ".cursor/rules" / f"{name}.mdc", 8),
            (root / ".github/instructions" / f"{name}.instructions.md", 6),
        ]
        for path, max_nonempty_lines in adapters:
            require(
                failures,
                check,
                path.exists(),
                f"missing rule adapter {path.relative_to(root)}",
            )
            if path.exists():
                _require_thin_adapter(
                    root,
                    path,
                    f".agent/rules/{name}.md",
                    failures,
                    check,
                    max_nonempty_lines=max_nonempty_lines,
                )
    return failures


def _audit_reviewer_parity(root: Path) -> list[str]:
    check = "reviewer-parity"
    failures: list[str] = []
    canonical = {
        path.stem for path in (root / ".agent/sub-agents/templates").glob("*.md") if path.is_file()
    }
    for name in canonical:
        adapters = [
            (root / ".claude/agents" / f"{name}.md", 24),
            (root / ".cursor/agents" / f"{name}.md", 16),
            (root / ".gemini/agents" / f"{name}.md", 16),
            (root / ".github/agents" / f"{name}.agent.md", 16),
            (root / ".codex/agents" / f"{name}.toml", 8),
        ]
        for path, max_nonempty_lines in adapters:
            require(
                failures,
                check,
                path.exists(),
                f"missing reviewer adapter {path.relative_to(root)}",
            )
            if path.exists():
                _require_thin_adapter(
                    root,
                    path,
                    f".agent/sub-agents/templates/{name}.md",
                    failures,
                    check,
                    max_nonempty_lines=max_nonempty_lines,
                )
    return failures


def _require_thin_adapter(
    root: Path,
    path: Path,
    canonical_target: str,
    failures: list[str],
    check: str,
    *,
    max_nonempty_lines: int,
) -> None:
    text = read_text(path, failures, check)
    if text is None:
        return
    nonempty_lines = [line for line in text.splitlines() if line.strip()]
    require(
        failures,
        check,
        canonical_target in text or f"@{canonical_target}" in text,
        f"{path.relative_to(root)} must stay a thin pointer to {canonical_target}",
    )
    require(
        failures,
        check,
        len(nonempty_lines) <= max_nonempty_lines,
        f"{path.relative_to(root)} must stay thin rather than copying canonical content",
    )


def _parse_support_matrix(text: str) -> dict[str, dict[str, str]] | None:
    rows = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 3:
        return None
    header = [cell.strip() for cell in rows[0].strip("|").split("|")]
    if not header or header[0] != "Surface":
        return None
    parsed_rows: dict[str, dict[str, str]] = {}
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(header):
            return None
        record = dict(zip(header, cells, strict=True))
        surface = record.pop("Surface")
        parsed_rows[surface] = record
    return parsed_rows


DEFAULT_AUDIT_CHECKS: tuple[AuditFunction, ...] = (
    audit_required_paths,
    audit_entry_surfaces,
    audit_identity,
    audit_gate_scripts,
    audit_packaging_contract,
    audit_typing_contract,
    audit_commit_workflow,
    audit_dependency_hygiene,
    audit_hook_contract,
    audit_repo_local_command_surface,
    audit_python_test_practice,
    audit_adapter_parity,
)


def run_audits(
    root: Path = REPO_ROOT,
    checks: Sequence[AuditFunction] = DEFAULT_AUDIT_CHECKS,
) -> list[str]:
    failures: list[str] = []
    for check in checks:
        failures.extend(check(root))
    return failures


def main(
    root: Path = REPO_ROOT,
    *,
    stdout: TextIO = sys.stdout,
) -> None:
    failures = run_audits(root)
    if failures:
        for failure in failures:
            print(failure, file=stdout)
        raise SystemExit(1)
    print("repo audit passed", file=stdout)


if __name__ == "__main__":
    main()
