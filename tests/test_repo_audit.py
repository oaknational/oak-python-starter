from __future__ import annotations

import json
from collections.abc import Callable
from io import StringIO
from pathlib import Path

import pytest

import tools.repo_audit as subject

PUBLISHED_SCRIPTS = {
    "activity-report": "oaknational.python_repo_template.demo.activity_report:main",
}

GATE_CONTRACT = """
[repo_local_commands]
clean = "clean"
build = "build"
dev = "dev"
lint = "lint"
lint-fix = "lint_fix"
format = "format_gate"
format-fix = "format_fix"
typecheck = "typecheck"
repo-audit = "repo_audit"
test = "test"
coverage = "coverage"
fix = "fix"
check = "check"
check-ci = "check_ci"

[gate_sequences]
fix = ["format-fix", "lint-fix", "format-fix", "import-linter"]
check = [
  "format-fix",
  "lint-fix",
  "format-fix",
  "import-linter",
  "format",
  "typecheck",
  "lint",
  "dependency-hygiene",
  "repo-audit",
  "build",
  "test",
  "coverage",
]
check-ci = [
  "format",
  "typecheck",
  "lint",
  "import-linter",
  "dependency-hygiene",
  "repo-audit",
  "build",
  "test",
  "coverage",
]
""".strip()

REPO_AUDIT_CONTRACT = """
legacy_public_commands = ["format-check"]

[published_entry_points]
activity-report = "oaknational.python_repo_template.demo.activity_report:main"

[documentation_commands]
".agent/directives/AGENT.md" = [
  "clean",
  "build",
  "dev",
  "check",
  "check-ci",
  "fix",
  "test",
  "coverage",
]
".agent/skills/start-right-quick/SKILL.md" = ["check", "check-ci"]
".agent/commands/gates.md" = ["clean", "build", "dev", "check", "check-ci"]
"README.md" = ["clean", "build", "dev", "check", "check-ci", "fix", "test", "coverage"]
"docs/dev-tooling.md" = [
  "clean",
  "build",
  "dev",
  "format",
  "format-fix",
  "lint",
  "lint-fix",
  "typecheck",
  "repo-audit",
  "test",
  "coverage",
  "fix",
  "check",
  "check-ci",
]
""".strip()

CHECK_CI_SEQUENCE = (
    "format -> typecheck -> lint -> import-linter -> dependency-hygiene -> "
    "repo-audit -> build -> test -> coverage"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{text.strip()}\n", encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")


def _write_gate_contract(root: Path) -> None:
    _write(
        root / "src" / "oaknational" / "python_repo_template" / "gate_contract.toml",
        GATE_CONTRACT,
    )


def _write_repo_audit_contract(root: Path) -> None:
    _write(root / "tools" / "repo_audit_contract.toml", REPO_AUDIT_CONTRACT)


def _gate_scripts_toml(
    *,
    extra_scripts: dict[str, str] | None = None,
    omitted_scripts: set[str] | None = None,
) -> str:
    scripts = dict(PUBLISHED_SCRIPTS)
    if omitted_scripts is not None:
        for name in omitted_scripts:
            scripts.pop(name, None)
    if extra_scripts is not None:
        scripts.update(extra_scripts)

    lines = [
        "[project]",
        'name = "oaknational-python-repo-template"',
        "",
        "[project.scripts]",
    ]
    for name, target in scripts.items():
        lines.append(f'{name} = "{target}"')
    return "\n".join(lines)


def test_audit_gate_scripts_requires_only_the_published_activity_report_surface(
    tmp_path: Path,
) -> None:
    _write_gate_contract(tmp_path)
    _write_repo_audit_contract(tmp_path)
    _write(tmp_path / "pyproject.toml", _gate_scripts_toml())

    assert subject.audit_gate_scripts(tmp_path) == []

    _write(
        tmp_path / "pyproject.toml",
        _gate_scripts_toml(omitted_scripts={"activity-report"}),
    )

    failures = subject.audit_gate_scripts(tmp_path)

    assert "must expose 'activity-report'" in "\n".join(failures)


