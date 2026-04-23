from __future__ import annotations

from pathlib import Path

import tools.repo_audit as subject


def test_audit_gate_scripts_requires_pythonic_canonical_gate_names(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "oaknational-python-repo-template"

[project.scripts]
clean = "oaknational.python_repo_template.devtools:clean"
build = "oaknational.python_repo_template.devtools:build"
dev = "oaknational.python_repo_template.devtools:dev"
format = "oaknational.python_repo_template.devtools:format_gate"
format-fix = "oaknational.python_repo_template.devtools:format_fix"
lint = "oaknational.python_repo_template.devtools:lint"
lint-fix = "oaknational.python_repo_template.devtools:lint_fix"
typecheck = "oaknational.python_repo_template.devtools:typecheck"
repo-audit = "oaknational.python_repo_template.devtools:repo_audit"
test = "oaknational.python_repo_template.devtools:test"
coverage = "oaknational.python_repo_template.devtools:coverage"
fix = "oaknational.python_repo_template.devtools:fix"
check = "oaknational.python_repo_template.devtools:check"
check-ci = "oaknational.python_repo_template.devtools:check_ci"
""".strip(),
        encoding="utf-8",
    )

    assert subject.audit_gate_scripts(tmp_path) == []

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "oaknational-python-repo-template"

[project.scripts]
clean = "oaknational.python_repo_template.devtools:clean"
build = "oaknational.python_repo_template.devtools:build"
dev = "oaknational.python_repo_template.devtools:dev"
format = "oaknational.python_repo_template.devtools:format_gate"
format-fix = "oaknational.python_repo_template.devtools:format_fix"
format-check = "oaknational.python_repo_template.devtools:format_gate"
lint = "oaknational.python_repo_template.devtools:lint"
lint-fix = "oaknational.python_repo_template.devtools:lint_fix"
typecheck = "oaknational.python_repo_template.devtools:typecheck"
repo-audit = "oaknational.python_repo_template.devtools:repo_audit"
test = "oaknational.python_repo_template.devtools:test"
coverage = "oaknational.python_repo_template.devtools:coverage"
fix = "oaknational.python_repo_template.devtools:fix"
check = "oaknational.python_repo_template.devtools:check"
check-ci = "oaknational.python_repo_template.devtools:check_ci"
""".strip(),
        encoding="utf-8",
    )

    failures = subject.audit_gate_scripts(tmp_path)

    assert "legacy gate script 'format-check'" in "\n".join(failures)


def test_audit_typing_contract_requires_explicit_strict_pyright_scope(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.pyright]
include = ["src", "tests", "tools"]
pythonVersion = "3.14"
typeCheckingMode = "strict"

[tool.hatch.build.targets.wheel.force-include]
"src/oaknational/python_repo_template/py.typed" = "oaknational/python_repo_template/py.typed"
""".strip(),
        encoding="utf-8",
    )

    assert subject.audit_typing_contract(tmp_path) == []

    (tmp_path / "pyproject.toml").write_text(
        """
[tool.pyright]
include = ["src"]
pythonVersion = "3.14"
typeCheckingMode = "basic"
""".strip(),
        encoding="utf-8",
    )

    failures = subject.audit_typing_contract(tmp_path)
    joined = "\n".join(failures)

    assert "cover src, tests, and tools explicitly" in joined
    assert "strict type checking" in joined
    assert "force-include py.typed" in joined


def test_audit_packaging_contract_requires_namespace_preserving_wheel_mapping(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.hatch.build.targets.wheel]
only-include = ["src/oaknational/python_repo_template"]
sources = ["src"]
""".strip(),
        encoding="utf-8",
    )

    assert subject.audit_packaging_contract(tmp_path) == []

    (tmp_path / "pyproject.toml").write_text(
        """
[tool.hatch.build.targets.wheel]
packages = ["src/oaknational/python_repo_template"]
""".strip(),
        encoding="utf-8",
    )

    failures = subject.audit_packaging_contract(tmp_path)
    joined = "\n".join(failures)

    assert "package the Oak namespace directory without collapsing it" in joined
    assert "strip the src/ prefix while preserving the oaknational namespace path" in joined


def test_audit_commit_workflow_requires_commitizen_and_truthful_hooking(
    tmp_path: Path,
) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / ".agent" / "commands").mkdir(parents=True)

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "oaknational-python-repo-template"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9.0.0", "commitizen>=4.10.0"]

[tool.commitizen]
name = "cz_conventional_commits"
version_provider = "uv"
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
default_install_hook_types:
  - pre-commit
  - pre-push
  - commit-msg

repos:
  - repo: local
    hooks:
      - id: commitizen-commit-msg
        entry: uv run cz check --allow-abort --commit-msg-file
        language: system
        stages: [commit-msg]
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        """
uv run pre-commit install
uv run cz commit
uv run cz check --message "feat: add truthful commit-msg enforcement"
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "dev-tooling.md").write_text(
        """
commitizen
uv run cz commit
uv run cz check --message "docs: explain the Commitizen workflow"
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / ".agent" / "commands" / "commit.md").write_text(
        """
uv run cz commit
uv run cz check
""".strip(),
        encoding="utf-8",
    )

    assert subject.audit_commit_workflow(tmp_path) == []

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "oaknational-python-repo-template"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9.0.0"]

[tool.commitizen]
name = "cz_customize"
version_provider = "pep621"
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
repos:
  - repo: local
    hooks:
      - id: quality-gates
        entry: uv run check-ci
        language: system
        stages: [pre-commit, pre-push]
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Oak Python Repo Template", encoding="utf-8")
    (tmp_path / "docs" / "dev-tooling.md").write_text("# Dev Tooling", encoding="utf-8")
    (tmp_path / ".agent" / "commands" / "commit.md").write_text(
        "# Commit Current Work",
        encoding="utf-8",
    )

    failures = subject.audit_commit_workflow(tmp_path)
    joined = "\n".join(failures)

    assert "add commitizen to the dev dependency group" in joined
    assert "configure Commitizen for Conventional Commits" in joined
    assert "configure Commitizen to use the uv version provider" in joined
    assert "install commit-msg hooks by default" in joined
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
