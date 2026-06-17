---
date: 2026-06-17
type: synthesis-report
status: stable
---

# Oak Quality-Gate Types Review

A cross-ecosystem survey of the quality-gate *types* used across Oak repos, run
to decide which gates this template should model. One deep review of
`oak-open-curriculum-ecosystem` plus three parallel surveys covering roughly a
dozen repos (Oak-Web-Application, oak-components, studio, oak-ai-lesson-assistant,
oak-ai-moderation-service, oak-openapi, oak-curriculum-ontology,
agent-governance-toolkit, oak-skills, Cloud-Config, exploring-external-curricula-models).

This report is the rationale behind the
[quality-gate-surface-expansion plan](../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md).

## Headline finding

This template is already **ahead of most Oak repos** on gate rigour. Its
`check-ci` runs format, typecheck (actually run — many Oak repos configure but
skip it), lint, import-boundary, dependency-hygiene, a wheel build + installed-CLI
smoke probe (rare), tests, and coverage — plus commitizen and a sophisticated
`repo_audit.py` governance validator. That auditor is the same genre as Oak's
highest-signal bespoke validators (oak-skills `validate_skills.py`,
agent-governance-toolkit policy CLIs). The template is the *exemplar* for Tier-2
governance, not a laggard.

## Gate types observed, mapped to this template

| Category | Gate type | Oak tooling | This template |
| --- | --- | --- | --- |
| Static | lint, format, typecheck | ESLint/Prettier/tsc | have (ruff + pyright, run) |
| Boundaries | import/circular-dep | dependency-cruiser/Madge | have (import-linter) |
| Tests | unit/integration + coverage | Jest/Vitest/pytest | have (pytest + cov) |
| Packaging | build + install smoke | rare | have (wheel smoke probe) |
| Governance | repo/frontmatter/parity validators | validate_skills.py, policy CLIs | have (repo_audit, strong) |
| Commits | conventional-commit lint | commitlint | have (commitizen) |
| Docs | markdown lint | markdownlint(-cli2) | DONE this session (PyMarkdown) |
| Docs | spell check | cspell (+en-GB) | gap, queued (codespell) |
| Docs | link check | lychee (offline) | gap (not selected) |
| Security | secret scanning | gitleaks | gap, queued (gitleaks) |
| Supply-chain | dependency vuln scan | pip-audit/safety/dep-review | gap, queued (pip-audit) |
| Supply-chain | Dependabot + SHA-pinned actions | committed dependabot.yml, pinned SHAs | gap, queued |
| Release | SBOM, provenance, scorecard, semantic-release | cyclonedx, attestation, OpenSSF | deferred/optional |
| Skip (UI/infra) | visual-regression, a11y, Storybook, bundle-size, e2e, Terraform | Percy/Chromatic/pa11y/tflint | not transferable to a lib/CLI |

## Cross-cutting practices worth copying

- A single aggregate command (`check`/`check-ci`) that hooks and CI both call —
  parity by construction. This template already does this.
- Pre-commit hooks mirroring CI; a local script reproducing CI exactly.
- Zero-warning gates (`--max-warnings 0`).
- A commented ignore file that treats "what gets linted" as a governance
  decision (the ecosystem `.markdownlintignore` doctrine).
- Determinism discipline for generated artefacts (sorted, hashed, no timestamps)
  so a regenerate-and-fail-on-diff gate is meaningful.

## Recommendations (proportionate set)

Selected for implementation (each its own PR): **gitleaks** (secret scanning),
**pip-audit** (dependency vuln scan — fills the explicit hygiene-not-vuln gap),
**codespell** (en-GB, fits the British-spelling rule), and **supply-chain config**
(committed `dependabot.yml` + SHA-pinned action versions, optionally a
`repo_audit` self-check that workflows are pinned).

Notable efficiency: **bandit** (Python SAST) need not be a separate gate — ruff's
`S` (flake8-bandit) ruleset covers most of it.

Explicitly out of scope for a library/CLI template: visual regression,
accessibility-of-UI, Storybook, bundle-size, e2e, Terraform/IaC gates, LLM eval
gates, container image scanning.