def test_audit_gate_scripts_rejects_repo_local_devtools_commands(tmp_path: Path) -> None:
    _write_gate_contract(tmp_path)
    _write_repo_audit_contract(tmp_path)
    _write(
        tmp_path / "pyproject.toml",
        _gate_scripts_toml(
            extra_scripts={"check-ci": "oaknational.python_repo_template.devtools:check_ci"}
        ),
    )

    failures = subject.audit_gate_scripts(tmp_path)

    assert "repo-local devtools command 'check-ci'" in "\n".join(failures)


def test_audit_gate_scripts_rejects_legacy_gate_commands(tmp_path: Path) -> None:
    _write_gate_contract(tmp_path)
    _write_repo_audit_contract(tmp_path)
    _write(
        tmp_path / "pyproject.toml",
        _gate_scripts_toml(
            extra_scripts={"format-check": "oaknational.python_repo_template.devtools:format_gate"}
        ),
    )

    failures = subject.audit_gate_scripts(tmp_path)

    assert "repo-local devtools command 'format-check'" in "\n".join(failures)


def test_audit_gate_scripts_rejects_unexpected_public_scripts(tmp_path: Path) -> None:
    _write_gate_contract(tmp_path)
    _write_repo_audit_contract(tmp_path)
    _write(
        tmp_path / "pyproject.toml",
        _gate_scripts_toml(
            extra_scripts={"deptry": "oaknational.python_repo_template.devtools:check_ci"}
        ),
    )

    failures = subject.audit_gate_scripts(tmp_path)

    assert "unexpected public scripts: ['deptry']" in "\n".join(failures)


def test_audit_typing_contract_requires_explicit_strict_pyright_scope(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        """
[tool.pyright]
include = ["src", "tests", "tools"]
pythonVersion = "3.14"
typeCheckingMode = "strict"

[tool.hatch.build.targets.wheel.force-include]
"src/oaknational/python_repo_template/py.typed" = "oaknational/python_repo_template/py.typed"
""",
    )
    _write_json(
        tmp_path / "pyrightconfig.json",
        {
            "pythonVersion": "3.14",
            "typeCheckingMode": "strict",
            "include": ["src", "tests", "tools"],
        },
    )

    assert subject.audit_typing_contract(tmp_path) == []

    _write(
        tmp_path / "pyproject.toml",
        """
[tool.pyright]
include = ["src"]
pythonVersion = "3.14"
typeCheckingMode = "basic"
""",
    )
    _write_json(
        tmp_path / "pyrightconfig.json",
        {
            "pythonVersion": "3.14",
            "typeCheckingMode": "basic",
            "include": ["src", "tests"],
        },
    )

    failures = subject.audit_typing_contract(tmp_path)
    joined = "\n".join(failures)

    assert "cover src, tests, and tools explicitly" in joined
    assert "strict type checking" in joined
    assert "force-include py.typed" in joined
    assert (
        "pyrightconfig.json must configure pyright to cover src, tests, and tools explicitly"
        in joined
    )
    assert "pyrightconfig.json must configure pyright with strict type checking" in joined


def test_audit_packaging_contract_requires_namespace_preserving_wheel_mapping(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "pyproject.toml",
        """
[tool.hatch.build.targets.wheel]
only-include = ["src/oaknational/python_repo_template"]
sources = ["src"]
""",
    )

    assert subject.audit_packaging_contract(tmp_path) == []

    _write(
        tmp_path / "pyproject.toml",
        """
[tool.hatch.build.targets.wheel]
packages = ["src/oaknational/python_repo_template"]
""",
    )

    failures = subject.audit_packaging_contract(tmp_path)
    joined = "\n".join(failures)

    assert "package the Oak namespace directory without collapsing it" in joined
    assert "strip the src/ prefix while preserving the oaknational namespace path" in joined


