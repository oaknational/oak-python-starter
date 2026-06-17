from __future__ import annotations

import io
import json

import pytest

import tools.agent_hooks as subject

QUALITY_GATE_MESSAGE = (
    "If Python or tooling files change, run uv run python -m "
    "oaknational.python_repo_template.devtools check before you stop."
)
SKIP_BYPASS_REASON = (
    "SKIP is prohibited here when it bypasses the repo's quality-gates or "
    "commitizen-commit-msg hooks."
)
HOOKS_PATH_BYPASS_REASON = (
    "core.hooksPath overrides are prohibited here because they bypass repo git hooks."
)
GIT_CONFIG_ENV_BYPASS_REASON = (
    "GIT_CONFIG_* is prohibited here because it can hide hook bypasses or force pushes."
)
GIT_ALIAS_BYPASS_REASON = (
    "Git alias overrides are prohibited here because they can hide hook bypasses or force pushes."
)
DYNAMIC_GIT_CONFIG_REASON = (
    "Dynamic git config is prohibited here for git commit and git push because "
    "it can hide hook bypasses or force pushes."
)


def test_load_policy_reads_the_canonical_repo_policy() -> None:
    policy = subject.load_policy()

    assert (
        policy.session_start_message
        == "Read .agent/commands/start-right-quick.md before substantive work."
    )
    assert policy.quality_gate_message == QUALITY_GATE_MESSAGE
    assert policy.blocked_pre_commit_skip_ids == ("quality-gates", "commitizen-commit-msg")
    assert policy.blocked_pre_commit_skip_reason == SKIP_BYPASS_REASON
    assert policy.blocked_hook_bypass_env_var_prefixes == (
        subject.BlockedPrefix(
            prefix="GIT_CONFIG_",
            reason=GIT_CONFIG_ENV_BYPASS_REASON,
        ),
    )
    assert policy.blocked_git_config_prefixes == (
        subject.BlockedPrefix(
            prefix="alias.",
            reason=GIT_ALIAS_BYPASS_REASON,
        ),
    )
    assert policy.blocked_dynamic_git_config_reason == DYNAMIC_GIT_CONFIG_REASON


def test_normalise_pre_tool_payload_extracts_shell_command_per_platform() -> None:
    assert subject.normalise_hook_context(
        platform="cursor",
        event="pre-tool",
        payload={
            "tool_name": "Shell",
            "tool_input": {"command": "git stash", "working_directory": "/project"},
            "cwd": "/project",
        },
    ) == subject.HookContext(
        platform="cursor",
        event="pre-tool",
        shell_command="git stash",
        session_source=None,
    )
    assert subject.normalise_hook_context(
        platform="claude",
        event="pre-tool",
        payload={
            "tool_name": "Bash",
            "tool_input": {"command": "git reset --hard"},
            "cwd": "/project",
        },
    ) == subject.HookContext(
        platform="claude",
        event="pre-tool",
        shell_command="git reset --hard",
        session_source=None,
    )
    assert subject.normalise_hook_context(
        platform="gemini",
        event="pre-tool",
        payload={
            "tool_name": "run_shell_command",
            "tool_input": {"command": "git clean -fd"},
            "cwd": "/project",
        },
    ) == subject.HookContext(
        platform="gemini",
        event="pre-tool",
        shell_command="git clean -fd",
        session_source=None,
    )
    assert subject.normalise_hook_context(
        platform="github",
        event="pre-tool",
        payload={
            "toolName": "bash",
            "toolArgs": json.dumps({"command": "git push --force", "description": "push"}),
            "cwd": "/project",
        },
    ) == subject.HookContext(
        platform="github",
        event="pre-tool",
        shell_command="git push --force",
        session_source=None,
    )


def test_normalise_session_start_payload_preserves_platform_sources() -> None:
    assert subject.normalise_hook_context(
        platform="cursor",
        event="session-start",
        payload={"session_id": "cursor-session"},
    ) == subject.HookContext(
        platform="cursor",
        event="session-start",
        shell_command=None,
        session_source=None,
    )
    assert subject.normalise_hook_context(
        platform="claude",
        event="session-start",
        payload={"session_id": "claude-session"},
    ) == subject.HookContext(
        platform="claude",
        event="session-start",
        shell_command=None,
        session_source=None,
    )
    assert subject.normalise_hook_context(
        platform="gemini",
        event="session-start",
        payload={"source": "startup"},
    ) == subject.HookContext(
        platform="gemini",
        event="session-start",
        shell_command=None,
        session_source="startup",
    )


