#!/usr/bin/env python3
"""Audit tracked repo state using filesystem and text inspection."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "pyproject.toml",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".agent/directives/AGENT.md",
    ".agent/directives/principles.md",
    ".agent/directives/testing-strategy.md",
    ".agent/practice-index.md",
    ".agent/VISION.md",
    ".agent/plans/README.md",
    ".agent/plans/roadmap.md",
    ".agent/plans/agentic-engineering/README.md",
    ".agent/plans/runtime-infrastructure/README.md",
    ".agent/plans/demo-application/README.md",
    ".agent/reference/cross-platform-agent-surface-matrix.md",
    ".agent/hooks/policy.json",
    "src/python_repo_template/__main__.py",
    "src/python_repo_template/devtools.py",
    "src/python_repo_template/data/activity_store.py",
    "src/python_repo_template/demo/activity_report.py",
    "tools/__init__.py",
    "tools/agent_hooks.py",
    "tools/repo_audit.py",
    "tests/test_agent_hooks.py",
    "tests/test_activity_store.py",
    "tests/test_activity_report.py",
    "tests/test_package_entrypoint.py",
    "data/fixtures/activity_log.csv",
    "data/fixtures/activity_log.metadata.yaml",
    "docs/architecture-decision-records/ADR-0001-cross-platform-practice-surface-contract.md",
]
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".csv",
}
TEXT_FILE_NAMES = {
    ".gitignore",
    ".python-version",
}
IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".import_linter_cache",
    "htmlcov",
}


def _join_parts(*parts: str) -> str:
    return "".join(parts)


LEGACY_TERMS = (
    (_join_parts("trad", "ing"),),
    (_join_parts("trad", "e"),),
    (_join_parts("fin", "ance"),),
    (_join_parts("fin", "ancial"),),
    (_join_parts("sto", "ck"),),
    (_join_parts("sto", "cks"),),
    (_join_parts("sha", "re"),),
    (_join_parts("sha", "res"),),
    (_join_parts("mark", "et"), _join_parts("da", "ta")),
    (_join_parts("ohl", "cv"),),
    (_join_parts("back", "test"),),
    (_join_parts("back", "testing"),),
    (_join_parts("bro", "ker"),),
    (_join_parts("bro", "kerage"),),
    (_join_parts("port", "folio"),),
    (_join_parts("equ", "ity"),),
    (_join_parts("alp", "aca"),),
    (
        _join_parts("trad", "ing"),
        _join_parts("view"),
    ),
    (_join_parts("pi", "ne"),),
    (_join_parts("nv", "da"),),
)
DENY_PATTERN = re.compile(
    "|".join(
        (
            r"\b" + re.escape(parts[0]) + r"\b"
            if len(parts) == 1
            else r"\b" + r"\s+".join(re.escape(part) for part in parts) + r"\b"
        )
        for parts in LEGACY_TERMS
    ),
    flags=re.IGNORECASE,
)


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
            "# Python Repo Template" in readme and "activity-report" in readme,
            "README must describe the template identity and demo CLI",
        )
    if pyproject is not None:
        require(
            failures,
            check,
            'name = "python-repo-template"' in pyproject,
            "pyproject must expose the template package name",
        )
        require(
            failures,
            check,
            'activity-report = "python_repo_template.demo.activity_report:main"' in pyproject,
            "pyproject must expose the activity-report script",
        )
    if agent is not None:
        require(
            failures,
            check,
            "runtime infrastructure" in agent and "demo application" in agent,
            "AGENT.md must describe the three repo strands",
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


def audit_legacy_terms(root: Path) -> list[str]:
    check = "legacy-terms"
    failures: list[str] = []
    for path in iter_text_files(root):
        text = read_text(path, failures, check)
        if text is None:
            continue
        match = DENY_PATTERN.search(text)
        require(
            failures,
            check,
            match is None,
            f"{path.relative_to(root)} contains banned term {match.group(0)!r}" if match else "",
        )
    return failures


def iter_text_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_FILE_NAMES:
            paths.append(path)
    return sorted(paths)


def main() -> None:
    failures: list[str] = []
    checks = [
        audit_required_paths,
        audit_entry_surfaces,
        audit_identity,
        audit_adapter_parity,
        audit_legacy_terms,
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
