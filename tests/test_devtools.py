from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import cast

import pytest

import oaknational.python_repo_template.devtools as subject
from oaknational.python_repo_template.gate_registry import GateCommand


class Result:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode


def test_clean_removes_repo_cache_without_touching_virtualenv_cache(tmp_path: Path) -> None:
    repo_cache = tmp_path / "src" / "oaknational" / "python_repo_template" / "__pycache__"
    venv_cache = tmp_path / ".venv" / "lib" / "python3.14" / "site-packages" / "__pycache__"
    repo_cache.mkdir(parents=True)
    venv_cache.mkdir(parents=True)

    with pytest.raises(SystemExit) as exc_info:
        subject.clean([], repo_root=tmp_path)

    assert exc_info.value.code == 0
    assert not repo_cache.exists()
    assert venv_cache.exists()


def test_run_uses_target_script_directly_for_absolute_commands(tmp_path: Path) -> None:
    absolute_script = tmp_path / "activity-report"
    absolute_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(
        args: Sequence[str],
        *,
        check: bool,
        cwd: Path | None = None,
    ) -> Result:
        assert check is False
        calls.append((list(args), cwd))
        return Result(0)

    assert (
        subject.run_command(
            [str(absolute_script), "report"],
            cwd=tmp_path,
            process_runner=fake_run,
        )
        == 0
    )
    assert calls == [([str(absolute_script), "report"], tmp_path)]


def test_build_without_passthrough_builds_then_smokes(tmp_path: Path) -> None:
    wheel_path = tmp_path / "dist" / "oaknational_python_repo_template-0.1.0-py3-none-any.whl"
    build_calls: list[tuple[Path | None, tuple[str, ...]]] = []
    smoke_targets: list[Path] = []

    def fake_build_distribution(
        *,
        out_dir: Path | None = None,
        extra_args: Sequence[str] = (),
    ) -> int:
        build_calls.append((out_dir, tuple(extra_args)))
        return 0

    def fake_select_built_wheel(dist_dir: Path) -> Path:
        assert dist_dir == subject.REPO_ROOT / "dist"
        return wheel_path

    def fake_smoke_check(candidate: Path) -> int:
        smoke_targets.append(candidate)
        return 0

    with pytest.raises(SystemExit) as exc_info:
        subject.build(
            [],
            build_distribution=fake_build_distribution,
            select_built_wheel=fake_select_built_wheel,
            smoke_check=fake_smoke_check,
        )

    assert exc_info.value.code == 0
    assert build_calls == [(None, ())]
    assert smoke_targets == [wheel_path]


def test_run_build_probe_uses_a_temporary_dist_dir(tmp_path: Path) -> None:
    run_build_probe_name = "_run_build_probe"
    run_build_probe = cast(Callable[..., int], getattr(subject, run_build_probe_name))
    build_dirs: list[Path] = []
    selected_dirs: list[Path] = []
    smoke_targets: list[Path] = []
    temp_root = tmp_path / "build-probe"
    wheel_path = temp_root / "oaknational_python_repo_template-0.1.0-py3-none-any.whl"

    class FakeTemporaryDirectory:
        def __init__(self, *, prefix: str) -> None:
            assert prefix == "oaknational-python-repo-template-build-"

        def __enter__(self) -> str:
            temp_root.mkdir(parents=True, exist_ok=True)
            return str(temp_root)

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

    def fake_build_distribution(
        *,
        out_dir: Path | None = None,
        extra_args: Sequence[str] = (),
    ) -> int:
        assert extra_args == ()
        assert out_dir is not None
        build_dirs.append(out_dir)
        return 0

    def fake_select_built_wheel(dist_dir: Path) -> Path:
        selected_dirs.append(dist_dir)
        return wheel_path

    def fake_smoke_check(candidate: Path) -> int:
        smoke_targets.append(candidate)
        return 0

    assert (
        run_build_probe(
            build_distribution=fake_build_distribution,
            select_built_wheel=fake_select_built_wheel,
            smoke_check=fake_smoke_check,
            temporary_directory=FakeTemporaryDirectory,
        )
        == 0
    )
    assert build_dirs == [temp_root]
    assert selected_dirs == [temp_root]
    assert smoke_targets == [wheel_path]
    assert not temp_root.is_relative_to(subject.REPO_ROOT)


