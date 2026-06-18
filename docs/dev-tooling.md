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
- markdown linting: `pymarkdown`
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
- `uv run python -m oaknational.python_repo_template.devtools markdownlint`
- `uv run python -m oaknational.python_repo_template.devtools markdownlint-fix`
- `uv run python -m oaknational.python_repo_template.devtools typecheck`
- `uv run python -m oaknational.python_repo_template.devtools repo-audit`
- `uv run python -m oaknational.python_repo_template.devtools test`
- `uv run python -m oaknational.python_repo_template.devtools coverage`
- `uv run python -m oaknational.python_repo_template.devtools fix`
- `uv run python -m oaknational.python_repo_template.devtools check`
- `uv run python -m oaknational.python_repo_template.devtools check-ci`

## Dependency hygiene

- direct command: `uv run deptry .`
- `deptry` proves declared dependency hygiene (unused, missing, or misplaced
  dependencies) — which is distinct from vulnerability scanning (see below)
- `uv run python -m oaknational.python_repo_template.devtools check` and
  `uv run python -m oaknational.python_repo_template.devtools check-ci` both
  run dependency hygiene before the tracked-repo audit
- `pyarrow` remains a deliberate `deptry` `DEP002` exception because pandas
  exercises it indirectly through the bounded Parquet path

## Dependency vulnerability scanning

- `pip-audit` scans the project's locked dependencies for known advisories; it is
  a blocking step in `check` and `check-ci` (right after dependency hygiene)
- direct command (the pipe equivalent of the gate):
  `uv export --no-emit-project --no-hashes --format requirements-txt | uv run pip-audit -r -`
  (the gate itself writes the export to a temporary file and passes
  `--requirement <file>`, which is equivalent)
- the gate exports the locked set with `--no-emit-project` (so the project itself
  is not audited against PyPI) and audits that, so it scans exactly what is pinned
  in `uv.lock`

## Markdown linting

- direct commands:
  `uv run python -m oaknational.python_repo_template.devtools markdownlint`
  (check) and
  `uv run python -m oaknational.python_repo_template.devtools markdownlint-fix`
  (autofix)
- `pymarkdown` scans the tracked Markdown estate, respecting `.gitignore`
- rules are configured in `[tool.pymarkdown]` in `pyproject.toml`; YAML front
  matter is recognised, `MD013`, `MD041`, and `MD029` are disabled and `MD024`
  is relaxed to siblings-only, so structural rules such as `MD040` stay on
- `check` and `check-ci` both run the markdown lint after the Ruff lint

## Spell checking

- `codespell` spell-checks the tracked text estate; it is a blocking step in
  `check` and `check-ci` (right after the Markdown lint)
- direct command: `uv run codespell .`
- British spellings pass codespell's default dictionary, so no en-GB conversion
  fires; configuration lives in `[tool.codespell]` in `pyproject.toml`
- `skip` excludes lock files, caches, and binary artefacts; add repo jargon to
  `ignore-words-list` only when codespell genuinely flags a real non-word

## Secret scanning

- `gitleaks` performs secret scanning: it looks for committed credentials,
  tokens, and keys
- it runs *alongside* `check-ci`, not inside it: `gitleaks` is a Go binary, not
  a `uv` package, so the venv cannot carry it and `uv sync` stays sufficient for
  the gate sequence
- locally it runs as a pinned pre-commit hook (the official
  `github.com/gitleaks/gitleaks` mirror); `uv run pre-commit install` wires it in
  and pre-commit installs the binary for you via its Go support — no manual step
- in CI a dedicated `secret-scan` job installs the same pinned binary (with a
  verified checksum) and runs `gitleaks dir .`
- the allowlist lives in `.gitleaks.toml`, which extends the upstream default
  rule set (`useDefault = true`); every exemption must justify itself in a
  comment, mirroring the commented-ignore-file doctrine used for Markdown linting
- the version is pinned once in `tools/repo_audit_contract.toml` and kept in
  lockstep across the pre-commit mirror and CI by the `secret-scanning`
  `repo-audit` check; bump all three together
