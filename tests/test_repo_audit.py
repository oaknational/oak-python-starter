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
markdownlint = "markdownlint"
markdownlint-fix = "markdownlint_fix"
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
fix = ["format-fix", "lint-fix", "format-fix", "markdownlint-fix", "import-linter"]
check = [
  "format-fix",
  "lint-fix",
  "format-fix",
  "markdownlint-fix",
  "import-linter",
  "format",
  "typecheck",
  "lint",
  "markdownlint",
  "codespell",
  "dependency-hygiene",
  "pip-audit",
  "repo-audit",
  "build",
  "test",
  "coverage",
]
check-ci = [
  "format",
  "typecheck",
  "lint",
  "markdownlint",
  "codespell",
  "import-linter",
  "dependency-hygiene",
  "pip-audit",
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
  "markdownlint",
  "markdownlint-fix",
  "typecheck",
  "repo-audit",
  "test",
  "coverage",
  "fix",
  "check",
  "check-ci",
]

[secret_scanning]
gitleaks_version = "v8.30.1"
""".strip()

GITLEAKS_VERSION = "v8.30.1"

CHECK_CI_SEQUENCE = (
    "format -> typecheck -> lint -> markdownlint -> codespell -> import-linter -> "
    "dependency-hygiene -> pip-audit -> repo-audit -> build -> test -> coverage"
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


def _gitleaks_pre_commit_config(rev: str = GITLEAKS_VERSION) -> str:
    return f"""
repos:
  - repo: local
    hooks:
      - id: quality-gates
        entry: uv run python -m oaknational.python_repo_template.devtools check-ci
        language: system
  - repo: https://github.com/gitleaks/gitleaks
    rev: {rev}
    hooks:
      - id: gitleaks
"""


def _gitleaks_ci_workflow(version: str = GITLEAKS_VERSION) -> str:
    # Mirror the real workflow: the archive name is derived from the version, so
    # a mismatched version leaves no copy of the pinned version anywhere in the
    # run block and the lockstep check fires honestly.
    archive = f"gitleaks_{version.lstrip('v')}_linux_x64.tar.gz"
    return f"""
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - run: |
          GITLEAKS_VERSION={version}
          curl -sSLo gitleaks.tar.gz \\
            https://github.com/gitleaks/gitleaks/releases/download/{version}/{archive}
          gitleaks dir .
"""


def _write_valid_secret_scanning(root: Path) -> None:
    _write_repo_audit_contract(root)
    _write(root / ".gitleaks.toml", "[extend]\nuseDefault = true")
    _write(root / ".pre-commit-config.yaml", _gitleaks_pre_commit_config())
    _write(root / ".github" / "workflows" / "ci.yml", _gitleaks_ci_workflow())
    _write(
        root / "README.md",
        "Secret scanning runs gitleaks; install via github.com/gitleaks/gitleaks#installing.",
    )
    _write(
        root / "docs" / "dev-tooling.md", "Secret scanning: gitleaks scans the tree for secrets."
    )


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
It stays blocking in the aggregate gates. Vulnerability scanning is pip-audit.
""",
    )
    _write(
        tmp_path / "docs" / "dev-tooling.md",
        """
deptry
uv run deptry .
Dependency hygiene is distinct from vulnerability scanning, which is pip-audit.
""",
    )
    _write(
        tmp_path / ".agent" / "commands" / "gates.md",
        """
Dependency hygiene runs with uv run deptry .
Vulnerability scanning runs with pip-audit.
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
    assert "README must document the pip-audit dependency-vulnerability scan" in joined
    assert "docs/dev-tooling.md must document the pip-audit dependency-vulnerability scan" in joined
    assert ".agent/commands/gates.md must document the dependency-hygiene gate" in joined
    assert (
        ".agent/commands/gates.md must document the pip-audit dependency-vulnerability scan"
        in joined
    )
    assert "must document the exact check-ci gate sequence" in joined


@pytest.mark.parametrize(
    "audit_function",
    [
        subject.audit_typing_contract,
        subject.audit_commit_workflow,
        subject.audit_distribution_metadata,
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


def test_audit_distribution_metadata_requires_licence_and_metadata(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"
license = "MIT"
license-files = ["LICENCE"]
authors = [{ name = "Oak National Academy" }]
classifiers = [
  "Programming Language :: Python :: 3.14",
  "Typing :: Typed",
]

[project.urls]
Repository = "https://github.com/oaknational/oak-python-starter"
""",
    )
    _write(tmp_path / "LICENCE", "MIT License\n\nCopyright (c) 2026 Oak National Academy")
    _write(tmp_path / "SECURITY.md", "# Security Policy\n\nReport a vulnerability responsibly.")

    assert subject.audit_distribution_metadata(tmp_path) == []

    _write(
        tmp_path / "pyproject.toml",
        """
[project]
name = "oaknational-python-repo-template"
""",
    )

    failures = subject.audit_distribution_metadata(tmp_path)
    joined = "\n".join(failures)

    assert 'must declare license = "MIT"' in joined
    assert "must list LICENCE in license-files" in joined
    assert "must declare at least one author" in joined
    assert "must include the Python 3.14 classifier" in joined
    assert "must include 'Typing :: Typed'" in joined
    assert "must declare a Repository URL" in joined


