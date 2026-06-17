# Commit Current Work

Create a deliberate, well-formed commit for the current changes.

## Process

1. Check status with `git status`.
2. Review the staged and unstaged diff.
3. Confirm the relevant quality gates have passed, or run them now.
4. Stage selectively. Never use `git add .` blindly.
5. Use `uv run cz commit` to write a conventional commit message focused on the
   rationale.
6. Commit without bypassing hooks.
7. Confirm the worktree is in the expected post-commit state.

## Commit message format

Commitizen uses Conventional Commits. If you need to validate a message before
committing, use `uv run cz check`.

```text
type(scope): concise summary

Optional body explaining why this change exists.
```

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`,
`perf`.

## Safety rules

- do not use `--no-verify`
- do not rewrite history unless the user explicitly asks
- do not discard unrelated changes
- fix hook failures at source instead of bypassing them

Use `.agent/skills/commit/SKILL.md` when you need the fuller commit ritual.
