# Dev Tooling

This repo is the current Python leading-edge reference inside this Practice
network.

Its package identity follows the Oak Python convention:

- distribution name: `oaknational-python-repo-template`
- import path: `oaknational.python_repo_template`

## Current stack

- package manager and task runner: `uv`
- Python version management: `.python-version`
- formatter and linter: `ruff`
- type checking: `pyright`
- tests: `pytest`
- repo-state audit: `uv run repo-audit`

## Canonical command surface

- `uv run clean`
- `uv run build`
- `uv run dev`
- `uv run format`
- `uv run format-fix`
- `uv run lint`
- `uv run lint-fix`
- `uv run typecheck`
- `uv run repo-audit`
- `uv run test`
- `uv run coverage`
- `uv run fix`
- `uv run check`
- `uv run check-ci`

## Hydration guidance

When hydrating or extending another Python repo with this Practice:

1. keep the canonical `uv run ...` gate surface truthful
2. use Python-native separators such as dashes rather than colon aliases
3. preserve stronger existing local contracts where they already meet or exceed
   this stack
4. update docs, hooks, and audits in the same landing as command-surface
   changes