def test_audit_ci_workflow_accepts_bare_and_quoted_on_keys(tmp_path: Path) -> None:
    workflow_path = tmp_path / ".github" / "workflows" / "ci.yml"

    # Bare `on:` — PyYAML parses the key as the boolean True (the fallback branch).
    _write(
        workflow_path,
        """
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --locked
      - run: uv run python -m oaknational.python_repo_template.devtools check-ci
""",
    )

    assert subject.audit_ci_workflow(tmp_path) == []

    # Quoted "on": — survives as the string key, exercising the other branch.
    _write(
        workflow_path,
        """
name: CI
"on":
  push:
    branches: [main]
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: uv run python -m oaknational.python_repo_template.devtools check-ci
""",
    )

    assert subject.audit_ci_workflow(tmp_path) == []


def test_audit_ci_workflow_reports_missing_triggers_independently(tmp_path: Path) -> None:
    workflow_path = tmp_path / ".github" / "workflows" / "ci.yml"

    # Wrong triggers, but the gate command is present: only the trigger checks fire.
    _write(
        workflow_path,
        """
name: CI
on:
  workflow_dispatch:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: uv run python -m oaknational.python_repo_template.devtools check-ci
""",
    )

    joined = "\n".join(subject.audit_ci_workflow(tmp_path))

    assert "must trigger on push" in joined
    assert "must trigger on pull_request" in joined
    assert "must run the CI gate sequence" not in joined


def test_audit_ci_workflow_reports_missing_gate_command_independently(tmp_path: Path) -> None:
    workflow_path = tmp_path / ".github" / "workflows" / "ci.yml"

    # Correct triggers, but no gate command: only the command check fires.
    _write(
        workflow_path,
        """
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: echo "no gates here"
""",
    )

    joined = "\n".join(subject.audit_ci_workflow(tmp_path))

    assert "must run the CI gate sequence" in joined
    assert "must trigger on push" not in joined
    assert "must trigger on pull_request" not in joined


_VALID_BUMP_MAP = 'bump_map = { "^feat" = "MINOR", "^fix" = "MINOR", "^.+" = "PATCH" }'


def _release_workflow_yaml(
    *, triggers: str = "both", with_cz_bump: bool = True, with_increment_tool: bool = True
) -> str:
    on_block = {
        "both": "on:\n  push:\n    branches: [main]\n  workflow_dispatch:\n",
        "push-only": "on:\n  push:\n    branches: [main]\n",
        "dispatch-only": "on:\n  workflow_dispatch:\n",
    }[triggers]
    steps = ""
    if with_increment_tool:
        steps += (
            "      - run: git log --pretty=format:'%B%x00' "
            "| uv run python tools/release_increment.py\n"
        )
    steps += (
        "      - run: uv run cz bump --increment PATCH --files-only --yes\n"
        if with_cz_bump
        else "      - run: uv build\n"
    )
    return (
        "name: Release\n"
        + on_block
        + "jobs:\n  release:\n    runs-on: ubuntu-latest\n    steps:\n"
        + steps
    )


def _commitizen_pyproject(bump_map_line: str) -> str:
    return (
        "[project]\n"
        'name = "oaknational-python-repo-template"\n'
        'version = "0.1.0"\n\n'
        "[tool.commitizen]\n"
        'name = "cz_conventional_commits"\n'
        'version_provider = "uv"\n' + (bump_map_line + "\n" if bump_map_line else "")
    )


def _write_release_world(
    root: Path, *, workflow: str | None = None, bump_map_line: str = _VALID_BUMP_MAP
) -> None:
    _write(root / ".github" / "workflows" / "release.yml", workflow or _release_workflow_yaml())
    _write(root / "pyproject.toml", _commitizen_pyproject(bump_map_line))


def test_audit_release_workflow_accepts_a_valid_workflow_and_bump_map(tmp_path: Path) -> None:
    _write_release_world(tmp_path)

    assert subject.audit_release_workflow(tmp_path) == []