- scope boundary: CI scans the checked-out working tree (`gitleaks dir .`) and
  the pre-commit hook scans staged changes — neither walks the full git history,
  so a secret committed and later removed in an earlier commit is not caught.
  History scanning (`gitleaks git` with a full-depth checkout) is a deliberate
  later enhancement, not part of this gate

## Supply-chain pinning

- every GitHub Actions `uses:` in the workflows is pinned to a full commit SHA
  (with a trailing `# vX` comment for readability), so a retagged or compromised
  upstream release cannot silently change what CI runs
- `.github/dependabot.yml` schedules weekly grouped update PRs for the two pinned
  ecosystems — `uv` (the locked Python dependencies) and `github-actions` (the
  pinned SHAs, which Dependabot bumps together with their `# vX` comment)
- the `supply-chain` `repo-audit` check enforces both: it fails if any workflow
  `uses:` is a tag or branch rather than a 40-hex SHA, or if Dependabot stops
  watching either ecosystem, so the pins cannot quietly drift back to tags

## Packaging proof

- `uv run python -m oaknational.python_repo_template.devtools build` builds the
  repo artefacts and then smoke-tests the newest built wheel from a temporary
  virtual environment outside the source tree
- `uv run python -m oaknational.python_repo_template.devtools check` and
  `uv run python -m oaknational.python_repo_template.devtools check-ci` keep
  the same proof in their build step
- the smoke path proves the installed package import plus both entry surfaces:
  `activity-report` and `python -m oaknational.python_repo_template`

## Coverage reporting

- the `coverage` gate runs `pytest` under `coverage.py`; locally it prints the
  `term-missing` report and fails under the threshold in `[tool.coverage.report]`
  (`fail_under = 85`, an honest floor below the ~88% the suite achieves)
- the `coverage-contract` `repo-audit` check guards what the coverage gate
  itself cannot: it fails if `fail_under` drops below 85, or if
  `[tool.coverage.run].omit` excludes any file beyond the justified set
  (`devtools.py`) — so the threshold cannot be quietly lowered and code cannot be
  hidden from the coverage denominator. Raising `fail_under` is always allowed
- CI additionally derives a Cobertura report from the same run with the
  `coverage xml` subcommand — the `coverage` gate's `pytest --cov` run writes the
  `.coverage` data file, and `coverage xml` reads it (no second test run) — then
  uploads it to GitHub Code Quality via `actions/upload-code-coverage`, so
  coverage shows on pull requests
- `coverage.xml` and the `.coverage*` data files are git-ignored, and
  `devtools clean` removes them
- GitHub Code Quality is a preview that must be enabled for the organisation; the
  upload runs with `fail-on-error: false` so it never turns the gate run red
  before then

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

## Releases

- automated by `.github/workflows/release.yml` using the **release-PR pattern**,
  so the committed `pyproject.toml` version advances under the protected `main`
  ruleset with no direct push and no bypass token
- the bump policy is `feat`/`fix` → minor, everything else → patch, and breaking
  markers are **not** auto-mapped to major; it lives in `[tool.commitizen].bump_map`
  but, because `cz_conventional_commits` ignores that map, `tools/release_increment.py`
  reads it and computes the increment, which the workflow applies via
  `cz bump --increment`
- on a push to `main` the workflow either *prepares* (opens/refreshes a
  `chore(release)` PR that bumps `pyproject.toml`, `uv.lock`, and `CHANGELOG.md`)
  or *publishes* (when the committed version has no tag yet — i.e. a release PR
  just merged — it tags `vX.Y.Z`, runs `uv build`, and creates the GitHub Release
  with the wheel + sdist attached)
- **major releases are manual**: a `!`/`BREAKING CHANGE` marker makes the
  auto-release stand down; cut the major via the workflow's `workflow_dispatch`
  (`increment = MAJOR`)
- the version stays committed in the tree; releases publish to GitHub Releases
  only (no PyPI). `audit_release_workflow` keeps the workflow and the bump policy
  honest

## Hydration guidance

When hydrating or extending another Python repo with this Practice:

1. keep the canonical repo-local `uv run python -m ...` gate surface truthful
2. use Python-native separators such as dashes rather than colon aliases
3. preserve stronger existing local contracts where they already meet or exceed
   this stack
4. update docs, hooks, and audits in the same landing as command-surface
   changes
