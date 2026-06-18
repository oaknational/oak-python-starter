#!/usr/bin/env python3
"""Shared runtime for the repo's cross-platform agent hook guardrails."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TextIO, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / ".agent/hooks/policy.json"

Platform = Literal["cursor", "claude", "gemini", "github"]
Event = Literal["session-start", "pre-tool"]
JsonObject = dict[str, object]


@dataclass(frozen=True)
class BlockedShellPattern:
    """Repo-canonical shell-command rule used by the hook runtime."""

    pattern: str
    reason: str


@dataclass(frozen=True)
class BlockedToken:
    """Canonical token-level bypass rule used by hook evaluation."""

    token: str
    reason: str


@dataclass(frozen=True)
class BlockedEnvironmentAssignment:
    """Canonical env-assignment bypass rule used by hook evaluation."""

    name: str
    value: str
    reason: str


@dataclass(frozen=True)
class BlockedGitConfigOverride:
    """Canonical git-config override rule used by hook evaluation."""

    name: str
    reason: str


@dataclass(frozen=True)
class BlockedPrefix:
    """Canonical prefix-based rule used by hook evaluation."""

    prefix: str
    reason: str


@dataclass(frozen=True)
class HookPolicy:
    """Canonical hook policy loaded from `.agent/hooks/policy.json`."""

    session_start_message: str
    quality_gate_message: str
    blocked_shell_patterns: tuple[BlockedShellPattern, ...]
    blocked_hook_bypass_flags: tuple[BlockedToken, ...]
    blocked_hook_bypass_env_vars: tuple[BlockedEnvironmentAssignment, ...]
    blocked_git_config_overrides: tuple[BlockedGitConfigOverride, ...]
    blocked_hook_bypass_env_var_prefixes: tuple[BlockedPrefix, ...]
    blocked_git_config_prefixes: tuple[BlockedPrefix, ...]
    blocked_pre_commit_skip_ids: tuple[str, ...]
    blocked_pre_commit_skip_reason: str
    blocked_dynamic_git_config_reason: str


@dataclass(frozen=True)
class HookContext:
    """Normalised hook payload used by policy evaluation."""

    platform: Platform
    event: Event
    shell_command: str | None
    session_source: str | None


@dataclass(frozen=True)
class HookOutcome:
    """Decision returned by policy evaluation."""

    decision: Literal["allow", "deny", "advisory"]
    reason: str | None
    message: str | None


@dataclass(frozen=True)
class RenderedHookEmission:
    """Platform-specific hook output ready for stdout, stderr, and exit."""

    exit_code: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class GitInvocation:
    """Normalised git command shape used by hook-bypass detection."""

    subcommand: str
    tokens: tuple[str, ...]
    config_overrides: tuple[str, ...]
    has_dynamic_config: bool


def load_policy(path: Path = POLICY_PATH) -> HookPolicy:
    """Load the canonical hook policy from disk."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    blocked_shell_patterns = tuple(
        BlockedShellPattern(
            pattern=str(entry["pattern"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_shell_patterns"]
    )
    blocked_hook_bypass_flags = tuple(
        BlockedToken(
            token=str(entry["token"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_hook_bypass_flags"]
    )
    blocked_hook_bypass_env_vars = tuple(
        BlockedEnvironmentAssignment(
            name=str(entry["name"]),
            value=str(entry["value"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_hook_bypass_env_vars"]
    )
    blocked_git_config_overrides = tuple(
        BlockedGitConfigOverride(
            name=str(entry["name"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_git_config_overrides"]
    )
    blocked_hook_bypass_env_var_prefixes = tuple(
        BlockedPrefix(
            prefix=str(entry["prefix"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_hook_bypass_env_var_prefixes"]
    )
    blocked_git_config_prefixes = tuple(
        BlockedPrefix(
            prefix=str(entry["prefix"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_git_config_prefixes"]
    )
    return HookPolicy(
        session_start_message=str(raw["session_start_message"]),
        quality_gate_message=str(raw["quality_gate_message"]),
        blocked_shell_patterns=blocked_shell_patterns,
        blocked_hook_bypass_flags=blocked_hook_bypass_flags,
        blocked_hook_bypass_env_vars=blocked_hook_bypass_env_vars,
        blocked_git_config_overrides=blocked_git_config_overrides,
        blocked_hook_bypass_env_var_prefixes=blocked_hook_bypass_env_var_prefixes,
        blocked_git_config_prefixes=blocked_git_config_prefixes,
        blocked_pre_commit_skip_ids=tuple(str(item) for item in raw["blocked_pre_commit_skip_ids"]),
        blocked_pre_commit_skip_reason=str(raw["blocked_pre_commit_skip_reason"]),
        blocked_dynamic_git_config_reason=str(raw["blocked_dynamic_git_config_reason"]),
    )


def normalise_hook_context(platform: Platform, event: Event, payload: object) -> HookContext:
    """Normalise platform-native hook payloads into one repo-level shape."""

    payload_mapping = _as_mapping(payload)
    if not isinstance(payload, dict):
        return HookContext(
            platform=platform,
            event=event,
            shell_command=None,
            session_source=None,
        )
    if event == "session-start":
        session_source = None
        if platform == "gemini":
            session_source = _as_str(payload_mapping.get("source"))
        return HookContext(
            platform=platform,
            event=event,
            shell_command=None,
            session_source=session_source,
        )
    shell_command = None
    if platform == "cursor":
        tool_name = _as_str(payload_mapping.get("tool_name"))
        tool_input = _as_mapping(payload_mapping.get("tool_input"))
        if tool_name == "Shell":
            shell_command = _as_str(tool_input.get("command"))
    elif platform == "claude":
        tool_name = _as_str(payload_mapping.get("tool_name"))
        tool_input = _as_mapping(payload_mapping.get("tool_input"))
        if tool_name == "Bash":
            shell_command = _as_str(tool_input.get("command"))
    elif platform == "gemini":
        tool_name = _as_str(payload_mapping.get("tool_name"))
        tool_input = _as_mapping(payload_mapping.get("tool_input"))
        if tool_name == "run_shell_command":
            shell_command = _as_str(tool_input.get("command"))
    elif platform == "github":
        tool_name = _as_str(payload_mapping.get("toolName"))
        tool_args = _parse_tool_args(payload_mapping.get("toolArgs"))
        if tool_name == "bash":
            shell_command = _as_str(tool_args.get("command"))
    return HookContext(
        platform=platform,
        event=event,
        shell_command=shell_command,
        session_source=None,
    )


def evaluate_hook_policy(policy: HookPolicy, context: HookContext) -> HookOutcome:
    """Evaluate the normalised hook context against the canonical policy."""

    if context.event == "session-start":
        return HookOutcome(
            decision="advisory",
            reason=None,
            message=f"{policy.session_start_message}\n{policy.quality_gate_message}",
        )
    if context.shell_command is None:
        return HookOutcome(decision="allow", reason=None, message=None)
    hook_bypass_reason = _hook_bypass_reason(policy, context.shell_command)
    if hook_bypass_reason is not None:
        return HookOutcome(decision="deny", reason=hook_bypass_reason, message=None)
    blocked_shell_pattern_reason = _blocked_shell_pattern_reason(policy, context.shell_command)
    if blocked_shell_pattern_reason is not None:
        return HookOutcome(decision="deny", reason=blocked_shell_pattern_reason, message=None)
    return HookOutcome(decision="allow", reason=None, message=None)


def render_hook_emission(
    platform: Platform,
    event: Event,
    outcome: HookOutcome,
) -> RenderedHookEmission:
    """Render a repo-level outcome into a platform-native hook response."""

    if platform == "cursor":
        if event == "session-start":
            return RenderedHookEmission(
                exit_code=0,
                stdout=_json({"additional_context": outcome.message or ""}),
                stderr="",
            )
        permission = "deny" if outcome.decision == "deny" else "allow"
        payload: dict[str, object] = {"continue": True, "permission": permission}
        if outcome.reason is not None:
            payload["user_message"] = outcome.reason
            payload["agent_message"] = outcome.reason
        return RenderedHookEmission(exit_code=0, stdout=_json(payload), stderr="")

    if platform == "claude":
        if event == "session-start":
            return RenderedHookEmission(
                exit_code=0,
                stdout=outcome.message or "",
                stderr="",
            )
        if outcome.decision == "deny":
            return RenderedHookEmission(
                exit_code=2,
                stdout="",
                stderr=outcome.reason or "Blocked by repo hook policy.",
            )
        return RenderedHookEmission(exit_code=0, stdout="", stderr="")

    if platform == "gemini":
        if event == "session-start":
            message = outcome.message or ""
            return RenderedHookEmission(
                exit_code=0,
                stdout=_json(
                    {
                        "systemMessage": message,
                        "hookSpecificOutput": {"additionalContext": message},
                    }
                ),
                stderr="",
            )
        decision = "deny" if outcome.decision == "deny" else "allow"
        payload: dict[str, object] = {"decision": decision}
        if outcome.reason is not None:
            payload["reason"] = outcome.reason
        return RenderedHookEmission(exit_code=0, stdout=_json(payload), stderr="")

    if outcome.decision == "deny":
        return RenderedHookEmission(
            exit_code=0,
            stdout=_json(
                {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": outcome.reason or "Blocked by repo hook policy.",
                }
            ),
            stderr="",
        )
    return RenderedHookEmission(exit_code=0, stdout="", stderr="")


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    policy_path: Path = POLICY_PATH,
) -> None:
    """Load the canonical policy, evaluate the hook payload, and emit a response."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--platform", required=True, choices=["cursor", "claude", "gemini", "github"]
    )
    parser.add_argument("--event", required=True, choices=["session-start", "pre-tool"])
    args = parser.parse_args(argv)

    input_stream = sys.stdin if stdin is None else stdin
    output_stream = sys.stdout if stdout is None else stdout
    error_stream = sys.stderr if stderr is None else stderr

    payload = json.load(input_stream)
    policy = load_policy(policy_path)
    context = normalise_hook_context(
        platform=args.platform,
        event=args.event,
        payload=payload,
    )
    outcome = evaluate_hook_policy(policy, context)
    emission = render_hook_emission(args.platform, args.event, outcome)

    if emission.stdout:
        output_stream.write(emission.stdout)
    if emission.stderr:
        error_stream.write(emission.stderr)
    raise SystemExit(emission.exit_code)


def _as_mapping(value: object) -> JsonObject:
    if not isinstance(value, dict):
        return {}
    mapping: JsonObject = {}
    for key, item in cast(dict[object, object], value).items():
        if isinstance(key, str):
            mapping[key] = item
    return mapping


def _as_str(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _parse_tool_args(value: object) -> JsonObject:
    if isinstance(value, dict):
        return _as_mapping(cast(dict[object, object], value))
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return _as_mapping(cast(dict[object, object], parsed))
    return {}


def _json(payload: object) -> str:
    return json.dumps(payload, separators=(",", ":"))


def _reason_with_substitutions(
    policy: HookPolicy,
    command: str,
    check: Callable[[HookPolicy, str], str | None],
) -> str | None:
    """Run ``check`` on ``command``, then recurse into each substitution body.

    Recursion is bounded because every substitution body is strictly shorter
    than the command that contains it.
    """

    reason = check(policy, command)
    if reason is not None:
        return reason
    for inner_command in _substitution_commands(command):
        nested_reason = _reason_with_substitutions(policy, inner_command, check)
        if nested_reason is not None:
            return nested_reason
    return None


def _hook_bypass_reason_for_command(policy: HookPolicy, command: str) -> str | None:
    return _hook_bypass_reason_for_segments(policy, _shell_segments(command), {})


def _blocked_shell_pattern_reason_for_command(policy: HookPolicy, command: str) -> str | None:
    return _blocked_shell_pattern_reason_for_segments(policy, _shell_segments(command))


def _hook_bypass_reason(policy: HookPolicy, command: str) -> str | None:
    command = _strip_quoted_heredoc_bodies(command)
    return _reason_with_substitutions(policy, command, _hook_bypass_reason_for_command)


def _blocked_shell_pattern_reason(policy: HookPolicy, command: str) -> str | None:
    command = _strip_quoted_heredoc_bodies(command)
    return _reason_with_substitutions(policy, command, _blocked_shell_pattern_reason_for_command)


_QUOTED_HEREDOC_OPENER = re.compile(r"<<-?\s*(['\"])(\w+)\1")


def _strip_quoted_heredoc_bodies(command: str) -> str:
    """Drop the literal body of each quoted-delimiter here-document.

    A quoted delimiter (``<<'EOF'`` / ``<<"EOF"``) makes the body literal text
    with no expansion, so it is data rather than commands; analysing it produces
    false positives — most importantly a commit message that merely *documents* a
    blocked command. Unquoted ``<<EOF`` bodies undergo expansion and may contain a
    live ``$(...)``, so they are left in place to stay checked.
    """

    if "<<" not in command:
        return command
    kept_lines: list[str] = []
    open_tags: list[str] = []
    for line in command.split("\n"):
        if open_tags:
            if line.strip() == open_tags[0]:
                open_tags.pop(0)
            continue
        kept_lines.append(line)
        open_tags.extend(match.group(2) for match in _QUOTED_HEREDOC_OPENER.finditer(line))
    return "\n".join(kept_lines)


def _blocked_shell_pattern_reason_for_segments(
    policy: HookPolicy,
    segments: tuple[tuple[str, ...], ...],
) -> str | None:
    for segment in segments:
        export_result = _exported_environment_assignments(segment)
        segment_tokens = segment if export_result is None else export_result[1]
        if not segment_tokens:
            continue
        _env, command_tokens = _normalise_wrapped_command(segment_tokens)
        nested_command = _shell_launcher_command(command_tokens)
        if nested_command is not None:
            nested_reason = _blocked_shell_pattern_reason_for_segments(
                policy,
                _shell_segments(nested_command),
            )
            if nested_reason is not None:
                return nested_reason
        candidate = " ".join(command_tokens)
        for blocked in policy.blocked_shell_patterns:
            if re.search(blocked.pattern, candidate):
                return blocked.reason
    return None


def _hook_bypass_reason_for_segments(
    policy: HookPolicy,
    segments: tuple[tuple[str, ...], ...],
    exported_env: dict[str, str],
) -> str | None:
    current_exported_env = dict(exported_env)
    for segment in segments:
        export_result = _exported_environment_assignments(segment)
        segment_tokens = segment
        if export_result is not None:
            exported_updates, remainder = export_result
            current_exported_env.update(exported_updates)
            if not remainder:
                continue
            segment_tokens = remainder
        inline_env, command_tokens = _normalise_wrapped_command(segment_tokens)
        effective_env = {**current_exported_env, **inline_env}
        nested_command = _shell_launcher_command(command_tokens)
        if nested_command is not None:
            nested_reason = _hook_bypass_reason_for_segments(
                policy,
                _shell_segments(nested_command),
                effective_env,
            )
            if nested_reason is not None:
                return nested_reason
            continue
        git_invocation = _git_invocation(command_tokens)
        if git_invocation is None:
            continue
        for blocked in policy.blocked_hook_bypass_env_var_prefixes:
            if any(name.startswith(blocked.prefix) for name in effective_env):
                return blocked.reason
        for blocked in policy.blocked_git_config_prefixes:
            if any(
                config_name.startswith(blocked.prefix.casefold())
                for config_name in git_invocation.config_overrides
            ):
                return blocked.reason
        for blocked in policy.blocked_git_config_overrides:
            if blocked.name.casefold() in git_invocation.config_overrides:
                return blocked.reason
        if git_invocation.subcommand in {"commit", "push"} and git_invocation.has_dynamic_config:
            return policy.blocked_dynamic_git_config_reason
        if git_invocation.subcommand not in {"commit", "push"}:
            continue
        for blocked in policy.blocked_hook_bypass_flags:
            if blocked.token in git_invocation.tokens:
                return blocked.reason
        for blocked in policy.blocked_hook_bypass_env_vars:
            if effective_env.get(blocked.name) == blocked.value:
                return blocked.reason
        skip_value = effective_env.get("SKIP")
        if skip_value is not None:
            requested_ids = {item.strip() for item in skip_value.split(",") if item.strip()}
            if requested_ids.intersection(policy.blocked_pre_commit_skip_ids):
                return policy.blocked_pre_commit_skip_reason
    return None


def _shell_segments(command: str) -> tuple[tuple[str, ...], ...]:
    try:
        tokens = tuple(shlex.split(command, posix=True))
    except ValueError:
        tokens = tuple(command.split())

    segments: list[tuple[str, ...]] = []
    current: list[str] = []
    for token in tokens:
        if token in {"&&", "||", ";", "|"}:
            if current:
                segments.append(tuple(current))
                current = []
            continue
        current.append(token)
    if current:
        segments.append(tuple(current))
    return tuple(segments)


def _single_quoted_mask(command: str) -> tuple[bool, ...]:
    """Mark each character that lies inside a single-quoted span.

    Single quotes suppress command substitution in POSIX shells; double quotes
    do not. A single quote that itself sits inside double quotes is literal, so
    double-quote state is tracked only to gate single-quote toggling. Backslash
    escaping is intentionally not modelled — erring towards more checking.
    """

    mask: list[bool] = []
    in_single = False
    in_double = False
    for char in command:
        mask.append(in_single)
        if in_single:
            if char == "'":
                in_single = False
        elif in_double:
            if char == '"':
                in_double = False
        elif char == "'":
            in_single = True
        elif char == '"':
            in_double = True
    return tuple(mask)


def _substitution_commands(command: str) -> tuple[str, ...]:
    """Extract the inner command of each ``$(...)`` and backtick substitution.

    Substitutions inside single quotes are skipped because the shell treats them
    as literal text. Only the outermost substitutions are returned; nested ones
    are recovered when each inner command is itself evaluated, which also bounds
    the recursion because every inner command is strictly shorter than its
    parent. Bare subshells ``(...)`` are deliberately out of scope here; see the
    rename/guardrail notes for the documented residual.
    """

    inner_commands: list[str] = []
    mask = _single_quoted_mask(command)
    index = 0
    length = len(command)
    while index < length:
        char = command[index]
        if mask[index]:
            index += 1
            continue
        if char == "$" and index + 1 < length and command[index + 1] == "(":
            body, index = _read_balanced_substitution(command, index + 2, mask)
            if body:
                inner_commands.append(body)
            continue
        if char == "`":
            end = command.find("`", index + 1)
            if end == -1:
                inner_commands.append(command[index + 1 :])
                break
            inner_commands.append(command[index + 1 : end])
            index = end + 1
            continue
        index += 1
    return tuple(inner_commands)


def _read_balanced_substitution(
    command: str,
    start: int,
    mask: tuple[bool, ...],
) -> tuple[str, int]:
    """Return the body of a ``$(...)`` opened before ``start`` and the index past it.

    Parentheses are balanced so nested ``$(...)`` and subshells close correctly,
    ignoring parentheses inside single-quoted spans. An unterminated
    substitution fails safe-side: the remainder is returned so it is still
    checked rather than silently skipped.
    """

    depth = 1
    index = start
    length = len(command)
    while index < length:
        if not mask[index]:
            char = command[index]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return command[start:index], index + 1
        index += 1
    return command[start:], length


def _exported_environment_assignments(
    tokens: tuple[str, ...],
) -> tuple[dict[str, str], tuple[str, ...]] | None:
    if not tokens or tokens[0] != "export":
        return None

    exported_env: dict[str, str] = {}
    index = 1
    while index < len(tokens):
        name, value = _environment_assignment(tokens[index])
        if name is None:
            break
        exported_env[name] = value
        index += 1
    return exported_env, tokens[index:]


def _normalise_wrapped_command(
    tokens: tuple[str, ...],
) -> tuple[dict[str, str], tuple[str, ...]]:
    env: dict[str, str] = {}
    remaining = tokens
    while remaining:
        if remaining[0] == "command":
            remaining = _strip_command_builtin(remaining)
            continue
        env_updates, next_tokens, consumed = _consume_env_command(remaining)
        if consumed:
            env.update(env_updates)
            remaining = next_tokens
            continue
        inline_env, next_tokens = _consume_inline_environment_assignments(remaining)
        if not inline_env:
            break
        env.update(inline_env)
        remaining = next_tokens
    return env, remaining


def _shell_launcher_command(tokens: tuple[str, ...]) -> str | None:
    if not tokens or Path(tokens[0]).name not in {"bash", "dash", "ksh", "sh", "zsh"}:
        return None

    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            index += 1
            continue
        if token.startswith("--"):
            index += 1
            continue
        if token.startswith("-"):
            if "c" in token[1:]:
                if index + 1 >= len(tokens):
                    return None
                return tokens[index + 1]
            index += 1
            continue
        return None
    return None


def _consume_env_command(
    tokens: tuple[str, ...],
) -> tuple[dict[str, str], tuple[str, ...], bool]:
    if not tokens or Path(tokens[0]).name != "env":
        return {}, tokens, False

    env: dict[str, str] = {}
    index = 1
    while index < len(tokens):
        token = tokens[index]
        name, value = _environment_assignment(token)
        if name is not None:
            env[name] = value
            index += 1
            continue
        if token == "--":
            index += 1
            break
        if _env_option_consumes_next(token):
            index = min(len(tokens), index + 2)
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    return env, tokens[index:], True


def _env_option_consumes_next(token: str) -> bool:
    return token in {"-C", "--chdir", "-S", "--split-string", "-u", "--unset"}


def _consume_inline_environment_assignments(
    tokens: tuple[str, ...],
) -> tuple[dict[str, str], tuple[str, ...]]:
    env: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        name, value = _environment_assignment(tokens[index])
        if name is None:
            break
        env[name] = value
        index += 1
    return env, tokens[index:]


def _strip_command_builtin(tokens: tuple[str, ...]) -> tuple[str, ...]:
    index = 1
    while index < len(tokens) and tokens[index] in {"-p", "-v", "-V"}:
        index += 1
    if index < len(tokens) and tokens[index] == "--":
        index += 1
    return tokens[index:]


def _environment_assignment(token: str) -> tuple[str | None, str]:
    if "=" not in token:
        return None, ""
    name, value = token.split("=", maxsplit=1)
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return None, ""
    return name, value


def _git_invocation(tokens: tuple[str, ...]) -> GitInvocation | None:
    if not tokens or tokens[0] != "git":
        return None

    config_overrides: list[str] = []
    has_dynamic_config = False
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            index += 1
            break
        if token == "-c":
            if index + 1 >= len(tokens):
                return None
            has_dynamic_config = True
            config_name = _git_config_name(tokens[index + 1])
            if config_name is not None:
                config_overrides.append(config_name)
            index += 2
            continue
        if token.startswith("-c") and token != "-c":
            has_dynamic_config = True
            config_name = _git_config_name(token[2:])
            if config_name is not None:
                config_overrides.append(config_name)
            index += 1
            continue
        if token == "--config-env":
            if index + 1 >= len(tokens):
                return None
            has_dynamic_config = True
            config_name = _git_config_name(tokens[index + 1])
            if config_name is not None:
                config_overrides.append(config_name)
            index += 2
            continue
        if token.startswith("--config-env="):
            has_dynamic_config = True
            config_name = _git_config_name(token.partition("=")[2])
            if config_name is not None:
                config_overrides.append(config_name)
            index += 1
            continue
        if token.startswith(
            ("--exec-path=", "--git-dir=", "--work-tree=", "--namespace=", "--super-prefix=")
        ):
            index += 1
            continue
        if _git_global_option_consumes_next(token):
            index = min(len(tokens), index + 2)
            continue
        if token.startswith("-"):
            index += 1
            continue
        return GitInvocation(
            subcommand=token,
            tokens=tokens,
            config_overrides=tuple(config_overrides),
            has_dynamic_config=has_dynamic_config,
        )
    return None


def _git_global_option_consumes_next(token: str) -> bool:
    return token in {"-C", "--exec-path", "--git-dir", "--work-tree", "--namespace"}


def _git_config_name(value: str) -> str | None:
    if "=" not in value:
        return None
    return value.split("=", maxsplit=1)[0].casefold()


if __name__ == "__main__":
    main()
