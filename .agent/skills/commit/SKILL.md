---
name: commit
classification: passive
description: >-
  Create a deliberate commit using the repo's canonical commit workflow and
  quality gates.
---

# Commit

Use this skill when preparing a commit.

## Read first

1. `.agent/commands/commit.md`
2. `.agent/directives/principles.md`
3. `.agent/rules/no-verify-requires-fresh-authorisation.md`

## Checklist

1. Check `git status`.
2. Review `git diff --staged` and any related unstaged changes.
3. Ensure the relevant gates are green.
4. Stage only the files the commit message truthfully describes.
5. Use conventional commit format.
6. Commit without bypassing hooks.

## Local constraints

- This repo does not use aliases or compatibility layers for gate names.
- Prefer the canonical `uv run ...` surfaces when you need to re-run checks.
- If the change updates durable doctrine, include those docs in the same
  commit.
