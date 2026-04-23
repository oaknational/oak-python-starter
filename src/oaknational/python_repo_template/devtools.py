"""Repo-local developer tooling entrypoints for ``uv run python -m`` checks."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol, cast

from oaknational.python_repo_template.gate_registry import (
    CANONICAL_GATE_COMMANDS,
    GateCommand,
    canonical_gate_names,
    gate_sequence,
)

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


class CompletedProcessLike(Protocol):
    """Minimal subprocess result surface needed by the command runner."""

    returncode: int


class TemporaryDirectoryFactory(Protocol):
    """Protocol for creating temporary directories in tests and production."""

    def __call__(self, *, prefix: str) -> AbstractContextManager[str]: ...


class StepCommandRunner(Protocol):
    """Protocol for command runners used by build smoke helpers."""

    def __call__(self, args: Sequence[str], *, cwd: Path | None = None) -> int: ...


def _command_args(args: Sequence[str] | None) -> tuple[str, ...]:
    return tuple(sys.argv[1:] if args is None else args)


def _reject_unexpected_args(command_name: str, args: Sequence[str]) -> None:
    if args:
        joined_args = " ".join(args)
        msg = f"{command_name} does not accept arguments: {joined_args}"
        raise SystemExit(msg)


def _resolve_executable(command: str) -> tuple[str, bool]:
    command_path = Path(command)
    if not command_path.is_absolute() and command_path.parent == Path("."):
        candidate = Path(sys.executable).parent / command
        if candidate.exists():
            return str(candidate), True
    return command, False


def _venv_bin_directory(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts"
    return venv_dir / "bin"


def _venv_command(venv_dir: Path, command: str) -> str:
    bin_directory = _venv_bin_directory(venv_dir)
    candidates = [command]
    if sys.platform == "win32":
        candidates = [f"{command}.exe", f"{command}.cmd", command]
    for candidate in candidates:
        path = bin_directory / candidate
        if path.exists():
            return str(path)
    return str(bin_directory / candidates[0])


def _build_distribution(*, out_dir: Path | None = None, extra_args: Sequence[str] = ()) -> int:
    args = ["uv", "build"]
    if out_dir is not None:
        args.extend(["--out-dir", str(out_dir)])
    args.extend(extra_args)
    return run_command(args)


def _select_built_wheel(dist_dir: Path) -> Path | None:
    wheels = sorted(
        dist_dir.glob("*.whl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not wheels:
        print(f"No wheel artefact found in {dist_dir}.")
        return None
    return wheels[0]


def _copy_smoke_activity_pack(destination: Path) -> Path:
    fixture = REPO_ROOT / "data" / "fixtures" / "activity_log.csv"
    metadata = REPO_ROOT / "data" / "fixtures" / "activity_log.metadata.yaml"
    shutil.copy2(fixture, destination / fixture.name)
    shutil.copy2(metadata, destination / metadata.name)
    return destination / fixture.name


def _run_installed_wheel_smoke_check(
    wheel_path: Path,
    *,
    temporary_directory: TemporaryDirectoryFactory = tempfile.TemporaryDirectory,
    copy_smoke_activity_pack: Callable[[Path], Path] = _copy_smoke_activity_pack,
    venv_command: Callable[[Path, str], str] = _venv_command,
    command_runner: StepCommandRunner | None = None,
) -> int:
    runner = run_command if command_runner is None else command_runner
    with temporary_directory(prefix="oaknational-python-repo-template-wheel-smoke-") as temp_dir:
        temp_root = Path(temp_dir)
        workspace = temp_root / "workspace"
        workspace.mkdir()
        smoke_input = copy_smoke_activity_pack(workspace)
        venv_dir = temp_root / "venv"
        venv_python = venv_command(venv_dir, "python")

        steps = [
            ["uv", "venv", "--no-project", str(venv_dir)],
            ["uv", "pip", "install", "--python", venv_python, str(wheel_path)],
            [
                venv_python,
                "-c",
                (
                    "import sys\n"
                    "from pathlib import Path\n"
                    "import oaknational.python_repo_template as package\n"
                    f"repo_root = Path({str(REPO_ROOT)!r}).resolve()\n"
                    "package_path = Path(package.__file__).resolve()\n"
                    "print(package_path)\n"
                    "if package_path.is_relative_to(repo_root):\n"
                    "    message = 'Installed wheel resolved back to the source tree.'\n"
                    "    print(message, file=sys.stderr)\n"
                    "    raise SystemExit(1)\n"
                ),
            ],
            [venv_command(venv_dir, "activity-report"), "report", "--input", str(smoke_input)],
            [
                venv_python,
                "-m",
                "oaknational.python_repo_template",
                "report",
                "--input",
                str(smoke_input),
            ],
        ]
        for args in steps:
            code = runner(args, cwd=workspace)
            if code != 0:
                return code
    return 0


def _run_default_build(
    *,
    build_distribution: Callable[..., int] = _build_distribution,
    select_built_wheel: Callable[[Path], Path | None] = _select_built_wheel,
    smoke_check: Callable[[Path], int] = _run_installed_wheel_smoke_check,
    dist_dir: Path | None = None,
) -> int:
    target_dist_dir = REPO_ROOT / "dist" if dist_dir is None else dist_dir
    code = build_distribution()
    if code != 0:
        return code
    wheel_path = select_built_wheel(target_dist_dir)
    if wheel_path is None:
        return 1
    return smoke_check(wheel_path)


def _is_python_script(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(2) == b"#!"
    except OSError:
        return False


def run_command(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    current_python: str = sys.executable,
    process_runner: Callable[..., CompletedProcessLike] = subprocess.run,
) -> int:
    if not args:
        raise ValueError("Expected at least one argument to run a command.")
    command, uses_current_python = _resolve_executable(str(args[0]))
    resolved_path = Path(command)
    rest = [str(arg) for arg in args[1:]]
    if uses_current_python and resolved_path.exists() and _is_python_script(resolved_path):
        resolved_args = [current_python, str(resolved_path), *rest]
    else:
        resolved_args = [command, *rest]
    result = process_runner(resolved_args, check=False, cwd=cwd)
    return result.returncode


def _run_or_exit(args: Sequence[str], *, current_python: str = sys.executable) -> None:
    raise SystemExit(run_command(args, current_python=current_python))


def _run_named_step(name: str, runner: Sequence[str] | Callable[[], int]) -> None:
    if callable(runner):
        print(f"==> {name}")
    else:
        print(f"==> {name}: {' '.join(runner)}")
    start = time.perf_counter()
    code = runner() if callable(runner) else run_command(runner)
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


def _run_build_probe(
    *,
    build_distribution: Callable[..., int] = _build_distribution,
    select_built_wheel: Callable[[Path], Path | None] = _select_built_wheel,
    smoke_check: Callable[[Path], int] = _run_installed_wheel_smoke_check,
    temporary_directory: TemporaryDirectoryFactory = tempfile.TemporaryDirectory,
) -> int:
    with temporary_directory(prefix="oaknational-python-repo-template-build-") as out_dir:
        dist_dir = Path(out_dir)
        code = build_distribution(out_dir=dist_dir)
        if code != 0:
            return code
        wheel_path = select_built_wheel(dist_dir)
        if wheel_path is None:
            return 1
        return smoke_check(wheel_path)


def _remove_path(path: Path) -> bool:
    if path.is_dir():
        shutil.rmtree(path)
        return True
    if path.exists():
        path.unlink()
        return True
    return False


def _is_cleanable_descendant(path: Path) -> bool:
    return not any(part in IGNORED_CLEAN_PARTS for part in path.parts)


def _clean_paths(repo_root: Path) -> list[str]:
    removed: list[str] = []
    for directory in CLEAN_DIRECTORIES:
        path = repo_root / directory
        if _remove_path(path):
            removed.append(directory)
    for path in sorted(repo_root.rglob("__pycache__")):
        relative_path = path.relative_to(repo_root)
        if _is_cleanable_descendant(relative_path) and _remove_path(path):
            removed.append(str(relative_path))
    for path in sorted(repo_root.glob(".coverage*")):
        if path.is_file() and _remove_path(path):
            removed.append(str(path.relative_to(repo_root)))
    for path in sorted(repo_root.glob("*.egg-info")):
        if _remove_path(path):
            removed.append(str(path.relative_to(repo_root)))
    return removed


def clean(
    args: Sequence[str] | None = None,
    *,
    repo_root: Path = REPO_ROOT,
) -> None:
    _reject_unexpected_args("clean", _command_args(args))
    removed = _clean_paths(repo_root)
    if removed:
        print("Removed:")
        for item in removed:
            print(f"- {item}")
    else:
        print("Nothing to clean.")
    raise SystemExit(0)


def build(
    args: Sequence[str] | None = None,
    build_distribution: Callable[..., int] = _build_distribution,
    select_built_wheel: Callable[[Path], Path | None] = _select_built_wheel,
    smoke_check: Callable[[Path], int] = _run_installed_wheel_smoke_check,
) -> None:
    command_args = _command_args(args)
    _reject_unexpected_args("build", command_args)
    raise SystemExit(
        _run_default_build(
            build_distribution=build_distribution,
            select_built_wheel=select_built_wheel,
            smoke_check=smoke_check,
        )
    )


def dev(args: Sequence[str] | None = None) -> None:
    command_args = _command_args(args)
    if command_args:
        _run_or_exit(["activity-report", *command_args])
    _run_or_exit(["activity-report", "report", "--input", "data/fixtures/activity_log.csv"])


def lint(args: Sequence[str] | None = None) -> None:
    command_args = _command_args(args)
    steps: list[list[str]] = [
        ["ruff", "check", *PYTHON_TARGETS, "--ignore-noqa", *command_args],
        ["lint-imports"],
    ]
    for step_args in steps:
        code = run_command(step_args)
        if code != 0:
            raise SystemExit(code)
    raise SystemExit(0)


def lint_fix(args: Sequence[str] | None = None) -> None:
    command_args = _command_args(args)
    steps: list[list[str]] = [
        ["ruff", "check", *PYTHON_TARGETS, "--fix", "--ignore-noqa", *command_args],
        ["lint-imports"],
    ]
    for step_args in steps:
        code = run_command(step_args)
        if code != 0:
            raise SystemExit(code)
    raise SystemExit(0)


def format_gate(args: Sequence[str] | None = None) -> None:
    _run_or_exit(["ruff", "format", "--check", *PYTHON_TARGETS, *_command_args(args)])


def format_fix(args: Sequence[str] | None = None) -> None:
    _run_or_exit(["ruff", "format", *PYTHON_TARGETS, *_command_args(args)])


def typecheck(args: Sequence[str] | None = None) -> None:
    raise SystemExit(run_command(["pyright", *_command_args(args)]))


def repo_audit(args: Sequence[str] | None = None) -> None:
    _run_or_exit([sys.executable, "tools/repo_audit.py", *_command_args(args)])


def test(args: Sequence[str] | None = None) -> None:
    _run_or_exit(["pytest", *_command_args(args)])


def coverage(args: Sequence[str] | None = None) -> None:
    _run_or_exit(
        [
            "pytest",
            "--cov=oaknational.python_repo_template",
            "--cov-report=term-missing",
            *_command_args(args),
        ]
    )


def _step_runners(
    *,
    python_executable: str = sys.executable,
) -> dict[str, Sequence[str] | Callable[[], int]]:
    return {
        "format": ["ruff", "format", "--check", *PYTHON_TARGETS],
        "format-fix": ["ruff", "format", *PYTHON_TARGETS],
        "typecheck": ["pyright"],
        "lint": ["ruff", "check", *PYTHON_TARGETS, "--ignore-noqa"],
        "lint-fix": ["ruff", "check", *PYTHON_TARGETS, "--fix", "--ignore-noqa"],
        "import-linter": ["lint-imports"],
        "dependency-hygiene": ["deptry", "."],
        "repo-audit": [python_executable, "tools/repo_audit.py"],
        "build": _run_build_probe,
        "test": ["pytest"],
        "coverage": [
            "pytest",
            "--cov=oaknational.python_repo_template",
            "--cov-report=term-missing",
        ],
    }


def gate_steps(
    sequence_name: str,
    *,
    python_executable: str = sys.executable,
) -> tuple[tuple[str, Sequence[str] | Callable[[], int]], ...]:
    runners = _step_runners(python_executable=python_executable)
    return tuple((name, runners[name]) for name in gate_sequence(sequence_name))


def fix(args: Sequence[str] | None = None) -> None:
    _reject_unexpected_args("fix", _command_args(args))
    _run_gate_sequence(gate_steps("fix"))


def check_ci(
    args: Sequence[str] | None = None,
    *,
    run_gate_sequence: Callable[
        [Sequence[tuple[str, Sequence[str] | Callable[[], int]]]],
        None,
    ] = _run_gate_sequence,
    python_executable: str = sys.executable,
) -> None:
    _reject_unexpected_args("check-ci", _command_args(args))
    run_gate_sequence(gate_steps("check-ci", python_executable=python_executable))


def check(
    args: Sequence[str] | None = None,
    *,
    run_gate_sequence: Callable[
        [Sequence[tuple[str, Sequence[str] | Callable[[], int]]]],
        None,
    ] = _run_gate_sequence,
    python_executable: str = sys.executable,
) -> None:
    _reject_unexpected_args("check", _command_args(args))
    run_gate_sequence(gate_steps("check", python_executable=python_executable))


def _dispatch_table(
    *,
    command_definitions: Sequence[GateCommand] = CANONICAL_GATE_COMMANDS,
    namespace: Mapping[str, object] | None = None,
) -> dict[str, Callable[[Sequence[str] | None], None]]:
    source = globals() if namespace is None else namespace
    dispatch: dict[str, Callable[[Sequence[str] | None], None]] = {}
    for command_definition in command_definitions:
        handler = source.get(command_definition.handler_name)
        if not callable(handler):
            msg = f"Missing gate-command handler: {command_definition.handler_name!r}"
            raise RuntimeError(msg)
        dispatch[command_definition.name] = cast(Callable[[Sequence[str] | None], None], handler)
    return dispatch


def main(
    argv: Sequence[str] | None = None,
    *,
    command_definitions: Sequence[GateCommand] = CANONICAL_GATE_COMMANDS,
    namespace: Mapping[str, object] | None = None,
) -> None:
    command_line = _command_args(argv)
    command_names = tuple(command.name for command in command_definitions)
    if not command_line:
        msg = (
            "Usage: uv run python -m oaknational.python_repo_template.devtools "
            f"<{'|'.join(command_names or canonical_gate_names())}> [args...]"
        )
        raise SystemExit(msg)

    command = command_line[0]
    passthrough = command_line[1:]

    dispatch = _dispatch_table(command_definitions=command_definitions, namespace=namespace)
    fn = dispatch.get(command)
    if fn is None:
        msg = f"Unknown command: {command!r}"
        raise SystemExit(msg)
    fn(passthrough)


if __name__ == "__main__":
    main()
