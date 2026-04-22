#!/usr/bin/env python3
"""Shared runtime for the repo's cross-platform agent hook guardrails."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / ".agent/hooks/policy.json"

Platform = Literal["cursor", "claude", "gemini", "github"]
Event = Literal["session-start", "pre-tool"]


@dataclass(frozen=True)
class BlockedShellPattern:
    """Repo-canonical shell-command rule used by the hook runtime."""

    pattern: str
    reason: str


@dataclass(frozen=True)
class HookPolicy:
    """Canonical hook policy loaded from `.agent/hooks/policy.json`."""

    session_start_message: str
    quality_gate_message: str
    blocked_shell_patterns: tuple[BlockedShellPattern, ...]


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


def load_policy(path: Path = POLICY_PATH) -> HookPolicy:
    """Load the canonical hook policy from disk."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    blocked = tuple(
        BlockedShellPattern(
            pattern=str(entry["pattern"]),
            reason=str(entry["reason"]),
        )
        for entry in raw["blocked_shell_patterns"]
    )
    return HookPolicy(
        session_start_message=str(raw["session_start_message"]),
        quality_gate_message=str(raw["quality_gate_message"]),
        blocked_shell_patterns=blocked,
    )


def normalise_hook_context(platform: Platform, event: Event, payload: object) -> HookContext:
    """Normalise platform-native hook payloads into one repo-level shape."""

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
            session_source = _as_str(payload.get("source"))
        return HookContext(
            platform=platform,
            event=event,
            shell_command=None,
            session_source=session_source,
        )
    shell_command = None
    if platform == "cursor":
        tool_name = _as_str(payload.get("tool_name"))
        tool_input = _as_mapping(payload.get("tool_input"))
        if tool_name == "Shell":
            shell_command = _as_str(tool_input.get("command"))
    elif platform == "claude":
        tool_name = _as_str(payload.get("tool_name"))
        tool_input = _as_mapping(payload.get("tool_input"))
        if tool_name == "Bash":
            shell_command = _as_str(tool_input.get("command"))
    elif platform == "gemini":
        tool_name = _as_str(payload.get("tool_name"))
        tool_input = _as_mapping(payload.get("tool_input"))
        if tool_name == "run_shell_command":
            shell_command = _as_str(tool_input.get("command"))
    elif platform == "github":
        tool_name = _as_str(payload.get("toolName"))
        tool_args = _parse_tool_args(payload.get("toolArgs"))
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
    for blocked in policy.blocked_shell_patterns:
        if re.search(blocked.pattern, context.shell_command):
            return HookOutcome(decision="deny", reason=blocked.reason, message=None)
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


def main() -> None:
    """Load the canonical policy, evaluate the hook payload, and emit a response."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--platform", required=True, choices=["cursor", "claude", "gemini", "github"]
    )
    parser.add_argument("--event", required=True, choices=["session-start", "pre-tool"])
    args = parser.parse_args()

    payload = json.load(sys.stdin)
    policy = load_policy()
    context = normalise_hook_context(
        platform=args.platform,
        event=args.event,
        payload=payload,
    )
    outcome = evaluate_hook_policy(policy, context)
    emission = render_hook_emission(args.platform, args.event, outcome)

    if emission.stdout:
        sys.stdout.write(emission.stdout)
    if emission.stderr:
        sys.stderr.write(emission.stderr)
    raise SystemExit(emission.exit_code)


def _as_mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    return {}


def _as_str(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _parse_tool_args(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return parsed
    return {}


def _json(payload: object) -> str:
    return json.dumps(payload, separators=(",", ":"))


if __name__ == "__main__":
    main()
