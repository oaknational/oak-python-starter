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
- dependency hygiene: `deptry`
- commit workflow: `commitizen`
- tests: `pytest`
- repo-state audit: `uv run python -m oaknational.python_repo_template.devtools repo-audit`

## Typing contract

- the distribution ships `py.typed`
- `pyright` runs in explicit strict mode
- the checked repo-owned surface is `src/`, `tests/`, and `tools/`

## Canonical command surface

- `uv run python -m oaknational.python_repo_template.devtools clean`
- `uv run python -m oaknational.python_repo_template.devtools build`
- `uv run python -m oaknational.python_repo_template.devtools dev`
- `uv run python -m oaknational.python_repo_template.devtools format`
- `uv run python -m oaknational.python_repo_template.devtools format-fix`
- `uv run python -m oaknational.python_repo_template.devtools lint`
- `uv run python -m oaknational.python_repo_template.devtools lint-fix`
- `uv run python -m oaknational.python_repo_template.devtools typecheck`
- `uv run python -m oaknational.python_repo_template.devtools repo-audit`
- `uv run python -m oaknational.python_repo_template.devtools test`
- `uv run python -m oaknational.python_repo_template.devtools coverage`
- `uv run python -m oaknational.python_repo_template.devtools fix`
- `uv run python -m oaknational.python_repo_template.devtools check`
- `uv run python -m oaknational.python_repo_template.devtools check-ci`

## Dependency hygiene

- direct command: `uv run deptry .`
- `deptry` proves declared dependency hygiene, not vulnerability scanning
- `uv run python -m oaknational.python_repo_template.devtools check` and
  `uv run python -m oaknational.python_repo_template.devtools check-ci` both
  run dependency hygiene before the tracked-repo audit
- `pyarrow` remains a deliberate `deptry` `DEP002` exception because pandas
  exercises it indirectly through the bounded Parquet path

## Packaging proof

- `uv run python -m oaknational.python_repo_template.devtools build` builds the
  repo artefacts and then smoke-tests the newest built wheel from a temporary
  virtual environment outside the source tree
- `uv run python -m oaknational.python_repo_template.devtools check` and
  `uv run python -m oaknational.python_repo_template.devtools check-ci` keep
  the same proof in their build step
- the smoke path proves the installed package import plus both entry surfaces:
  `activity-report` and `python -m oaknational.python_repo_template`

## Commit workflow

Install the repo hooks with:

```bash
uv run pre-commit install
```

The repo config installs `pre-commit`, `pre-push`, and `commit-msg` by
default, so Commitizen validation runs on real commit messages rather than as a
separate advisory command.

Create a conventional commit with:

```bash
uv run cz commit
```

Validate a message manually with:

```bash
uv run cz check --message "docs: explain the Commitizen workflow"
```

## Hydration guidance

When hydrating or extending another Python repo with this Practice:

1. keep the canonical repo-local `uv run python -m ...` gate surface truthful
2. use Python-native separators such as dashes rather than colon aliases
3. preserve stronger existing local contracts where they already meet or exceed
   this stack
4. update docs, hooks, and audits in the same landing as command-surface
   changes