def test_run_installed_wheel_smoke_check_uses_out_of_repo_workspace_and_installed_surfaces(
    tmp_path: Path,
) -> None:
    run_installed_wheel_smoke_check_name = "_run_installed_wheel_smoke_check"
    run_installed_wheel_smoke_check = cast(
        Callable[..., int],
        getattr(subject, run_installed_wheel_smoke_check_name),
    )
    temp_root = tmp_path / "wheel-smoke"
    wheel_path = temp_root / "oaknational_python_repo_template-0.1.0-py3-none-any.whl"
    workspace = temp_root / "workspace"
    venv_dir = temp_root / "venv"
    copied_to: list[Path] = []
    venv_commands: list[tuple[Path, str]] = []
    run_calls: list[tuple[list[str], Path | None]] = []

    class FakeTemporaryDirectory:
        def __init__(self, *, prefix: str) -> None:
            assert prefix == "oaknational-python-repo-template-wheel-smoke-"

        def __enter__(self) -> str:
            temp_root.mkdir(parents=True, exist_ok=True)
            return str(temp_root)

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

    def fake_copy_smoke_activity_pack(destination: Path) -> Path:
        copied_to.append(destination)
        return destination / "activity_log.csv"

    def fake_venv_command(target_venv_dir: Path, command: str) -> str:
        venv_commands.append((target_venv_dir, command))
        return str(target_venv_dir / "bin" / command)

    def fake_command_runner(args: Sequence[str], *, cwd: Path | None = None) -> int:
        run_calls.append(([str(arg) for arg in args], cwd))
        return 0

    assert (
        run_installed_wheel_smoke_check(
            wheel_path,
            temporary_directory=FakeTemporaryDirectory,
            copy_smoke_activity_pack=fake_copy_smoke_activity_pack,
            venv_command=fake_venv_command,
            command_runner=fake_command_runner,
        )
        == 0
    )
    assert copied_to == [workspace]
    assert venv_commands == [
        (venv_dir, "python"),
        (venv_dir, "activity-report"),
    ]
    assert all(cwd == workspace for _args, cwd in run_calls)
    assert run_calls[0][0] == ["uv", "venv", "--no-project", str(venv_dir)]
    assert run_calls[1][0] == [
        "uv",
        "pip",
        "install",
        "--python",
        str(venv_dir / "bin" / "python"),
        str(wheel_path),
    ]
    assert run_calls[2][0][0] == str(venv_dir / "bin" / "python")
    assert "Installed wheel resolved back to the source tree." in run_calls[2][0][2]
    assert run_calls[3][0] == [
        str(venv_dir / "bin" / "activity-report"),
        "report",
        "--input",
        str(workspace / "activity_log.csv"),
    ]
    assert run_calls[4][0] == [
        str(venv_dir / "bin" / "python"),
        "-m",
        "oaknational.python_repo_template",
        "report",
        "--input",
        str(workspace / "activity_log.csv"),
    ]
    assert not workspace.is_relative_to(subject.REPO_ROOT)


def test_build_rejects_passthrough_args() -> None:
    with pytest.raises(SystemExit) as exc_info:
        subject.build(["--wheel"])

    assert str(exc_info.value) == "build does not accept arguments: --wheel"


@pytest.mark.parametrize(
    ("function", "expected_names"),
    [
        (
            subject.check_ci,
            [
                "format",
                "typecheck",
                "lint",
                "import-linter",
                "dependency-hygiene",
                "repo-audit",
                "build",
                "test",
                "coverage",
            ],
        ),
        (
            subject.check,
            [
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
            ],
        ),
    ],
)
def test_aggregate_gates_include_dependency_hygiene(
    function: Callable[..., None],
    expected_names: list[str],
) -> None:
    captured_steps: list[tuple[str, Sequence[str] | Callable[[], int]]] = []

    def fake_run_gate_sequence(
        steps: Sequence[tuple[str, Sequence[str] | Callable[[], int]]],
    ) -> None:
        captured_steps.extend(steps)

    function(
        [],
        run_gate_sequence=fake_run_gate_sequence,
        python_executable="/tmp/test-python",
    )

    assert [name for name, _runner in captured_steps] == expected_names
    assert ("dependency-hygiene", ["deptry", "."]) in captured_steps
    assert ("repo-audit", ["/tmp/test-python", "tools/repo_audit.py"]) in captured_steps


def test_fix_gate_steps_follow_the_canonical_contract() -> None:
    steps = subject.gate_steps("fix")

    assert [name for name, _runner in steps] == [
        "format-fix",
        "lint-fix",
        "format-fix",
        "import-linter",
    ]


def test_main_reports_usage_without_a_repo_local_command() -> None:
    with pytest.raises(SystemExit) as exc_info:
        subject.main([])

    expected_message = (
        "Usage: uv run python -m oaknational.python_repo_template.devtools "
        "<clean|build|dev|lint|lint-fix|format|format-fix|typecheck|repo-audit|"
        "test|coverage|fix|check|check-ci> [args...]"
    )
    assert str(exc_info.value) == expected_message


def test_main_rejects_unknown_repo_local_command() -> None:
    with pytest.raises(SystemExit) as exc_info:
        subject.main(["unknown"])

    assert str(exc_info.value) == "Unknown command: 'unknown'"


def test_main_dispatches_the_selected_repo_local_command() -> None:
    calls: list[tuple[str, ...]] = []

    def fake_check(args: Sequence[str] | None = None) -> None:
        calls.append(tuple(() if args is None else args))
        raise SystemExit(0)

    with pytest.raises(SystemExit) as exc_info:
        subject.main(
            ["check", "--quiet"],
            command_definitions=(GateCommand(name="check", handler_name="fake_check"),),
            namespace={"fake_check": fake_check},
        )

    assert exc_info.value.code == 0
    assert calls == [("--quiet",)]


def test_main_fails_closed_when_the_gate_contract_points_to_a_missing_handler() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        subject.main(
            ["check"],
            command_definitions=(GateCommand(name="check", handler_name="missing_handler"),),
            namespace={},
        )

    assert str(exc_info.value) == "Missing gate-command handler: 'missing_handler'"