def test_audit_commit_workflow_requires_commitizen_and_truthful_hooking(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9.0.0", "commitizen>=4.10.0"]

[tool.commitizen]
name = "cz_conventional_commits"
version_provider = "uv"
""",
    )
    _write(
        tmp_path / ".pre-commit-config.yaml",
        """
default_install_hook_types:
  - pre-commit
  - pre-push
  - commit-msg

repos:
  - repo: local
    hooks:
      - id: quality-gates
        entry: uv run python -m oaknational.python_repo_template.devtools check-ci
        language: system
        stages: [pre-commit, pre-push]
        pass_filenames: false
      - id: commitizen-commit-msg
        entry: uv run cz check --allow-abort --commit-msg-file
        language: system
        stages: [commit-msg]
""",
    )
    _write(
        tmp_path / "README.md",
        """
uv run pre-commit install
uv run cz commit
uv run cz check --message "feat: add truthful commit-msg enforcement"
""",
    )
    _write(
        tmp_path / "docs" / "dev-tooling.md",
        """
commitizen
uv run cz commit
uv run cz check --message "docs: explain the Commitizen workflow"
""",
    )
    _write(
        tmp_path / ".agent" / "commands" / "commit.md",
        """
uv run cz commit
uv run cz check
""",
    )

    assert subject.audit_commit_workflow(tmp_path) == []

    _write(tmp_path / ".pre-commit-config.yaml", "- invalid")

    failures = subject.audit_commit_workflow(tmp_path)

    assert ".pre-commit-config.yaml must define a top-level mapping" in "\n".join(failures)

    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9.0.0"]

[tool.commitizen]
name = "cz_customize"
version_provider = "pep621"
""",
    )
    _write(
        tmp_path / ".pre-commit-config.yaml",
        """
repos:
  - repo: local
    hooks:
      - id: quality-gates
        entry: uv run python -m oaknational.python_repo_template.devtools check-ci
        language: system
        stages: [pre-commit, pre-push]
""",
    )
    _write(tmp_path / "README.md", "# Oak Python Repo Template")
    _write(tmp_path / "docs" / "dev-tooling.md", "# Dev Tooling")
    _write(tmp_path / ".agent" / "commands" / "commit.md", "# Commit Current Work")

    failures = subject.audit_commit_workflow(tmp_path)
    joined = "\n".join(failures)

    assert "add commitizen to the dev dependency group" in joined
    assert "configure Commitizen for Conventional Commits" in joined
    assert "configure Commitizen to use the uv version provider" in joined
    assert "install commit-msg hooks by default" in joined
    assert "enforce quality gates with the repo-local check-ci command" in joined
    assert "enforce commit messages with Commitizen at commit-msg" in joined
    assert (
        "README must document hook installation plus Commitizen commit creation and validation"
        in joined
    )
    assert "docs/dev-tooling.md must document the Commitizen workflow" in joined
    assert (
        ".agent/commands/commit.md must direct commit creation and validation through Commitizen"
        in joined
    )


def test_audit_dependency_hygiene_requires_exact_contract_and_docs(
    tmp_path: Path,
) -> None:
    _write_gate_contract(tmp_path)
    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9.0.0", "deptry>=0.25.1"]

[tool.deptry]
known_first_party = ["oaknational"]

[tool.deptry.per_rule_ignores]
DEP002 = ["pyarrow"]
""",
    )
    _write(
        tmp_path / "README.md",
        """
Dependency hygiene runs through uv run deptry .
It stays blocking in the aggregate gates, and it is not vulnerability scanning.
""",
    )
    _write(
        tmp_path / "docs" / "dev-tooling.md",
        """
deptry
uv run deptry .
It is dependency hygiene, not vulnerability scanning.
""",
    )
    _write(
        tmp_path / ".agent" / "commands" / "gates.md",
        """
Dependency hygiene runs with uv run deptry .
""",
    )
    _write(
        tmp_path / ".agent" / "skills" / "start-right-quick" / "SKILL.md",
        f"""
The gate sequence for this repo:

{CHECK_CI_SEQUENCE}
""",
    )

    assert subject.audit_dependency_hygiene(tmp_path) == []

    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9.0.0", "deptry>=0.25.1"]

[tool.deptry]
known_first_party = ["oaknational", "legacy"]
experimental_namespace_package = true

[tool.deptry.per_rule_ignores]
DEP002 = ["pyarrow", "requests"]
DEP003 = ["pandas"]
""",
    )
    _write(
        tmp_path / "README.md",
        """
Dependency hygiene runs through uv run deptry .
""",
    )
    _write(
        tmp_path / "docs" / "dev-tooling.md",
        """
deptry
uv run deptry .
""",
    )
    _write(tmp_path / ".agent" / "commands" / "gates.md", "# Quality Gates")
    _write(
        tmp_path / ".agent" / "skills" / "start-right-quick" / "SKILL.md",
        """
format -> typecheck -> lint -> dependency-hygiene -> repo-audit -> build -> tests -> coverage
""",
    )

    failures = subject.audit_dependency_hygiene(tmp_path)
    joined = "\n".join(failures)

    assert "must keep [tool.deptry] small and explicit" in joined
    assert "must configure deptry to treat the Oak namespace as first party" in joined
    assert "must limit deptry per-rule ignores to the single DEP002 exception" in joined
    assert "must document the single DEP002 ignore for pyarrow" in joined
    assert "README must explain that deptry is not vulnerability scanning" in joined
    assert "docs/dev-tooling.md must explain that deptry is not vulnerability scanning" in joined
    assert ".agent/commands/gates.md must document the dependency-hygiene gate" in joined
    assert "must document the exact check-ci gate sequence" in joined