def test_evaluate_hook_policy_denies_repo_canonical_prohibited_shell_commands() -> None:
    policy = subject.load_policy()

    cases = [
        ("git stash", "git stash is prohibited here because it can lose uncommitted work."),
        (
            "git reset --hard",
            "git reset is prohibited here because it can discard commits or changes.",
        ),
        (
            "git checkout -- pyproject.toml",
            "git checkout -- is prohibited here because it discards uncommitted changes.",
        ),
        ("git clean -fd", "git clean is prohibited here because it deletes untracked files."),
        ("git rebase main", "git rebase is prohibited here because it rewrites history."),
        (
            "git commit --no-verify -m test",
            "--no-verify is prohibited here because it bypasses git hooks.",
        ),
        (
            "git push --force origin main",
            "Force push is prohibited here because it overwrites remote history.",
        ),
        (
            "git push -f origin main",
            "Force push is prohibited here because it overwrites remote history.",
        ),
        (
            "git push --force-with-lease origin main",
            "Force push is prohibited here because it overwrites remote history.",
        ),
        (
            "SKIP=quality-gates git commit -m test",
            SKIP_BYPASS_REASON,
        ),
        (
            "SKIP=quality-gates env git commit -m test",
            SKIP_BYPASS_REASON,
        ),
        (
            "env SKIP=commitizen-commit-msg git commit -m test",
            SKIP_BYPASS_REASON,
        ),
        (
            "env -i SKIP=quality-gates git commit -m test",
            SKIP_BYPASS_REASON,
        ),
        (
            "export SKIP=quality-gates && git commit -m test",
            SKIP_BYPASS_REASON,
        ),
        (
            "HUSKY=0 git push origin main",
            "HUSKY=0 is prohibited here because it disables git hooks.",
        ),
        (
            "SKIP_HOOKS=1 git commit -m test",
            "SKIP_HOOKS=1 is prohibited here because it disables git hooks.",
        ),
        (
            "git commit --no-pre-commit -m test",
            "--no-pre-commit is prohibited here because it bypasses pre-commit hooks.",
        ),
        (
            "command git commit --no-pre-commit -m test",
            "--no-pre-commit is prohibited here because it bypasses pre-commit hooks.",
        ),
        (
            "git -c core.hooksPath=/dev/null commit -m test",
            HOOKS_PATH_BYPASS_REASON,
        ),
        (
            "git --config-env=core.hooksPath=HOOKS_PATH commit -m test",
            HOOKS_PATH_BYPASS_REASON,
        ),
        (
            "git -c color.ui=always commit -m test",
            DYNAMIC_GIT_CONFIG_REASON,
        ),
        (
            "git -c alias.c='commit --no-verify' c -m test",
            GIT_ALIAS_BYPASS_REASON,
        ),
        (
            "git -c alias.fp='push --force' fp origin main",
            GIT_ALIAS_BYPASS_REASON,
        ),
        (
            "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath "
            "GIT_CONFIG_VALUE_0=/dev/null git commit -m test",
            GIT_CONFIG_ENV_BYPASS_REASON,
        ),
        (
            "sh -c 'SKIP=quality-gates git commit -m test'",
            SKIP_BYPASS_REASON,
        ),
        (
            "bash -lc 'HUSKY=0 git push origin main'",
            "HUSKY=0 is prohibited here because it disables git hooks.",
        ),
        (
            "/bin/bash -lc 'git push --force origin main'",
            "Force push is prohibited here because it overwrites remote history.",
        ),
        (
            "/bin/bash -lc 'git -c core.hooksPath=/dev/null commit -m test'",
            HOOKS_PATH_BYPASS_REASON,
        ),
        (
            "/bin/bash -lc 'git commit --no-pre-commit -m test'",
            "--no-pre-commit is prohibited here because it bypasses pre-commit hooks.",
        ),
        (
            "/bin/sh -c 'SKIP=quality-gates git commit -m test'",
            SKIP_BYPASS_REASON,
        ),
        (
            "/usr/bin/env bash -lc 'SKIP=quality-gates git commit -m test'",
            SKIP_BYPASS_REASON,
        ),
        (
            "/usr/bin/env /bin/bash -lc 'git push --force origin main'",
            "Force push is prohibited here because it overwrites remote history.",
        ),
        (
            "export SKIP=quality-gates\ngit commit -m test",
            SKIP_BYPASS_REASON,
        ),
    ]

    for command, reason in cases:
        outcome = subject.evaluate_hook_policy(
            policy,
            subject.HookContext(
                platform="github",
                event="pre-tool",
                shell_command=command,
                session_source=None,
            ),
        )

        assert outcome == subject.HookOutcome(
            decision="deny",
            reason=reason,
            message=None,
        )


def test_evaluate_hook_policy_allows_safe_shell_commands_and_safe_mentions() -> None:
    policy = subject.load_policy()

    safe_commands = [
        "uv run python -m oaknational.python_repo_template.devtools check",
        "echo SKIP=quality-gates",
        "SKIP=quality-gates python -c 'print(1)'",
        "export SKIP=quality-gates && python -c 'print(1)'",
    ]
    for command in safe_commands:
        assert subject.evaluate_hook_policy(
            policy,
            subject.HookContext(
                platform="cursor",
                event="pre-tool",
                shell_command=command,
                session_source=None,
            ),
        ) == subject.HookOutcome(decision="allow", reason=None, message=None)

    assert subject.evaluate_hook_policy(
        policy,
        subject.HookContext(
            platform="cursor",
            event="pre-tool",
            shell_command=None,
            session_source=None,
        ),
    ) == subject.HookOutcome(decision="allow", reason=None, message=None)


