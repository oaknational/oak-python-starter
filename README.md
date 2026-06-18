# Oak Python Repo Template

[![CI](https://github.com/oaknational/oak-python-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/oaknational/oak-python-starter/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/oaknational/oak-python-starter?label=release)](https://github.com/oaknational/oak-python-starter/releases/latest)

`oaknational-python-repo-template` is a reusable Oak Python starter with:

- a canonical `src/` package layout
- strict quality gates driven by `uv`
- cross-platform agent infrastructure in `.agent/`, `.cursor/`, `.claude/`,
  `.gemini/`, `.github/`, `.agents/`, and `.codex/`
- a small demo CLI, `activity-report`, that exercises validation, file I/O,
  reporting, plotting, YAML sidecars, bounded HTTPS retrieval, and repo audits

Install the distribution as `oaknational-python-repo-template` and import it as
`oaknational.python_repo_template`. That is the baseline convention this repo
uses to define "Pythonic within Oak".

Adopting this template for a new project? See
[docs/using-this-template.md](docs/using-this-template.md) for the ordered rename
steps — `repo-audit` pins the template identity, so it doubles as a checklist
that flags any surface you miss.

The package ships `py.typed`, and the repo type-checks `src/`, `tests/`, and
`tools/` under explicit strict `pyright` settings.

The canonical repo-local build and `check-ci` flow also smoke-tests the built
wheel in a temporary virtual environment outside the source tree, running the
installed package import plus the `activity-report` and
`python -m oaknational.python_repo_template` entry surfaces.

Dependency hygiene runs through `uv run deptry .` and is included as a blocking
step inside both aggregate gate commands — it proves declared-dependency hygiene
(unused, missing, misplaced), which is distinct from vulnerability scanning.
Vulnerability scanning is a separate blocking gate: `pip-audit` checks the locked
dependencies for known advisories.

Secret scanning uses `gitleaks`. Because `gitleaks` is a Go binary rather than a
`uv` package, it runs alongside `check-ci` rather than inside it (so `uv sync`
stays sufficient for the gate sequence): a pinned pre-commit hook locally and a
pinned `secret-scan` job in CI, kept in lockstep by the `repo-audit`
`secret-scanning` check. The allowlist lives in `.gitleaks.toml`.

## Quality gates & CI/CD

This repo is a working reference for a strict Python quality bar and CI/CD;
everything below runs identically locally and in CI. The full detail is in
[docs/dev-tooling.md](docs/dev-tooling.md).

**Quality gates** — one `check-ci` sequence, run the same way locally and in CI:

| Gate | Tool | Proves |
| --- | --- | --- |
| format | `ruff format` | consistent formatting |
| typecheck | `pyright` (strict) | types across `src`/`tests`/`tools` |
| lint | `ruff` | lint rules |
| markdownlint | `pymarkdown` | Markdown hygiene |
| codespell | `codespell` | spelling |
| import-linter | `import-linter` | import-direction boundaries |
| dependency-hygiene | `deptry` | no unused/missing/misplaced deps |
| pip-audit | `pip-audit` | no known vulnerabilities in the locked deps |
| repo-audit | `tools/repo_audit.py` | repo identity, and that the gates' own config cannot be weakened |
| build | `uv build` + wheel smoke | the built wheel installs and both entry points run |
| test | `pytest` (+ Hypothesis) | behaviour, including property-based tests |
| coverage | `coverage.py` (branch) | coverage stays at or above the honest floor |

Three more gates run outside `check-ci`: **gitleaks** (secret scanning),
**SonarCloud** (pull-request analysis), and **CodeQL** (code quality).

**CI/CD**:

- **CI** runs the same `check-ci` on every push and pull request.
- **Continuous release on merge**: every qualifying merge to `main` advances the
  version (semantic-release via the Oak Semantic Release Bot) and publishes a
  GitHub Release with the wheel + sdist. See [Releases](#releases).
- **Supply-chain pinning**: every Actions `uses:` is pinned to a commit SHA, with
  Dependabot keeping the pins and the locked deps current.
- **Branch + tag rulesets**: PR required, required status checks, no force-push,
  and `v*` tags protected.
- **Self-guarding**: `repo_audit.py` audits the gates' own configuration (the
  coverage floor + branch mode, the supply-chain pins, the release workflow's
  shape), so the gates cannot be quietly weakened.

## Agentic Engineering

This repo is optimised for agentic engineering. Its Practice surfaces,
guardrails, and quality gates are designed so agents can plan, execute, review,
and close out work predictably and safely.

That does not make it agent-only. The same structure works well for
conventional human-led development, pair programming, and mixed human-agent
workflows.

The rules are intentionally strict because that strictness is part of the
safety model for agentic engineering. They are not convenience defaults and
should not be relaxed simply to make unsafe workflows easier.

## Demo CLI

The seeded example works with a simple activity log contract:

- `date` — ISO date (`YYYY-MM-DD`)
- `category` — non-empty label
- `minutes` — positive integer
- `notes` — optional text

The richer activity-pack demo also supports an optional same-stem YAML sidecar,
for example `activity_log.metadata.yaml`, for descriptive metadata, category
display labels, and simple per-category target minutes.

Prepare validated Parquet output:

```bash
uv run activity-report prepare \
  --input data/fixtures/activity_log.csv \
  --output data/fixtures/activity_log.parquet
```

Print a report:

```bash
uv run activity-report report --input data/fixtures/activity_log.csv
```

Override the auto-discovered metadata sidecar:

```bash
uv run activity-report report \
  --input data/fixtures/activity_log.csv \
  --metadata data/fixtures/activity_log.metadata.yaml
```

Run the same report via the package module entry point:

```bash
uv run python -m oaknational.python_repo_template report --input data/fixtures/activity_log.csv
```

Print a report and render a chart:

```bash
uv run activity-report report \
  --input data/fixtures/activity_log.parquet \
  --chart activity-summary.png
```

The chart is built to WCAG 2.2 AA: every bar clears a 3:1 non-text contrast
ratio and the target marker carries a contrasting halo (SC 1.4.11), and a text
alternative is written beside the image — `activity-summary.png.txt` — so a
non-visual reader gets the same per-category minutes, shares, and target deltas
(SC 1.1.1).

Report directly from a bounded HTTPS input:

```bash
uv run activity-report report --input https://example.test/activity_log.csv
```

## Prerequisites

Most tooling is managed through `uv`, so the usual setup is `uv sync` followed by
`uv run pre-commit install`. Two tools are binaries rather than Python packages,
so `uv sync` does not install them:

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — the
  toolchain every command below runs through; install it first.
- **[gitleaks](https://github.com/gitleaks/gitleaks#installing-gitleaks)** — the
  secret scanner. The pre-commit hook installs it automatically (pre-commit
  provisions its own Go toolchain), so no manual step is normally needed. Install
  it directly via the official instructions only if you want to run `gitleaks`
  outside pre-commit, or if the automatic install is unavailable in your
  environment.

## Development Commands

```bash
uv sync
uv run python -m oaknational.python_repo_template.devtools clean
uv run python -m oaknational.python_repo_template.devtools build
uv run python -m oaknational.python_repo_template.devtools dev
uv run deptry .
uv run python -m oaknational.python_repo_template.devtools check
uv run python -m oaknational.python_repo_template.devtools check-ci
uv run python -m oaknational.python_repo_template.devtools fix
uv run python -m oaknational.python_repo_template.devtools test
uv run python -m oaknational.python_repo_template.devtools coverage
```

Those developer commands are source-checkout workflows. The installed wheel
publishes only `activity-report` and `python -m oaknational.python_repo_template`.

## Commit Workflow

Install the repo hooks after cloning:

```bash
uv run pre-commit install
```

That installs the repo's `pre-commit`, `pre-push`, and `commit-msg` hooks from
`.pre-commit-config.yaml`.

Create a conventional commit with Commitizen:

```bash
uv run cz commit
```

Check a commit message manually:

```bash
uv run cz check --message "feat: add truthful commit-msg enforcement"
```

## Releases

Releases are **continuous**, and originate **only** from a merge to `main`. After
CI passes on `main`, the Release workflow computes the Conventional Commits
increment, and the **Oak Semantic Release Bot** (a `main`-ruleset bypass actor)
bumps `pyproject.toml`, `uv.lock`, and `CHANGELOG.md`, commits + tags `vX.Y.Z`,
pushes straight to `main`, and publishes a GitHub Release with the built wheel +
sdist attached. The bump commit carries `[skip ci]` so it does not loop. There is
no manual release trigger.

The bump level is computed by Commitizen with this repo's policy:

| Commit type(s) | Bump |
| --- | --- |
| `feat`, `fix` | minor |
| everything else (`chore`, `docs`, `perf`, `refactor`, `build`, `ci`, …) | patch |
| `!` / `BREAKING CHANGE` | no auto-release |

**Major versions are not automated.** A breaking marker makes the auto-release
stand down, and the `prevent-accidental-major` commit-msg hook rejects `type!:` /
`BREAKING CHANGE` in commits so one cannot land by accident. On the rare occasion
a major is warranted, a human engineer cuts it strategically, outside this repo's
automation. Releases publish to GitHub Releases only, not PyPI — if a project
based on this template needs PyPI, see
[docs/publishing-to-pypi.md](docs/publishing-to-pypi.md).

The workflow needs the `RELEASE_APP_CLIENT_ID` / `RELEASE_APP_PRIVATE_KEY`
secrets and the bot added as a ruleset bypass actor — see
[docs/repository-governance.md](docs/repository-governance.md).

## Governance

Most of the quality bar is enforced in code (the `check-ci` gates, the
`repo_audit.py` self-checks, and the SonarCloud PR gate). A few protections live
only in GitHub settings — required status checks, a release-PR token, the Code
Quality preview, and tag protection. Those owner actions are listed in
[docs/repository-governance.md](docs/repository-governance.md); an adopter should
work through them once per repository.

## Practice Surface

- Agent entry point: `.agent/directives/AGENT.md`
- Practice index: `.agent/practice-index.md`
- Capability roadmap: `.agent/plans/roadmap.md`

## Repo Shape

- `src/oaknational/python_repo_template/` — the canonical Oak namespace package root
- `src/oaknational/python_repo_template/data/` — validation and storage boundaries
- `src/oaknational/python_repo_template/demo/` — the example CLI surface
- `tests/` — behaviour-first tests
- `tools/repo_audit.py` — tracked-file audit for repo identity and adapter
  integrity

## Licence

Released under the [MIT licence](LICENCE), copyright Oak National Academy.

See [SECURITY.md](SECURITY.md) for vulnerability reporting and the credentials
policy.