@pytest.mark.parametrize(
    "audit_function",
    [
        subject.audit_packaging_contract,
        subject.audit_typing_contract,
        subject.audit_commit_workflow,
    ],
)
def test_audit_functions_report_invalid_toml(
    audit_function: Callable[[Path], list[str]],
    tmp_path: Path,
) -> None:
    _write(tmp_path / "pyproject.toml", "[project")
    if audit_function is subject.audit_typing_contract:
        _write_json(
            tmp_path / "pyrightconfig.json",
            {
                "pythonVersion": "3.14",
                "typeCheckingMode": "strict",
                "include": ["src", "tests", "tools"],
            },
        )

    failures = audit_function(tmp_path)

    assert "invalid TOML in" in "\n".join(failures)


def test_audit_python_test_practice_rejects_runtime_patch_helpers(tmp_path: Path) -> None:
    _write(
        tmp_path / "tests" / "test_ok.py",
        """
def test_ok() -> None:
    assert True
""",
    )

    assert subject.audit_python_test_practice(tmp_path) == []

    _write(
        tmp_path / "tests" / "test_bad.py",
        """
import pytest
import pytest as pt
from unittest import mock as unittest_mock
import unittest.mock as mock
from unittest.mock import patch
from unittest.mock import patch as patch_fn
from pytest import MonkeyPatch as MP


def test_bad(monkeypatch: pytest.MonkeyPatch) -> None:
    assert patch is not None
    assert patch_fn is not None
    assert mock.patch is not None
    assert unittest_mock.patch is not None
    helper: MP | None = None
    assert helper is None
    value: pt.MonkeyPatch | None = None
    assert value is None
    assert monkeypatch is not None


async def test_async_bad(monkeypatch) -> None:
    assert monkeypatch is not None
""",
    )

    failures = subject.audit_python_test_practice(tmp_path)
    joined = "\n".join(failures)

    assert "test_bad.py must not use runtime patch helpers" in joined
    assert "monkeypatch fixture" in joined
    assert "pytest.MonkeyPatch" in joined
    assert "unittest.mock.patch" in joined


def test_audit_required_paths_reports_missing_files(tmp_path: Path) -> None:
    failures = subject.audit_required_paths(tmp_path)

    assert "missing required path README.md" in "\n".join(failures)


def test_audit_entry_surfaces_requires_canonical_delegation(tmp_path: Path) -> None:
    for relative_path in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        _write(tmp_path / relative_path, "Read `.agent/directives/AGENT.md` and follow it.")

    assert subject.audit_entry_surfaces(tmp_path) == []

    _write(tmp_path / "GEMINI.md", "Read something else.")

    failures = subject.audit_entry_surfaces(tmp_path)

    assert "GEMINI.md must delegate to .agent/directives/AGENT.md" in "\n".join(failures)


def test_audit_identity_requires_template_contracts(tmp_path: Path) -> None:
    _write(
        tmp_path / "README.md",
        """
# Oak Python Repo Template

activity-report
""",
    )
    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"

[project.scripts]
activity-report = "oaknational.python_repo_template.demo.activity_report:main"
""",
    )
    _write(
        tmp_path / ".agent" / "directives" / "AGENT.md",
        """
runtime infrastructure
demo application
""",
    )
    _write(
        tmp_path / ".agent" / "practice-index.md",
        """
