"""Developer tooling entrypoints for ``uv run`` quality checks."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON_TARGETS = ("src", "tests", "tools")
CLEAN_DIRECTORIES = (
    "build",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".import_linter_cache",
    "htmlcov",
)
IGNORED_CLEAN_PARTS = {".git", ".venv"}


def _resolve_executable(command: str) -> str:
    candidate = Path(sys.executable).parent / command
    if candidate.exists():
        return str(candidate)
    return command


def _is_python_script(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(2) == b"#!"
    except OSError:
        return False


def _run(args: Sequence[str]) -> int:
    if not args:
        raise ValueError("Expected at least one argument to run a command.")
    command = _resolve_executable(str(args[0]))
    resolved_path = Path(command)
    rest = [str(arg) for arg in args[1:]]
    if resolved_path.exists() and _is_python_script(resolved_path):
        resolved_args = [sys.executable, str(resolved_path), *rest]
    else:
        resolved_args = [command, *rest]
    result = subprocess.run(resolved_args, check=False)
    return result.returncode


def _run_or_exit(args: Sequence[str]) -> None:
    raise SystemExit(_run(args))


def _run_named_step(name: str, runner: Sequence[str] | Callable[[], int]) -> None:
    if callable(runner):
        print(f"==> {name}")
    else:
        print(f"==> {name}: {' '.join(runner)}")
    start = time.perf_counter()
    code = runner() if callable(runner) else _run(runner)
    duration = time.perf_counter() - start
    if code != 0:
        print(f"FAILED: {name} ({duration:.2f}s)")
        raise SystemExit(code)
    print(f"PASS: {name} ({duration:.2f}s)")


def _run_gate_sequence(steps: Sequence[tuple[str, Sequence[str] | Callable[[], int]]]) -> None:
    for name, runner in steps:
        _run_named_step(name, runner)
    print("all checks passed")
    raise SystemExit(0)


def _run_build_probe() -> int:
    with tempfile.TemporaryDirectory(prefix="oaknational-python-repo-template-build-") as out_dir:
        return _run(["uv", "build", "--out-dir", out_dir])


def _remove_path(path: Path) -> bool:
    if path.is_dir():
        shutil.rmtree(path)
        return True
    if path.exists():
        path.unlink()
        return True
    return False


def _is_cleanable_descendant(path: Path) -> bool:
    return not any(part in IGNORED_CLEAN_PARTS for part in path.relative_to(REPO_ROOT).parts)


def clean() -> None:
    removed: list[str] = []
    for directory in CLEAN_DIRECTORIES:
        path = REPO_ROOT / directory
        if _remove_path(path):
            removed.append(directory)
    for path in sorted(REPO_ROOT.rglob("__pycache__")):
        if _is_cleanable_descendant(path) and _remove_path(path):
            removed.append(str(path.relative_to(REPO_ROOT)))
    for path in sorted(REPO_ROOT.glob(".coverage*")):
        if path.is_file() and _remove_path(path):
            removed.append(str(path.relative_to(REPO_ROOT)))
    for path in sorted(REPO_ROOT.glob("*.egg-info")):
        if _remove_path(path):
            removed.append(str(path.relative_to(REPO_ROOT)))
    if removed:
        print("Removed:")
        for item in removed:
            print(f"- {item}")
    else:
        print("Nothing to clean.")
    raise SystemExit(0)


def build() -> None:
    _run_or_exit(["uv", "build", *sys.argv[1:]])


def dev() -> None:
    if sys.argv[1:]:
        _run_or_exit(["activity-report", *sys.argv[1:]])
    _run_or_exit(["activity-report", "report", "--input", "data/fixtures/activity_log.csv"])


def lint() -> None:
    steps: list[list[str]] = [
        ["ruff", "check", *PYTHON_TARGETS, "--ignore-noqa", *sys.argv[1:]],
        ["lint-imports"],
    ]
    for args in steps:
        code = _run(args)
        if code != 0:
            raise SystemExit(code)
    raise SystemExit(0)


def lint_fix() -> None:
    steps: list[list[str]] = [
        ["ruff", "check", *PYTHON_TARGETS, "--fix", "--ignore-noqa", *sys.argv[1:]],
        ["lint-imports"],
    ]
    for args in steps:
        code = _run(args)
        if code != 0:
            raise SystemExit(code)
    raise SystemExit(0)


def format_gate() -> None:
    _run_or_exit(["ruff", "format", "--check", *PYTHON_TARGETS, *sys.argv[1:]])


def format_fix() -> None:
    _run_or_exit(["ruff", "format", *PYTHON_TARGETS, *sys.argv[1:]])


def typecheck() -> None:
    raise SystemExit(_run(["pyright", *sys.argv[1:]]))


def repo_audit() -> None:
    _run_or_exit([sys.executable, "tools/repo_audit.py", *sys.argv[1:]])


def test() -> None:
    _run_or_exit(["pytest", *sys.argv[1:]])


def coverage() -> None:
    _run_or_exit(
        [
            "pytest",
            "--cov=oaknational.python_repo_template",
            "--cov-report=term-missing",
            *sys.argv[1:],
        ]
    )


def fix() -> None:
    steps: list[tuple[str, Sequence[str] | Callable[[], int]]] = [
        ("format-fix", ["ruff", "format", *PYTHON_TARGETS]),
        ("lint-fix", ["ruff", "check", *PYTHON_TARGETS, "--fix", "--ignore-noqa"]),
        ("format-fix", ["ruff", "format", *PYTHON_TARGETS]),
        ("import-linter", ["lint-imports"]),
    ]
    _run_gate_sequence(steps)


def check_ci() -> None:
    steps: list[tuple[str, Sequence[str] | Callable[[], int]]] = [
        ("format", ["ruff", "format", "--check", *PYTHON_TARGETS]),
        ("typecheck", ["pyright"]),
        ("lint", ["ruff", "check", *PYTHON_TARGETS, "--ignore-noqa"]),
        ("import-linter", ["lint-imports"]),
        ("repo-audit", [sys.executable, "tools/repo_audit.py"]),
        ("build", _run_build_probe),
        ("test", ["pytest"]),
        (
            "coverage",
            [
                "pytest",
                "--cov=oaknational.python_repo_template",
                "--cov-report=term-missing",
            ],
        ),
    ]
    _run_gate_sequence(steps)


def check() -> None:
    steps: list[tuple[str, Sequence[str] | Callable[[], int]]] = [
        ("format-fix", ["ruff", "format", *PYTHON_TARGETS]),
        ("lint-fix", ["ruff", "check", *PYTHON_TARGETS, "--fix", "--ignore-noqa"]),
        ("format-fix", ["ruff", "format", *PYTHON_TARGETS]),
        ("import-linter", ["lint-imports"]),
        ("format", ["ruff", "format", "--check", *PYTHON_TARGETS]),
        ("typecheck", ["pyright"]),
        ("lint", ["ruff", "check", *PYTHON_TARGETS, "--ignore-noqa"]),
        ("repo-audit", [sys.executable, "tools/repo_audit.py"]),
        ("build", _run_build_probe),
        ("test", ["pytest"]),
        (
            "coverage",
            [
                "pytest",
                "--cov=oaknational.python_repo_template",
                "--cov-report=term-missing",
            ],
        ),
    ]
    _run_gate_sequence(steps)


def main() -> None:
    if len(sys.argv) < 2:
        msg = (
            "Usage: uv run <clean|build|dev|lint|lint-fix|format|format-fix|typecheck|"
            "repo-audit|test|coverage|fix|check|check-ci> [args...]"
        )
        raise SystemExit(msg)

    command = sys.argv[1]
    passthrough = sys.argv[2:]
    sys.argv = [sys.argv[0], *passthrough]

    dispatch: dict[str, Callable[[], None]] = {
        "clean": clean,
        "build": build,
        "dev": dev,
        "lint": lint,
        "lint-fix": lint_fix,
        "format": format_gate,
        "format-fix": format_fix,
        "typecheck": typecheck,
        "repo-audit": repo_audit,
        "test": test,
        "coverage": coverage,
        "fix": fix,
        "check": check,
        "check-ci": check_ci,
    }
    fn = dispatch.get(command)
    if fn is None:
        msg = f"Unknown command: {command!r}"
        raise SystemExit(msg)
    fn()


if __name__ == "__main__":
    main()