def test_audit_release_workflow_reports_missing_release_yml(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", _commitizen_pyproject(_VALID_BUMP_MAP))

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "could not read" in joined and ".github/workflows/release.yml" in joined


def test_audit_release_workflow_rejects_a_non_mapping_workflow(tmp_path: Path) -> None:
    _write_release_world(tmp_path, workflow="- invalid")

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert ".github/workflows/release.yml must define a top-level mapping" in joined


def test_audit_release_workflow_requires_a_push_trigger(tmp_path: Path) -> None:
    _write_release_world(tmp_path, workflow=_release_workflow_yaml(triggers="dispatch-only"))

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must trigger on push to main" in joined
    assert "must offer workflow_dispatch" not in joined


def test_audit_release_workflow_requires_workflow_dispatch_for_manual_major(tmp_path: Path) -> None:
    _write_release_world(tmp_path, workflow=_release_workflow_yaml(triggers="push-only"))

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must offer workflow_dispatch for manual major releases" in joined
    assert "must trigger on push to main" not in joined


def test_audit_release_workflow_requires_a_cz_bump_step(tmp_path: Path) -> None:
    _write_release_world(tmp_path, workflow=_release_workflow_yaml(with_cz_bump=False))

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must run `cz bump`" in joined


def test_audit_release_workflow_requires_the_increment_tool(tmp_path: Path) -> None:
    _write_release_world(tmp_path, workflow=_release_workflow_yaml(with_increment_tool=False))

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must compute the increment via tools/release_increment.py" in joined


def test_audit_release_workflow_requires_feat_and_fix_to_be_minor(tmp_path: Path) -> None:
    _write_release_world(
        tmp_path,
        bump_map_line='bump_map = { "^feat" = "PATCH", "^fix" = "PATCH", "^.+" = "PATCH" }',
    )

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must map feat and fix to MINOR" in joined


def test_audit_release_workflow_requires_a_patch_catch_all(tmp_path: Path) -> None:
    _write_release_world(
        tmp_path,
        bump_map_line='bump_map = { "^feat" = "MINOR", "^fix" = "MINOR" }',
    )

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must map other commit types to PATCH" in joined


def test_audit_release_workflow_rejects_auto_major(tmp_path: Path) -> None:
    _write_release_world(
        tmp_path,
        bump_map_line=(
            'bump_map = { "^.+!$" = "MAJOR", "^feat" = "MINOR", "^fix" = "MINOR", "^.+" = "PATCH" }'
        ),
    )

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must not auto-bump MAJOR" in joined


def test_audit_release_workflow_requires_a_bump_map(tmp_path: Path) -> None:
    _write_release_world(tmp_path, bump_map_line="")

    joined = "\n".join(subject.audit_release_workflow(tmp_path))

    assert "must map feat and fix to MINOR" in joined


def test_audit_secret_scanning_accepts_pinned_lockstep_surfaces(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)

    assert subject.audit_secret_scanning(tmp_path) == []


def test_audit_secret_scanning_requires_the_gitleaks_config(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    (tmp_path / ".gitleaks.toml").unlink()

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert ".gitleaks.toml must exist" in joined


def test_audit_secret_scanning_requires_extending_the_default_ruleset(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / ".gitleaks.toml", '[allowlist]\ndescription = "local only"')

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must extend the default ruleset" in joined


def test_audit_secret_scanning_requires_the_pre_commit_rev_to_match(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / ".pre-commit-config.yaml", _gitleaks_pre_commit_config(rev="v8.0.0"))

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must pin the gitleaks mirror rev" in joined


def test_audit_secret_scanning_requires_the_pre_commit_mirror_to_exist(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(
        tmp_path / ".pre-commit-config.yaml",
        """
repos:
  - repo: local
    hooks:
      - id: quality-gates
        entry: uv run python -m oaknational.python_repo_template.devtools check-ci
        language: system
""",
    )

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must include the gitleaks mirror repo" in joined


def test_audit_secret_scanning_requires_the_ci_version_to_match(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / ".github" / "workflows" / "ci.yml", _gitleaks_ci_workflow(version="v8.0.0"))

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must run gitleaks pinned to" in joined


def test_audit_secret_scanning_requires_readme_documentation(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / "README.md", "No secret-scanning mention here.")

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "README must document the gitleaks secret-scanning gate" in joined
    assert "docs/dev-tooling.md must document" not in joined


def test_audit_secret_scanning_requires_the_official_install_link(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / "README.md", "Secret scanning runs gitleaks as a pinned pre-commit hook.")

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must link to the official gitleaks install instructions" in joined


def test_audit_secret_scanning_requires_dev_tooling_documentation(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / "docs" / "dev-tooling.md", "No mention here.")

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "docs/dev-tooling.md must document the gitleaks secret-scanning gate" in joined
    assert "README must document" not in joined


def test_audit_secret_scanning_requires_a_pinned_contract_version(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(tmp_path / "tools" / "repo_audit_contract.toml", "legacy_public_commands = []")

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must pin [secret_scanning].gitleaks_version" in joined


def test_audit_secret_scanning_rejects_a_version_without_the_tag_prefix(tmp_path: Path) -> None:
    _write_valid_secret_scanning(tmp_path)
    _write(
        tmp_path / "tools" / "repo_audit_contract.toml",
        '[secret_scanning]\ngitleaks_version = "8.30.1"',
    )

    joined = "\n".join(subject.audit_secret_scanning(tmp_path))

    assert "must pin [secret_scanning].gitleaks_version to a gitleaks tag" in joined


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
        tmp_path / ".agents" / "skills" / "oak-example" / "SKILL.md",
        "Read and follow `.agent/commands/example.md`.",
    )
    _write(
        tmp_path / ".claude" / "commands" / "oak-example.md",
        "Read and follow `.agent/commands/example.md`.",
    )
    _write(
        tmp_path / ".cursor" / "commands" / "oak-example.md",
        "Read and follow @.agent/commands/example.md",
    )
    _write(
        tmp_path / ".gemini" / "commands" / "oak-example.toml",
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
        tmp_path / ".cursor" / "commands" / "oak-example.md",
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


_PINNED_CI_WORKFLOW = """
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e # v6
      - run: uv run python -m oaknational.python_repo_template.devtools check-ci
"""

_DEPENDABOT_CONFIG = """
version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
"""


def _write_supply_chain_world(
    root: Path,
    *,
    ci_workflow: str = _PINNED_CI_WORKFLOW,
    dependabot: str | None = _DEPENDABOT_CONFIG,
) -> None:
    _write(root / ".github" / "workflows" / "ci.yml", ci_workflow)
    if dependabot is not None:
        _write(root / ".github" / "dependabot.yml", dependabot)


def test_audit_supply_chain_accepts_sha_pinned_actions_and_dependabot(tmp_path: Path) -> None:
    _write_supply_chain_world(tmp_path)

    assert subject.audit_supply_chain(tmp_path) == []


def test_audit_supply_chain_rejects_a_tag_pinned_action(tmp_path: Path) -> None:
    _write_supply_chain_world(
        tmp_path,
        ci_workflow="""
name: CI
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""",
    )

    joined = "\n".join(subject.audit_supply_chain(tmp_path))

    assert "actions/checkout@v4" in joined
    assert "must be pinned to a commit SHA" in joined


def test_audit_supply_chain_requires_a_dependabot_config(tmp_path: Path) -> None:
    _write_supply_chain_world(tmp_path, dependabot=None)

    joined = "\n".join(subject.audit_supply_chain(tmp_path))

    assert ".github/dependabot.yml" in joined
    assert "must exist" in joined


def test_audit_supply_chain_requires_dependabot_version_2(tmp_path: Path) -> None:
    _write_supply_chain_world(
        tmp_path,
        dependabot="""
version: 1
updates:
  - package-ecosystem: "uv"
    directory: "/"
  - package-ecosystem: "github-actions"
    directory: "/"
""",
    )

    joined = "\n".join(subject.audit_supply_chain(tmp_path))

    assert "version: 2" in joined


def test_audit_supply_chain_rejects_a_tag_pinned_reusable_workflow(tmp_path: Path) -> None:
    # A job-level `uses:` (a reusable-workflow call) must be pinned too, not just
    # step-level action references.
    _write_supply_chain_world(
        tmp_path,
        ci_workflow="""
name: CI
on: [push]
jobs:
  call:
    uses: some-org/repo/.github/workflows/reusable.yml@v1
""",
    )

    joined = "\n".join(subject.audit_supply_chain(tmp_path))

    assert "reusable.yml@v1" in joined
    assert "must be pinned" in joined


def test_audit_supply_chain_accepts_a_docker_digest_and_local_action(tmp_path: Path) -> None:
    # A `docker://` ref pinned to a sha256 digest is genuinely pinned, and a
    # local composite action (`./...`, no `@`) is first-party and exempt.
    digest = "sha256:" + "a" * 64
    _write_supply_chain_world(
        tmp_path,
        ci_workflow=f"""
name: CI
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/local
      - uses: docker://ghcr.io/owner/image@{digest}
""",
    )

    assert subject.audit_supply_chain(tmp_path) == []


def test_audit_supply_chain_scans_yaml_extension_workflows(tmp_path: Path) -> None:
    # GitHub Actions accepts both .yml and .yaml; a tag pin in a .yaml workflow
    # must still be caught.
    _write_supply_chain_world(tmp_path)
    _write(
        tmp_path / ".github" / "workflows" / "extra.yaml",
        """
name: Extra
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""",
    )

    joined = "\n".join(subject.audit_supply_chain(tmp_path))

    assert "extra.yaml" in joined
    assert "actions/checkout@v4" in joined


def test_audit_supply_chain_requires_both_pinned_ecosystems(tmp_path: Path) -> None:
    _write_supply_chain_world(
        tmp_path,
        dependabot="""
version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
""",
    )

    joined = "\n".join(subject.audit_supply_chain(tmp_path))

    assert "github-actions" in joined


def _coverage_pyproject(*, fail_under: float = 85, omit: list[str] | None = None) -> str:
    if omit is None:
        omit = ["src/oaknational/python_repo_template/devtools.py"]
    omit_literal = "[" + ", ".join(f'"{entry}"' for entry in omit) + "]"
    return (
        "[project]\n"
        'name = "oaknational-python-repo-template"\n\n'
        "[tool.coverage.run]\n"
        'source = ["oaknational.python_repo_template"]\n'
        f"omit = {omit_literal}\n\n"
        "[tool.coverage.report]\n"
        f"fail_under = {fail_under}\n"
    )


def test_audit_coverage_contract_accepts_the_pinned_floor_and_omit_list(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", _coverage_pyproject())

    assert subject.audit_coverage_contract(tmp_path) == []


def test_audit_coverage_contract_accepts_a_raised_floor(tmp_path: Path) -> None:
    # The audit pins a floor, not an exact value, so raising the bar is fine.
    _write(tmp_path / "pyproject.toml", _coverage_pyproject(fail_under=92))

    assert subject.audit_coverage_contract(tmp_path) == []


def test_audit_coverage_contract_rejects_a_lowered_fail_under(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", _coverage_pyproject(fail_under=70))

    joined = "\n".join(subject.audit_coverage_contract(tmp_path))

    assert "fail_under" in joined
    assert "85" in joined


def test_audit_coverage_contract_rejects_a_missing_fail_under(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        "[project]\n"
        'name = "oaknational-python-repo-template"\n\n'
        "[tool.coverage.run]\n"
        'source = ["oaknational.python_repo_template"]\n'
        'omit = ["src/oaknational/python_repo_template/devtools.py"]\n',
    )

    joined = "\n".join(subject.audit_coverage_contract(tmp_path))

    assert "fail_under" in joined


def test_audit_coverage_contract_rejects_an_unjustified_omit(tmp_path: Path) -> None:
    # Adding files to the omit-list hides them from the coverage denominator;
    # the gate cannot catch that, so the audit must.
    _write(
        tmp_path / "pyproject.toml",
        _coverage_pyproject(
            omit=[
                "src/oaknational/python_repo_template/devtools.py",
                "src/oaknational/python_repo_template/data/activity_store.py",
            ]
        ),
    )

    joined = "\n".join(subject.audit_coverage_contract(tmp_path))

    assert "omit" in joined
    assert "activity_store.py" in joined


def test_audit_coverage_contract_accepts_an_absent_omit(tmp_path: Path) -> None:
    # No omit at all is the safest case (no files hidden) and must pass.
    _write(
        tmp_path / "pyproject.toml",
        "[project]\n"
        'name = "oaknational-python-repo-template"\n\n'
        "[tool.coverage.run]\n"
        'source = ["oaknational.python_repo_template"]\n\n'
        "[tool.coverage.report]\n"
        "fail_under = 85\n",
    )

    assert subject.audit_coverage_contract(tmp_path) == []


def test_audit_coverage_contract_rejects_a_boolean_fail_under(tmp_path: Path) -> None:
    # TOML `true` parses to a Python bool (a subclass of int); it must not pass
    # the numeric floor.
    _write(
        tmp_path / "pyproject.toml",
        "[project]\n"
        'name = "oaknational-python-repo-template"\n\n'
        "[tool.coverage.run]\n"
        'omit = ["src/oaknational/python_repo_template/devtools.py"]\n\n'
        "[tool.coverage.report]\n"
        "fail_under = true\n",
    )

    joined = "\n".join(subject.audit_coverage_contract(tmp_path))

    assert "fail_under" in joined


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