practice-core/practice-verification.md
memory/operational/repo-continuity.md
plans/high-level-plan.md
docs/dev-tooling.md
""",
    )

    assert subject.audit_identity(tmp_path) == []

    _write(tmp_path / "README.md", "# Wrong Repo")

    failures = subject.audit_identity(tmp_path)

    assert "README must describe the template identity and demo CLI" in "\n".join(failures)


def test_audit_hook_contract_requires_canonical_policy_and_gemini_support(tmp_path: Path) -> None:
    _copy_repo_file(".agent/hooks/policy.json", tmp_path)
    _copy_repo_file(".cursor/hooks.json", tmp_path)
    _copy_repo_file(".claude/settings.json", tmp_path)
    _copy_repo_file(".gemini/settings.json", tmp_path)
    _copy_repo_file(".github/hooks/guardrails.json", tmp_path)
    _copy_repo_file(
        ".agent/memory/executive/cross-platform-agent-surface-matrix.md",
        tmp_path,
    )
    _copy_repo_file(
        "docs/architecture-decision-records/ADR-0001-cross-platform-practice-surface-contract.md",
        tmp_path,
    )

    assert subject.audit_hook_contract(tmp_path) == []

    matrix_path = (
        tmp_path / ".agent" / "memory" / "executive" / "cross-platform-agent-surface-matrix.md"
    )
    supported_hooks_row = (
        "| hooks | `.agent/hooks/` | portable | unsupported | portable | portable | "
        "portable | hook runtime |"
    )
    unsupported_gemini_hooks_row = (
        "| hooks | `.agent/hooks/` | portable | unsupported | portable | unsupported | "
        "portable | hook runtime |"
    )
    matrix_path.write_text(
        matrix_path.read_text(encoding="utf-8").replace(
            supported_hooks_row,
            unsupported_gemini_hooks_row,
        ),
        encoding="utf-8",
    )

    failures = subject.audit_hook_contract(tmp_path)

    assert "Gemini hooks as portable" in "\n".join(failures)


@pytest.mark.parametrize(
    "relative_path",
    (
        ".agent/hooks/policy.json",
        ".cursor/hooks.json",
        ".claude/settings.json",
        ".gemini/settings.json",
        ".github/hooks/guardrails.json",
    ),
)
def test_audit_hook_contract_fails_closed_on_non_object_hook_config(
    tmp_path: Path,
    relative_path: str,
) -> None:
    for path in (
        ".agent/hooks/policy.json",
        ".cursor/hooks.json",
        ".claude/settings.json",
        ".gemini/settings.json",
        ".github/hooks/guardrails.json",
    ):
        _copy_repo_file(path, tmp_path)

    _write(tmp_path / relative_path, "[]")

    failures = subject.audit_hook_contract(tmp_path)

    assert f"{relative_path} must define a top-level JSON object" in "\n".join(failures)


def test_audit_repo_local_command_surface_requires_source_checkout_commands(tmp_path: Path) -> None:
    _write_gate_contract(tmp_path)
    _write_repo_audit_contract(tmp_path)
    for relative_path in (
        ".agent/directives/AGENT.md",
        ".agent/skills/start-right-quick/SKILL.md",
        ".agent/commands/gates.md",
        "README.md",
        "docs/dev-tooling.md",
    ):
        _copy_repo_file(relative_path, tmp_path)

    assert subject.audit_repo_local_command_surface(tmp_path) == []

    _write(
        tmp_path / "README.md",
        """
uv run check
""",
    )

    failures = subject.audit_repo_local_command_surface(tmp_path)

    assert "must not document the published-wheel form uv run check" in "\n".join(failures)


def test_audit_repo_local_command_surface_rejects_unknown_documented_commands(
    tmp_path: Path,
) -> None:
    _write_gate_contract(tmp_path)
    _write(
        tmp_path / "tools" / "repo_audit_contract.toml",
        """
legacy_public_commands = ["format-check"]

[published_entry_points]
activity-report = "oaknational.python_repo_template.demo.activity_report:main"

[documentation_commands]
"README.md" = ["check", "ship-it"]
""",
    )
    _write(
        tmp_path / "README.md",
        """
