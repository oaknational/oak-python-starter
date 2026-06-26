## Description

- List of changes

## Issue(s)

Fixes #

## How to test

1. `uv run python -m oaknational.python_repo_template.devtools check-ci` — all gates pass
2. `uv run pre-commit run --all-files` — hooks clean

## Checklist

- [ ] `check-ci` passes locally
- [ ] Tests added or updated where appropriate
- [ ] No coverage floor regression
- [ ] Conventional commit messages (`uv run cz check --message "..."` to verify)
