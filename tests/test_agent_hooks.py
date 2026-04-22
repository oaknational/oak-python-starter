import json

import tools.agent_hooks as subject


def make_policy() -> subject.HookPolicy:
    return subject.HookPolicy(
        session_start_message="Read .agent/commands/start-right-quick.md before substantive work.",
        quality_gate_message="If Python or tooling files change, run uv run check before you stop.",
        blocked_shell_patterns=(
            subject.BlockedShellPattern(
                pattern=r"(^|\s)git\s+stash(\s|$)",
                reason="git stash is prohibited here because it can lose uncommitted work.",
            ),
            subject.BlockedShellPattern(
                pattern=r"(^|\s)git\s+reset(\s|$)",
                reason="git reset is prohibited here because it can discard commits or changes.",
            ),
            subject.BlockedShellPattern(
                pattern=r"(^|\s)git\s+checkout\s+--(\s|$)",
                reason=(
                    "git checkout -- is prohibited here because it discards uncommitted changes."
                ),
            ),
            subject.BlockedShellPattern(
                pattern=r"(^|\s)git\s+clean(\s|$)",
                reason="git clean is prohibited here because it deletes untracked files.",
            ),
            subject.BlockedShellPattern(
                pattern=r"(^|\s)git\s+rebase(\s|$)",
                reason="git rebase is prohibited here because it rewrites history.",
            ),
            subject.BlockedShellPattern(
                pattern=r"(^|\s)--no-verify(\s|$)",
                reason="--no-verify is prohibited here because it bypasses git hooks.",
            ),
            subject.BlockedShellPattern(
                pattern=r"(^|\s)git\s+push\b[^\n]*\s(--force|-f)(\s|$)",
                reason="Force push is prohibited here because it overwrites remote history.",
            ),
        ),
    )


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
        payload={
            "session_id": "cursor-session",
            "is_background_agent": False,
            "composer_mode": "agent",
        },
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
    policy = make_policy()

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


def test_evaluate_hook_policy_allows_safe_shell_commands_and_non_shell_tools() -> None:
    policy = make_policy()

    assert subject.evaluate_hook_policy(
        policy,
        subject.HookContext(
            platform="cursor",
            event="pre-tool",
            shell_command="uv run check",
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
    policy = make_policy()
    expected = (
        "Read .agent/commands/start-right-quick.md before substantive work.\n"
        "If Python or tooling files change, run uv run check before you stop."
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
        message="Ground first.\nRun uv run check before you stop.",
    )
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
        "additional_context": "Ground first.\nRun uv run check before you stop."
    }

    claude_session = subject.render_hook_emission(
        platform="claude",
        event="session-start",
        outcome=advisory,
    )
    assert claude_session.exit_code == 0
    assert claude_session.stdout == "Ground first.\nRun uv run check before you stop."
    assert claude_session.stderr == ""

    gemini_session = subject.render_hook_emission(
        platform="gemini",
        event="session-start",
        outcome=advisory,
    )
    assert gemini_session.exit_code == 0
    assert json.loads(gemini_session.stdout) == {
        "systemMessage": "Ground first.\nRun uv run check before you stop.",
        "hookSpecificOutput": {
            "additionalContext": "Ground first.\nRun uv run check before you stop."
        },
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