uv run python -m oaknational.python_repo_template.devtools check
uv run python -m oaknational.python_repo_template.devtools ship-it
""",
    )

    failures = subject.audit_repo_local_command_surface(tmp_path)

    assert (
        "README.md must only document repo-local commands defined in "
        "gate_contract.toml; 'ship-it' is unknown"
    ) in "\n".join(failures)


def test_audit_adapter_parity_requires_thin_wrappers(tmp_path: Path) -> None:
    _write(tmp_path / ".agent" / "skills" / "example" / "SKILL.md", "# Example")
    _write(
        tmp_path / ".agents" / "skills" / "example" / "SKILL.md",
        "Read and follow `.agent/skills/example/SKILL.md`.",
    )
    _write(
        tmp_path / ".claude" / "skills" / "example" / "SKILL.md",
        "Read and follow `.agent/skills/example/SKILL.md`.",
    )
    _write(
        tmp_path / ".cursor" / "skills" / "example" / "SKILL.md",
        "Read and follow @.agent/skills/example/SKILL.md",
    )
    _write(
        tmp_path / ".gemini" / "skills" / "example" / "SKILL.md",
        "Read and follow `.agent/skills/example/SKILL.md`.",
    )
    _write(
        tmp_path / ".github" / "skills" / "example" / "SKILL.md",
        "Read and follow `.agent/skills/example/SKILL.md`.",
    )

    _write(tmp_path / ".agent" / "commands" / "example.md", "# Example")
    _write(
        tmp_path / ".agents" / "skills" / "jc-example" / "SKILL.md",
        "Read and follow `.agent/commands/example.md`.",
    )
    _write(
        tmp_path / ".claude" / "commands" / "jc-example.md",
        "Read and follow `.agent/commands/example.md`.",
    )
    _write(
        tmp_path / ".cursor" / "commands" / "jc-example.md",
        "Read and follow @.agent/commands/example.md",
    )
    _write(
        tmp_path / ".gemini" / "commands" / "jc-example.toml",
        'prompt = "Read and follow `.agent/commands/example.md`."',
    )

    _write(tmp_path / ".agent" / "rules" / "example.md", "# Example")
    _write(
        tmp_path / ".claude" / "rules" / "example.md",
        "Read and follow `.agent/rules/example.md`.",
    )
    _write(
        tmp_path / ".cursor" / "rules" / "example.mdc",
        "Read and follow `.agent/rules/example.md`.",
    )
    _write(
        tmp_path / ".github" / "instructions" / "example.instructions.md",
        "Read and follow `.agent/rules/example.md`.",
    )

    _write(tmp_path / ".agent" / "sub-agents" / "templates" / "example.md", "# Example")
    _write(
        tmp_path / ".claude" / "agents" / "example.md",
        "Read and follow `.agent/sub-agents/templates/example.md`.",
    )
    _write(
        tmp_path / ".cursor" / "agents" / "example.md",
        "Read and follow `.agent/sub-agents/templates/example.md`.",
    )
    _write(
        tmp_path / ".gemini" / "agents" / "example.md",
        "Read and follow `.agent/sub-agents/templates/example.md`.",
    )
    _write(
        tmp_path / ".github" / "agents" / "example.agent.md",
        "Read and follow `.agent/sub-agents/templates/example.md`.",
    )
    _write(
        tmp_path / ".codex" / "agents" / "example.toml",
        'prompt = "Read and follow `.agent/sub-agents/templates/example.md`."',
    )

    assert subject.audit_adapter_parity(tmp_path) == []

    _write(
        tmp_path / ".cursor" / "commands" / "jc-example.md",
        """
Read and follow @.agent/commands/example.md
line 1
line 2
line 3
line 4
line 5
line 6
line 7
line 8
line 9
line 10
""",
    )

    failures = subject.audit_adapter_parity(tmp_path)

    assert "must stay thin rather than copying canonical content" in "\n".join(failures)


def test_main_reports_success_and_failure() -> None:
    stdout = StringIO()
    subject.main(root=subject.REPO_ROOT, stdout=stdout)
    assert stdout.getvalue().strip() == "repo audit passed"

    failure_stdout = StringIO()
    with pytest.raises(SystemExit) as exc_info:
        subject.main(root=Path.cwd() / "does-not-exist", stdout=failure_stdout)

    assert exc_info.value.code == 1
    assert "required-paths:" in failure_stdout.getvalue()


def _copy_repo_file(relative_path: str, destination_root: Path) -> None:
    source = subject.REPO_ROOT / relative_path
    destination = destination_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
