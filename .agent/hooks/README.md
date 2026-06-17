# Hook Guardrails

Canonical hook policy for the repo's supported native hook surfaces.

## Purpose

This layer keeps hook behaviour small, explicit, and deterministic:

- advisory grounding at session start where the platform can show it
- advisory quality-gate reminder at session start
- blocking shell-command guardrails for repo-canonical prohibited git and
  history-bypass operations

## Canonical Assets

- `policy.json` — stable guardrail messages and blocked shell-command patterns
- `../../tools/agent_hooks.py` — shared runtime that normalises hook payloads
  and emits platform-native output

## Supported Native Activations

- Cursor: `.cursor/hooks.json`
  - `sessionStart`
  - `preToolUse` scoped to `Shell`
- Claude: `.claude/settings.json`
  - `SessionStart`
  - `PreToolUse` scoped to `Bash`
- Gemini: `.gemini/settings.json`
  - `SessionStart`
  - `BeforeTool` scoped to `run_shell_command`
- GitHub: `.github/hooks/guardrails.json`
  - `preToolUse` only
  - no grounding hook in v1 because GitHub session and prompt hook output is
    ignored
- Codex: unsupported until official OpenAI Codex docs expose a native repo
  hook surface

## Boundaries

- No auto-running `uv run python -m oaknational.python_repo_template.devtools check`
- No retry loops or prompt rewriting
- No platform-local hook scripts with substantive logic
- No support claim for Codex based on non-canonical third-party material
