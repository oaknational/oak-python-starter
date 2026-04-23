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
