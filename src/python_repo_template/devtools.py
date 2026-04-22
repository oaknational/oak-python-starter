"""Developer tooling entrypoints for ``uv run`` quality checks."""

from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path


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


def lint() -> None:
    steps: list[list[str]] = [
        ["ruff", "check", "src", "tests", "tools", "--ignore-noqa", *sys.argv[1:]],
        ["lint-imports"],
    ]
    for args in steps:
        code = _run(args)
        if code != 0:
            raise SystemExit(code)
    raise SystemExit(0)


def format_code() -> None:
    _run_or_exit(["ruff", "format", "src", "tests", "tools", *sys.argv[1:]])


def format_check() -> None:
    _run_or_exit(["ruff", "format", "--check", "src", "tests", "tools", *sys.argv[1:]])


def typecheck() -> None:
    raise SystemExit(_run(["pyright", *sys.argv[1:]]))


def repo_audit() -> None:
    _run_or_exit([sys.executable, "tools/repo_audit.py", *sys.argv[1:]])


def test() -> None:
    _run_or_exit(["pytest", *sys.argv[1:]])


def coverage() -> None:
    _run_or_exit(
        ["pytest", "--cov=python_repo_template", "--cov-report=term-missing", *sys.argv[1:]]
    )


def check() -> None:
    steps: list[tuple[str, list[str]]] = [
        ("format-check", ["ruff", "format", "--check", "src", "tests", "tools"]),
        ("typecheck", ["pyright"]),
        ("lint", ["ruff", "check", "src", "tests", "tools", "--ignore-noqa"]),
        ("import-linter", ["lint-imports"]),
        ("repo-audit", [sys.executable, "tools/repo_audit.py"]),
        ("test", ["pytest"]),
        ("coverage", ["pytest", "--cov=python_repo_template", "--cov-report=term-missing"]),
    ]
    for name, args in steps:
        print(f"==> {name}: {' '.join(args)}")
        start = time.perf_counter()
        code = _run(args)
        duration = time.perf_counter() - start
        if code != 0:
            print(f"FAILED: {name} ({duration:.2f}s)")
            raise SystemExit(code)
        print(f"PASS: {name} ({duration:.2f}s)")
    print("all checks passed")
    raise SystemExit(0)


def main() -> None:
    if len(sys.argv) < 2:
        msg = (
            "Usage: uv run <lint|format|format-check|typecheck|repo-audit|test|coverage|check>"
            " [args...]"
        )
        raise SystemExit(msg)

    command = sys.argv[1]
    passthrough = sys.argv[2:]
    sys.argv = [sys.argv[0], *passthrough]

    dispatch: dict[str, Callable[[], None]] = {
        "lint": lint,
        "format": format_code,
        "format-check": format_check,
        "typecheck": typecheck,
        "repo-audit": repo_audit,
        "test": test,
        "coverage": coverage,
        "check": check,
    }
    fn = dispatch.get(command)
    if fn is None:
        msg = f"Unknown command: {command!r}"
        raise SystemExit(msg)
    fn()


if __name__ == "__main__":
    main()