def test_evaluate_hook_policy_generates_session_start_advisory_message() -> None:
    policy = subject.load_policy()
    expected = (
        "Read .agent/commands/start-right-quick.md before substantive work.\n"
        f"{QUALITY_GATE_MESSAGE}"
    )

    for platform in ("cursor", "claude", "gemini"):
        assert subject.evaluate_hook_policy(
            policy,
            subject.HookContext(
                platform=platform,
                event="session-start",
                shell_command=None,
                session_source="startup" if platform == "gemini" else None,
            ),
        ) == subject.HookOutcome(decision="advisory", reason=None, message=expected)


def test_render_hook_emission_matches_platform_output_contracts() -> None:
    advisory = subject.HookOutcome(
        decision="advisory",
        reason=None,
        message=f"Ground first.\n{QUALITY_GATE_MESSAGE}",
    )
    allow = subject.HookOutcome(decision="allow", reason=None, message=None)
    deny = subject.HookOutcome(
        decision="deny",
        reason="git reset is prohibited here because it can discard commits or changes.",
        message=None,
    )

    cursor_session = subject.render_hook_emission(
        platform="cursor",
        event="session-start",
        outcome=advisory,
    )
    assert cursor_session.exit_code == 0
    assert json.loads(cursor_session.stdout) == {
        "additional_context": f"Ground first.\n{QUALITY_GATE_MESSAGE}"
    }

    claude_session = subject.render_hook_emission(
        platform="claude",
        event="session-start",
        outcome=advisory,
    )
    assert claude_session.exit_code == 0
    assert claude_session.stdout == f"Ground first.\n{QUALITY_GATE_MESSAGE}"
    assert claude_session.stderr == ""

    gemini_session = subject.render_hook_emission(
        platform="gemini",
        event="session-start",
        outcome=advisory,
    )
    assert gemini_session.exit_code == 0
    assert json.loads(gemini_session.stdout) == {
        "systemMessage": f"Ground first.\n{QUALITY_GATE_MESSAGE}",
        "hookSpecificOutput": {"additionalContext": f"Ground first.\n{QUALITY_GATE_MESSAGE}"},
    }

    github_deny = subject.render_hook_emission(
        platform="github",
        event="pre-tool",
        outcome=deny,
    )
    assert github_deny.exit_code == 0
    assert json.loads(github_deny.stdout) == {
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "git reset is prohibited here because it can discard commits or changes."
        ),
    }

    claude_deny = subject.render_hook_emission(
        platform="claude",
        event="pre-tool",
        outcome=deny,
    )
    assert claude_deny.exit_code == 2
    assert claude_deny.stdout == ""
    assert (
        claude_deny.stderr
        == "git reset is prohibited here because it can discard commits or changes."
    )

    cursor_allow = subject.render_hook_emission(
        platform="cursor",
        event="pre-tool",
        outcome=allow,
    )
    assert cursor_allow == subject.RenderedHookEmission(
        exit_code=0,
        stdout='{"continue":true,"permission":"allow"}',
        stderr="",
    )

    claude_allow = subject.render_hook_emission(
        platform="claude",
        event="pre-tool",
        outcome=allow,
    )
    assert claude_allow == subject.RenderedHookEmission(exit_code=0, stdout="", stderr="")

    gemini_allow = subject.render_hook_emission(
        platform="gemini",
        event="pre-tool",
        outcome=allow,
    )
    assert gemini_allow == subject.RenderedHookEmission(
        exit_code=0,
        stdout='{"decision":"allow"}',
        stderr="",
    )

    github_allow = subject.render_hook_emission(
        platform="github",
        event="pre-tool",
        outcome=allow,
    )
    assert github_allow == subject.RenderedHookEmission(exit_code=0, stdout="", stderr="")


def test_main_emits_cursor_session_start_payload() -> None:
    stdin = io.StringIO("{}")
    stdout = io.StringIO()
    stderr = io.StringIO()

    with pytest.raises(SystemExit) as exc_info:
        subject.main(
            ["--platform", "cursor", "--event", "session-start"],
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )

    assert exc_info.value.code == 0
    assert stderr.getvalue() == ""
    assert json.loads(stdout.getvalue()) == {
        "additional_context": (
            "Read .agent/commands/start-right-quick.md before substantive work.\n"
            f"{QUALITY_GATE_MESSAGE}"
        )
    }


def test_main_emits_github_deny_payload_for_skip_bypass() -> None:
    stdin = io.StringIO(
        json.dumps(
            {
                "toolName": "bash",
                "toolArgs": json.dumps({"command": "env SKIP=quality-gates git commit -m test"}),
            }
        )
    )
    stdout = io.StringIO()
    stderr = io.StringIO()

    with pytest.raises(SystemExit) as exc_info:
        subject.main(
            ["--platform", "github", "--event", "pre-tool"],
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )

    assert exc_info.value.code == 0
    assert stderr.getvalue() == ""
    assert json.loads(stdout.getvalue()) == {
        "permissionDecision": "deny",
        "permissionDecisionReason": SKIP_BYPASS_REASON,
    }
