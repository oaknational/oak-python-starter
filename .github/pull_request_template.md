## Description

- List of changes

## Issue(s)

<!-- Fixes #123 or delete if not applicable -->

## How to test

1. `uv run python -m <your_package>.devtools check-ci` — all gates pass
2. `uv run pre-commit run --all-files` — hooks clean

## Checklist

- [ ] `check-ci` passes locally
- [ ] Tests added or updated where appropriate
- [ ] No coverage floor regression
- [ ] Conventional commit messages (`uv run cz check --message "..."` to verify)
